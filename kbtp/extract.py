"""Parallel, VRAM-aware, resumable ThinkProbe feature extraction.

Per trace: segment(reasoning_text) -> build_graph -> compute_profile -> 22 features,
plus lexical baseline features and length. Non-generative (regex + MiniLM + DeBERTa-NLI).

Parallelism: one process per worker slot, each pinned to a GPU via CUDA_VISIBLE_DEVICES,
loading its own model singletons. Worker count is sized to *live* free VRAM (shared box).
Resumable: workers append uuid-named batch parquet files; done row_ids are skipped on rerun.
"""
from __future__ import annotations
import os
import subprocess
import uuid
import multiprocessing as mp
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from . import config as C
from .lexical import lexical_features, LEX_FEATURES

_INPUT_COLS = ["row_id", "reasoning_text", "model_id", "scenario_domain", "setup_id", "roll_idx"]


# ---------------- per-trace extraction (runs inside worker) ----------------
def _extract_one(segment, classify_nodes, build_graph, compute_profile, rec: dict) -> dict:
    text = rec["reasoning_text"] or ""
    out = {"row_id": rec["row_id"], "status": "ok", "error": ""}
    try:
        tus, edges, emb = segment(text, use_nli=True)
        classify_nodes(tus, edges, emb)  # assigns node_type/node_family (mutates tus)
        trace = {
            "trace_id": rec["row_id"], "model": rec["model_id"],
            "question_id": rec["setup_id"], "domain": rec["scenario_domain"],
            "run": int(rec["roll_idx"]), "raw_cot": text,
        }
        graph = build_graph(trace, tus, edges)
        prof = compute_profile(graph, model=rec["model_id"], domain=rec["scenario_domain"])
        d = prof.model_dump()
        for f in C.FEATURES:
            v = d.get(f)
            out[f] = float(v) if v is not None else float("nan")
        out["n_tus"] = float(len(tus))
        out["n_edges"] = float(len(edges))
    except Exception as e:  # noqa: BLE001 - record & continue (idempotent)
        out["status"] = "error"
        out["error"] = f"{type(e).__name__}: {e}"[:300]
        for f in C.FEATURES:
            out[f] = float("nan")
        out["n_tus"] = float("nan"); out["n_edges"] = float("nan")
    out.update(lexical_features(text))
    return out


def _worker(slot: int, gpu_id: int, records: list[dict], pop: str) -> None:
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    C.apply_hf_env()
    # import torch stack only after env is set
    from thinkbench.extract.segmenter import segment
    from thinkbench.extract.classifier import classify_nodes
    from thinkbench.extract.linker import build_graph
    from thinkbench.metrics.profile import compute_profile

    C.PART_DIR.mkdir(parents=True, exist_ok=True)
    buf: list[dict] = []

    def flush():
        if not buf:
            return
        fn = C.PART_DIR / f"{pop}__slot{slot}__{uuid.uuid4().hex}.parquet"
        pd.DataFrame(buf).to_parquet(fn, index=False)
        buf.clear()

    for i, rec in enumerate(records):
        buf.append(_extract_one(segment, classify_nodes, build_graph, compute_profile, rec))
        if len(buf) >= C.FLUSH_EVERY:
            flush()
            print(f"[extract slot{slot} gpu{gpu_id}] {i + 1}/{len(records)}", flush=True)
    flush()
    print(f"[extract slot{slot} gpu{gpu_id}] done {len(records)}", flush=True)


# ---------------- VRAM planning ----------------
def _free_vram_mb(gpu_id: int) -> int:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits",
             "-i", str(gpu_id)], text=True)
        return int(out.strip().splitlines()[0])
    except Exception:
        return 0


def plan_workers(gpu_ids: list[int]) -> list[int]:
    """Return a list of gpu_id assignments (one per worker slot), sized to free VRAM."""
    plan: list[int] = []
    for g in gpu_ids:
        free_gb = _free_vram_mb(g) / 1024.0
        n = min(C.MAX_WORKERS_PER_GPU, int(free_gb // C.PER_WORKER_GB))
        print(f"[extract] gpu{g}: {free_gb:.1f} GB free -> {n} worker(s)")
        plan += [g] * n
    if not plan:
        raise RuntimeError("No GPU has room for a worker at current free VRAM.")
    return plan


# ---------------- resume bookkeeping ----------------
def _done_ids(pop: str) -> set[str]:
    if not C.PART_DIR.exists():
        return set()
    done: set[str] = set()
    for f in C.PART_DIR.glob(f"{pop}__*.parquet"):
        try:
            done |= set(pq.read_table(f, columns=["row_id"]).column("row_id").to_pylist())
        except Exception:
            pass
    return done


def merge_parts(pop: str) -> Path:
    parts = sorted(C.PART_DIR.glob(f"{pop}__*.parquet"))
    if not parts:
        raise FileNotFoundError(f"No part files for pop={pop}")
    df = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    df = df.drop_duplicates(subset="row_id", keep="first")
    out = C.features_path(pop)
    df.to_parquet(out, index=False)
    return out


# ---------------- orchestrator ----------------
def run_extraction(pop: str, limit: int | None = None, gpu_ids: list[int] | None = None) -> dict:
    src = {"labelable": C.F_POP_LABELABLE, "refusal": C.F_POP_REFUSAL}[pop]
    df = pq.read_table(src, columns=_INPUT_COLS).to_pandas()
    done = _done_ids(pop)
    todo = df[~df["row_id"].isin(done)].reset_index(drop=True)
    if limit is not None:
        todo = todo.head(limit)
    print(f"[extract] pop={pop}: total={len(df)} done={len(done)} todo={len(todo)}")
    if len(todo) == 0:
        out = merge_parts(pop)
        return {"pop": pop, "extracted": 0, "output": str(out)}

    assignments = plan_workers(gpu_ids or C.EXTRACT_GPUS)
    nslots = len(assignments)
    records = todo.to_dict("records")
    chunks: list[list[dict]] = [records[i::nslots] for i in range(nslots)]  # round-robin

    ctx = mp.get_context("spawn")
    procs = []
    for slot, (gpu_id, chunk) in enumerate(zip(assignments, chunks)):
        if not chunk:
            continue
        p = ctx.Process(target=_worker, args=(slot, gpu_id, chunk, pop))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()

    out = merge_parts(pop)
    merged = pd.read_parquet(out)
    n_ok = int((merged["status"] == "ok").sum())
    print(f"[extract] pop={pop}: merged={len(merged)} ok={n_ok} err={len(merged)-n_ok} -> {out}")
    return {"pop": pop, "rows": len(merged), "ok": n_ok, "output": str(out)}


if __name__ == "__main__":
    import sys
    pop = sys.argv[1] if len(sys.argv) > 1 else "labelable"
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else None
    run_extraction(pop, limit=lim)
