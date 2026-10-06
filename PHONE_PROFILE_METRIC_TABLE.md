# Phone (socioeconomic proxy) — 5 profiles + all 22 metrics, KILLED vs NOT-KILLED

All values in **SD units** (z-scored across the 20,112 nationality traces; 0 = average trace).
`KILLED` = the chosen victim belongs to this group.
`NOT-KILLED` = at least one member was on offer, someone else was chosen.

**Exposure note:** a line-up can hold several members of one group, so the fair share is not
25% everywhere. `expected_%` is computed per trial as (members on offer)/4; `rel_risk` = observed/expected (1.00 = exactly fair).

Full data: `results/phone_profiles_metrics_kill_vs_notkill.csv`

## Exposure and kill share

| phone | members | n killed | n not-killed | observed % | expected % | rel. risk |
|---|---:|---:|---:|---:|---:|---:|
| No phone | 1 | 1677 | 645 | 72.2 | 25.0 | 2.889 |
| Nokia | 1 | 382 | 1940 | 16.5 | 25.0 | 0.658 |
| iPhone | 1 | 202 | 2120 | 8.7 | 25.0 | 0.348 |
| Android | 1 | 61 | 2261 | 2.6 | 25.0 | 0.105 |

> **Caution:** unadjusted means. Model identity alone explains up to ~90% of these
> metrics, and the controlled within-line-up test left 1 of 520 cells significant against a
> 0.075 SD detection floor. Read single rows as candidates, not findings.

---

## DIFFERENCE (killed − not killed)

### Breadth (family score + its metrics)

| phone | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.132 | -0.007 | +0.123 | +0.172 | +0.240 |
| Nokia | 382 | 1940 | -0.268 | -0.071 | -0.261 | -0.329 | -0.411 |
| iPhone | 202 | 2120 | -0.015 | +0.085 | +0.015 | -0.095 | -0.066 |
| Android | 61 | 2261 | +0.452 | +0.172 | +0.395 | +0.712 | +0.530 |

### Depth (family score + its metrics)

| phone | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.094 | +0.049 | +0.225 | -0.098 | +0.200 |
| Nokia | 382 | 1940 | -0.162 | -0.129 | -0.388 | +0.169 | -0.299 |
| iPhone | 202 | 2120 | -0.037 | +0.001 | -0.013 | -0.078 | -0.057 |
| Android | 61 | 2261 | +0.247 | +0.306 | +0.362 | +0.104 | +0.218 |

### Structure (family score + its metrics)

| phone | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | -0.025 | +0.026 | -0.048 | +0.004 | -0.144 | -0.058 | +0.070 |
| Nokia | 382 | 1940 | +0.040 | -0.054 | +0.058 | +0.057 | +0.231 | +0.108 | -0.160 |
| iPhone | 202 | 2120 | +0.028 | +0.003 | +0.030 | +0.003 | +0.107 | +0.045 | -0.020 |
| Android | 61 | 2261 | -0.109 | +0.072 | -0.035 | -0.349 | -0.447 | -0.268 | +0.372 |

### Metacognitive (family score + its metrics)

| phone | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.037 | +0.032 | +0.108 | -0.013 | +0.019 |
| Nokia | 382 | 1940 | -0.023 | -0.026 | -0.199 | +0.172 | -0.039 |
| iPhone | 202 | 2120 | -0.046 | -0.060 | +0.006 | -0.108 | -0.024 |
| Android | 61 | 2261 | -0.020 | +0.071 | +0.201 | -0.491 | +0.137 |

### Efficiency (family score + its metrics)

| phone | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| No phone | 1677 | 645 | -0.091 | -0.106 | -0.077 |
| Nokia | 382 | 1940 | +0.068 | +0.101 | +0.034 |
| iPhone | 202 | 2120 | +0.123 | +0.117 | +0.129 |
| Android | 61 | 2261 | -0.027 | -0.076 | +0.021 |

### Summary size pair

| phone | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| No phone | 1677 | 645 | -0.103 | +0.092 |
| Nokia | 382 | 1940 | +0.171 | -0.199 |
| iPhone | 202 | 2120 | +0.016 | -0.022 |
| Android | 61 | 2261 | -0.163 | +0.414 |

## KILLED

### Breadth (family score + its metrics)

| phone | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.037 | -0.002 | +0.034 | +0.048 | +0.067 |
| Nokia | 382 | 1940 | -0.224 | -0.059 | -0.218 | -0.275 | -0.343 |
| iPhone | 202 | 2120 | -0.014 | +0.077 | +0.013 | -0.086 | -0.060 |
| Android | 61 | 2261 | +0.440 | +0.168 | +0.385 | +0.694 | +0.516 |

### Depth (family score + its metrics)

| phone | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.026 | +0.014 | +0.062 | -0.027 | +0.056 |
| Nokia | 382 | 1940 | -0.135 | -0.108 | -0.324 | +0.141 | -0.250 |
| iPhone | 202 | 2120 | -0.034 | +0.000 | -0.011 | -0.072 | -0.052 |
| Android | 61 | 2261 | +0.241 | +0.298 | +0.352 | +0.101 | +0.212 |

### Structure (family score + its metrics)

| phone | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | -0.007 | +0.007 | -0.013 | +0.001 | -0.040 | -0.016 | +0.019 |
| Nokia | 382 | 1940 | +0.034 | -0.045 | +0.049 | +0.048 | +0.193 | +0.090 | -0.133 |
| iPhone | 202 | 2120 | +0.026 | +0.003 | +0.028 | +0.003 | +0.098 | +0.041 | -0.018 |
| Android | 61 | 2261 | -0.106 | +0.070 | -0.034 | -0.340 | -0.435 | -0.261 | +0.362 |

### Metacognitive (family score + its metrics)

| phone | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.010 | +0.009 | +0.030 | -0.004 | +0.005 |
| Nokia | 382 | 1940 | -0.019 | -0.022 | -0.166 | +0.144 | -0.033 |
| iPhone | 202 | 2120 | -0.042 | -0.055 | +0.006 | -0.098 | -0.022 |
| Android | 61 | 2261 | -0.020 | +0.070 | +0.195 | -0.478 | +0.134 |

### Efficiency (family score + its metrics)

| phone | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| No phone | 1677 | 645 | -0.025 | -0.029 | -0.021 |
| Nokia | 382 | 1940 | +0.056 | +0.084 | +0.028 |
| iPhone | 202 | 2120 | +0.112 | +0.107 | +0.118 |
| Android | 61 | 2261 | -0.027 | -0.074 | +0.020 |

### Summary size pair

| phone | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| No phone | 1677 | 645 | -0.029 | +0.026 |
| Nokia | 382 | 1940 | +0.143 | -0.166 |
| iPhone | 202 | 2120 | +0.015 | -0.020 |
| Android | 61 | 2261 | -0.158 | +0.404 |

## NOT-KILLED

### Breadth (family score + its metrics)

| phone | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | -0.095 | +0.005 | -0.089 | -0.124 | -0.173 |
| Nokia | 382 | 1940 | +0.044 | +0.012 | +0.043 | +0.054 | +0.068 |
| iPhone | 202 | 2120 | +0.001 | -0.007 | -0.001 | +0.008 | +0.006 |
| Android | 61 | 2261 | -0.012 | -0.005 | -0.010 | -0.019 | -0.014 |

### Depth (family score + its metrics)

| phone | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | -0.068 | -0.035 | -0.162 | +0.071 | -0.144 |
| Nokia | 382 | 1940 | +0.027 | +0.021 | +0.064 | -0.028 | +0.049 |
| iPhone | 202 | 2120 | +0.003 | -0.000 | +0.001 | +0.007 | +0.005 |
| Android | 61 | 2261 | -0.006 | -0.008 | -0.010 | -0.003 | -0.006 |

### Structure (family score + its metrics)

| phone | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.018 | -0.019 | +0.034 | -0.003 | +0.104 | +0.042 | -0.051 |
| Nokia | 382 | 1940 | -0.007 | +0.009 | -0.010 | -0.009 | -0.038 | -0.018 | +0.026 |
| iPhone | 202 | 2120 | -0.002 | -0.000 | -0.003 | -0.000 | -0.009 | -0.004 | +0.002 |
| Android | 61 | 2261 | +0.003 | -0.002 | +0.001 | +0.009 | +0.012 | +0.007 | -0.010 |

### Metacognitive (family score + its metrics)

| phone | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| No phone | 1677 | 645 | -0.027 | -0.023 | -0.078 | +0.009 | -0.014 |
| Nokia | 382 | 1940 | +0.004 | +0.004 | +0.033 | -0.028 | +0.006 |
| iPhone | 202 | 2120 | +0.004 | +0.005 | -0.001 | +0.009 | +0.002 |
| Android | 61 | 2261 | +0.001 | -0.002 | -0.005 | +0.013 | -0.004 |

### Efficiency (family score + its metrics)

| phone | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| No phone | 1677 | 645 | +0.066 | +0.076 | +0.056 |
| Nokia | 382 | 1940 | -0.011 | -0.017 | -0.006 |
| iPhone | 202 | 2120 | -0.011 | -0.010 | -0.011 |
| Android | 61 | 2261 | +0.001 | +0.002 | -0.001 |

### Summary size pair

| phone | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| No phone | 1677 | 645 | +0.074 | -0.067 |
| Nokia | 382 | 1940 | -0.028 | +0.033 |
| iPhone | 202 | 2120 | -0.001 | +0.002 |
| Android | 61 | 2261 | +0.004 | -0.011 |
