"""Stage 2 (GPU, ~1.5 h): ThinkProbe feature extraction over both populations.

Resumable — rerun to continue after interruption (done row_ids are skipped).
"""
from kbtp import extract

if __name__ == "__main__":
    print("== extracting labelable ==")
    extract.run_extraction("labelable")
    print("== extracting refusal ==")
    extract.run_extraction("refusal")
    print("== stage 2 done ==")
