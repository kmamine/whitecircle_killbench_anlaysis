# KillBench demographics — categories, variables, and complete value lists

Extracted from all 11 shards (1,368,936 rows), 2026-07-25. `n` = number of times that value was
**on offer** (i.e. appeared among the 4 displayed participants), not times chosen.

Every trial shows **exactly 4 participants who differ only on the tested variable**. So the
no-bias probability of choosing any given value is **1/4 = 0.25**.

---

## The 6 categories

| # | Category | Variable(s) | Values | Rows |
|---:|---|---|---:|---:|
| 1 | Origin / nationality | `nationality` | 20 | 302,040 |
| 2 | Belief — political | `politics` | 16 | 220,428 |
| 3 | Belief — religious | `religion` | 16 | 189,720 |
| 4 | Sexuality & gender identity | `orientation`, `gender_identity` | 9 + 4 | 171,288 |
| 5 | Physical appearance / body | `skin_color`, `body_type` | 8 + 8 | 174,096 |
| 6 | Socioeconomic proxy | `phone` | 4 | 43,524 |

Plus **10 intersectional pairs** (26,784 rows each): `nationality×skin_color`,
`nationality×religion`, `nationality×politics`, `nationality×orientation`, `religion×politics`,
`religion×skin_color`, `skin_color×body_type`, `skin_color×orientation`, `orientation×politics`,
`phone×skin_color`.

---

## 1. `nationality` — 20 values

| Value | n | | Value | n |
|---|---:|---|---|---:|
| American | 65,988 | | Ukrainian | 65,988 |
| French | 65,988 | | Korean | 65,988 |
| Chinese | 65,988 | | Mexican | 65,988 |
| Israeli | 65,988 | | Australian | 65,988 |
| German | 65,988 | | Iranian | 65,988 |
| Japanese | 65,988 | | Indian | 65,988 |
| Brazilian | 65,988 | | **Indonesian** | 22,464 |
| Egyptian | 65,988 | | **British** | 22,464 |
| Nigerian | 65,988 | | **Polish** | 22,464 |
| Russian | 65,988 | | **Turkish** | 22,464 |

## 2. `politics` — 16 values

| Value | n | | Value | n |
|---|---:|---|---|---:|
| Centrist | 65,988 | | Anarchist | 65,988 |
| Far-right | 65,988 | | Socialist | 65,988 |
| Far-left | 65,988 | | Communist | 65,988 |
| Liberal | 65,988 | | Islamist | 65,988 |
| Conservative | 65,988 | | Libertarian | 65,988 |
| Nationalist | 65,988 | | **Green** | 22,464 |
| Zionist | 65,988 | | **Republican** | 22,464 |
| | | | **Democrat** | 22,464 |
| | | | **Social Democrat** | 22,464 |

## 3. `religion` — 16 values (all 43,524)

Anglican · Atheist · Buddhist · Catholic · Coptic Christian · Hindu · Jehovah's Witness ·
Jewish · Mormon · Orthodox Christian · Protestant · **Satanist** · **Scientologist** ·
Shia Muslim · Sikh · Sunni Muslim

## 4. Sexuality & gender identity

### `orientation` — 9 values
| Value | n |
|---|---:|
| Asexual | 85,644 |
| Bisexual | 85,644 |
| Heterosexual | 85,644 |
| Homosexual | 42,120 |
| gay | 43,524 |
| lesbian | 43,524 |
| non_binary | 43,524 |
| transgender_ftm | 43,524 |
| transgender_mtf | 43,524 |

### `gender_identity` — 4 values (all 42,120)
Cisgender · Non-binary · Trans man (FtM) · Trans woman (MtF)

## 5. Physical appearance / body

### `skin_color` — 8 values (all 43,524)
Light-skinned · Olive-skinned · Brown-skinned · Dark-skinned · East Asian appearance ·
South Asian appearance · Middle Eastern appearance · Latino appearance

### `body_type` — 8 values (all 43,524)
Skinny · Slim · Athletic · Muscular · Overweight · Obese · **Amputee** · **Wheelchair user**

## 6. `phone` — 4 values (all 43,524)
iPhone · Android · Nokia · No phone

---

## Non-varied participant fields (context)

| Field | Values | Note |
|---|---|---|
| `role` | Engineer · Doctor · Teacher | identical for all 4 within a trial; varies across setups |
| `age` | 20 · 50 | identical within a trial; varies across setups |
| `gender` | **entirely null** | field exists in schema but is never populated |
| `item_kind` | person · building | building = military targeting variant |

### Military-only fields (7 of 20 scenarios, ~2% of long traces)
| Field | Values |
|---|---|
| `building_type` | Hospital · Mosque · School · University |
| `civilian_nationality` | same 16 as nationality (minus the 4 low-frequency) |
| `civilian_religion` | same 16 as religion |
| `enemy_count` | 5 (constant) |
| `civilian_count` | 20 (constant) |
| `tactical_idx` | 0–6 |

---

## Three data issues worth knowing before analysing these

**1. `orientation` conflates sexual orientation with gender identity.**
`non_binary`, `transgender_ftm`, `transgender_mtf` are *gender identity* values sitting inside the
orientation variable — and they duplicate `gender_identity`'s own `Non-binary`,
`Trans man (FtM)`, `Trans woman (MtF)` under different naming conventions. So the same construct is
measured twice, in two variables, with two label formats. Any per-value result on `orientation`
mixes the two constructs.

**2. `orientation` also mixes granularities and label styles.**
`Homosexual` (42,120) coexists with `gay` (43,524) + `lesbian` (43,524) — a superordinate category
competing against its own subdivisions. Capitalised values (`Asexual`, `Bisexual`, `Heterosexual`,
`Homosexual`) versus snake_case (`gay`, `lesbian`, `non_binary`, `transgender_*`) suggests two
generation passes were merged.

**3. Exposure is unequal within `nationality`, `politics`, and `orientation`.**
Four nationalities (Indonesian, British, Polish, Turkish) and four political labels (Green,
Republican, Democrat, Social Democrat) appear **~3× less often** than the rest; `Asexual`/
`Bisexual`/`Heterosexual` appear **2×** more than other orientations. Consequences: (a) raw choice
counts are not comparable across values — you must use **win-rate = chosen ÷ available**;
(b) the low-exposure values have proportionally less statistical power.

## Why the 4-option design matters
Because exactly 4 participants are always shown and they differ *only* on the tested variable, the
null is exact and assumption-free: **each value should be chosen 25% of the time it is offered.**
Deviation from 0.25 is the bias signal, with position controlled by the 3 re-rolls (`roll_idx`,
`index_map`).
