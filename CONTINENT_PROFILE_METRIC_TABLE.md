# Continent — 5 profiles + all 22 metrics, KILLED vs NOT-KILLED

All values in **SD units** (z-scored across the 20,112 nationality traces; 0 = average trace).
`KILLED` = the chosen victim belongs to this continent.
`NOT-KILLED` = at least one person from this continent was on offer, someone else was chosen.

**Exposure note:** a line-up can hold several members of one continent (up to 3 Asians), so the
fair-share expectation is *not* 25% for every continent — `expected_%` below is computed per trial
as (members on offer)/4. `rel_risk` = observed / expected; 1.00 = exactly fair.

Full data: `results/continent_profiles_metrics_kill_vs_notkill.csv`

## Exposure and kill share

| continent | nations | n killed | n not-killed | observed % | expected % | rel. risk |
|---|---:|---:|---:|---:|---:|---:|
| Oceania | 1 | 1156 | 3103 | 27.1 | 25.0 | 1.086 |
| Europe | 6 | 6011 | 14101 | 29.9 | 27.8 | 1.074 |
| Africa | 2 | 2240 | 6599 | 25.3 | 25.0 | 1.014 |
| Asia | 8 | 7657 | 10316 | 42.6 | 44.1 | 0.967 |
| South America | 1 | 991 | 3248 | 23.4 | 25.0 | 0.935 |
| North America | 2 | 2057 | 6999 | 22.7 | 25.0 | 0.909 |

> Caution: the profile numbers below are **unadjusted**. Model identity alone explains up to
> ~90% of these metrics, and the controlled within-line-up test left 1 of 520 cells significant
> against a 0.075 SD floor. Treat single rows as composition until confirmed.

---

## DIFFERENCE (killed − not killed)

### Breadth (family score + its metrics)

| continent | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | +0.004 | -0.006 | +0.017 | +0.002 | +0.004 |
| Europe | 6011 | 14101 | -0.004 | +0.048 | -0.027 | -0.015 | -0.021 |
| Africa | 2240 | 6599 | -0.051 | -0.052 | -0.040 | -0.039 | -0.072 |
| Asia | 7657 | 10316 | +0.010 | -0.001 | +0.011 | +0.007 | +0.020 |
| South America | 991 | 3248 | +0.080 | +0.068 | +0.124 | +0.045 | +0.081 |
| North America | 2057 | 6999 | +0.027 | +0.019 | +0.049 | +0.017 | +0.024 |

### Depth (family score + its metrics)

| continent | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | +0.009 | +0.056 | +0.042 | -0.007 | -0.054 |
| Europe | 6011 | 14101 | -0.034 | -0.067 | -0.046 | +0.000 | -0.024 |
| Africa | 2240 | 6599 | -0.028 | -0.027 | -0.035 | -0.049 | -0.003 |
| Asia | 7657 | 10316 | +0.027 | +0.025 | +0.023 | +0.038 | +0.020 |
| South America | 991 | 3248 | +0.062 | +0.111 | +0.073 | -0.024 | +0.089 |
| North America | 2057 | 6999 | +0.010 | +0.010 | +0.016 | +0.012 | +0.003 |

### Structure (family score + its metrics)

| continent | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.005 | -0.044 | -0.010 | -0.037 | +0.058 | -0.057 | +0.056 |
| Europe | 6011 | 14101 | +0.005 | +0.044 | -0.003 | +0.010 | +0.002 | +0.051 | -0.072 |
| Africa | 2240 | 6599 | -0.005 | -0.031 | +0.044 | +0.021 | -0.050 | +0.035 | -0.049 |
| Asia | 7657 | 10316 | +0.004 | -0.002 | -0.025 | +0.001 | +0.041 | -0.019 | +0.026 |
| South America | 991 | 3248 | -0.003 | +0.050 | -0.050 | -0.058 | -0.011 | -0.056 | +0.110 |
| North America | 2057 | 6999 | +0.002 | +0.025 | +0.009 | -0.040 | -0.020 | +0.006 | +0.029 |

### Metacognitive (family score + its metrics)

| continent | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | +0.003 | +0.026 | +0.030 | -0.011 | -0.033 |
| Europe | 6011 | 14101 | -0.007 | -0.025 | -0.030 | +0.007 | +0.018 |
| Africa | 2240 | 6599 | +0.023 | +0.015 | -0.030 | +0.109 | -0.001 |
| Asia | 7657 | 10316 | +0.007 | +0.033 | +0.015 | -0.014 | -0.004 |
| South America | 991 | 3248 | -0.024 | -0.068 | +0.062 | -0.156 | +0.067 |
| North America | 2057 | 6999 | -0.013 | -0.015 | +0.002 | -0.068 | +0.029 |

### Efficiency (family score + its metrics)

| continent | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | +0.038 | +0.051 | +0.024 |
| Europe | 6011 | 14101 | -0.039 | -0.044 | -0.035 |
| Africa | 2240 | 6599 | +0.007 | +0.030 | -0.017 |
| Asia | 7657 | 10316 | +0.037 | +0.024 | +0.051 |
| South America | 991 | 3248 | -0.030 | -0.058 | -0.002 |
| North America | 2057 | 6999 | -0.017 | -0.008 | -0.027 |

### Summary size pair

| continent | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Oceania | 1156 | 3103 | +0.090 | +0.053 |
| Europe | 6011 | 14101 | -0.053 | -0.060 |
| Africa | 2240 | 6599 | +0.017 | -0.057 |
| Asia | 7657 | 10316 | +0.042 | +0.041 |
| South America | 991 | 3248 | -0.066 | +0.078 |
| North America | 2057 | 6999 | -0.049 | +0.010 |

## KILLED

### Breadth (family score + its metrics)

| continent | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.022 | -0.124 | -0.031 | +0.043 | +0.023 |
| Europe | 6011 | 14101 | -0.003 | +0.033 | -0.019 | -0.010 | -0.015 |
| Africa | 2240 | 6599 | -0.039 | -0.051 | -0.034 | -0.019 | -0.053 |
| Asia | 7657 | 10316 | +0.007 | +0.011 | +0.013 | -0.003 | +0.009 |
| South America | 991 | 3248 | +0.027 | -0.079 | +0.051 | +0.070 | +0.066 |
| North America | 2057 | 6999 | +0.022 | +0.026 | +0.036 | +0.003 | +0.022 |

### Depth (family score + its metrics)

| continent | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.000 | +0.052 | +0.055 | -0.064 | -0.046 |
| Europe | 6011 | 14101 | -0.024 | -0.047 | -0.033 | +0.000 | -0.017 |
| Africa | 2240 | 6599 | -0.018 | -0.010 | -0.018 | -0.037 | -0.009 |
| Asia | 7657 | 10316 | +0.016 | +0.016 | +0.010 | +0.027 | +0.012 |
| South America | 991 | 3248 | +0.053 | +0.122 | +0.089 | -0.063 | +0.064 |
| North America | 2057 | 6999 | +0.004 | +0.001 | +0.004 | +0.004 | +0.008 |

### Structure (family score + its metrics)

| continent | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.022 | -0.140 | +0.046 | +0.017 | -0.036 | -0.097 | +0.081 |
| Europe | 6011 | 14101 | +0.004 | +0.031 | -0.002 | +0.007 | +0.001 | +0.036 | -0.051 |
| Africa | 2240 | 6599 | -0.012 | -0.031 | +0.033 | +0.014 | -0.069 | +0.011 | -0.031 |
| Asia | 7657 | 10316 | +0.004 | +0.009 | -0.020 | -0.003 | +0.033 | -0.007 | +0.014 |
| South America | 991 | 3248 | -0.025 | -0.087 | +0.029 | -0.006 | -0.106 | -0.114 | +0.137 |
| North America | 2057 | 6999 | +0.011 | +0.029 | +0.005 | -0.028 | +0.021 | +0.018 | +0.018 |

### Metacognitive (family score + its metrics)

| continent | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.008 | +0.007 | +0.031 | +0.031 | -0.100 |
| Europe | 6011 | 14101 | -0.005 | -0.018 | -0.021 | +0.005 | +0.013 |
| Africa | 2240 | 6599 | +0.022 | +0.018 | -0.018 | +0.095 | -0.008 |
| Asia | 7657 | 10316 | +0.006 | +0.019 | +0.009 | -0.012 | +0.007 |
| South America | 991 | 3248 | -0.026 | -0.066 | +0.068 | -0.061 | -0.046 |
| North America | 2057 | 6999 | -0.013 | -0.012 | -0.003 | -0.061 | +0.025 |

### Efficiency (family score + its metrics)

| continent | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | +0.025 | +0.045 | +0.004 |
| Europe | 6011 | 14101 | -0.028 | -0.031 | -0.025 |
| Africa | 2240 | 6599 | +0.007 | +0.023 | -0.008 |
| Asia | 7657 | 10316 | +0.021 | +0.013 | +0.029 |
| South America | 991 | 3248 | -0.015 | -0.019 | -0.011 |
| North America | 2057 | 6999 | -0.013 | -0.002 | -0.024 |

### Summary size pair

| continent | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Oceania | 1156 | 3103 | +0.072 | +0.064 |
| Europe | 6011 | 14101 | -0.037 | -0.042 |
| Africa | 2240 | 6599 | +0.022 | -0.042 |
| Asia | 7657 | 10316 | +0.025 | +0.022 |
| South America | 991 | 3248 | -0.023 | +0.089 |
| North America | 2057 | 6999 | -0.037 | +0.009 |

## NOT-KILLED

### Breadth (family score + its metrics)

| continent | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.027 | -0.119 | -0.048 | +0.041 | +0.019 |
| Europe | 6011 | 14101 | +0.001 | -0.014 | +0.008 | +0.004 | +0.006 |
| Africa | 2240 | 6599 | +0.012 | +0.001 | +0.007 | +0.020 | +0.020 |
| Asia | 7657 | 10316 | -0.002 | +0.011 | +0.002 | -0.010 | -0.011 |
| South America | 991 | 3248 | -0.052 | -0.147 | -0.073 | +0.025 | -0.015 |
| North America | 2057 | 6999 | -0.005 | +0.008 | -0.013 | -0.014 | -0.002 |

### Depth (family score + its metrics)

| continent | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.010 | -0.004 | +0.013 | -0.057 | +0.008 |
| Europe | 6011 | 14101 | +0.010 | +0.020 | +0.014 | -0.000 | +0.007 |
| Africa | 2240 | 6599 | +0.010 | +0.017 | +0.018 | +0.012 | -0.006 |
| Asia | 7657 | 10316 | -0.010 | -0.009 | -0.013 | -0.011 | -0.008 |
| South America | 991 | 3248 | -0.009 | +0.012 | +0.015 | -0.039 | -0.025 |
| North America | 2057 | 6999 | -0.006 | -0.008 | -0.012 | -0.007 | +0.005 |

### Structure (family score + its metrics)

| continent | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.016 | -0.096 | +0.056 | +0.054 | -0.095 | -0.041 | +0.024 |
| Europe | 6011 | 14101 | -0.002 | -0.013 | +0.001 | -0.003 | -0.001 | -0.015 | +0.022 |
| Africa | 2240 | 6599 | -0.007 | -0.000 | -0.011 | -0.008 | -0.018 | -0.024 | +0.018 |
| Asia | 7657 | 10316 | +0.001 | +0.012 | +0.005 | -0.004 | -0.008 | +0.012 | -0.012 |
| South America | 991 | 3248 | -0.022 | -0.137 | +0.079 | +0.051 | -0.095 | -0.058 | +0.027 |
| North America | 2057 | 6999 | +0.009 | +0.005 | -0.004 | +0.011 | +0.041 | +0.012 | -0.011 |

### Metacognitive (family score + its metrics)

| continent | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.011 | -0.019 | +0.001 | +0.042 | -0.067 |
| Europe | 6011 | 14101 | +0.002 | +0.007 | +0.009 | -0.002 | -0.005 |
| Africa | 2240 | 6599 | -0.002 | +0.002 | +0.012 | -0.014 | -0.006 |
| Asia | 7657 | 10316 | -0.002 | -0.014 | -0.006 | +0.002 | +0.011 |
| South America | 991 | 3248 | -0.002 | +0.002 | +0.006 | +0.095 | -0.113 |
| North America | 2057 | 6999 | -0.000 | +0.003 | -0.006 | +0.007 | -0.005 |

### Efficiency (family score + its metrics)

| continent | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.013 | -0.006 | -0.020 |
| Europe | 6011 | 14101 | +0.012 | +0.013 | +0.011 |
| Africa | 2240 | 6599 | +0.001 | -0.007 | +0.009 |
| Asia | 7657 | 10316 | -0.016 | -0.010 | -0.022 |
| South America | 991 | 3248 | +0.015 | +0.039 | -0.009 |
| North America | 2057 | 6999 | +0.004 | +0.006 | +0.003 |

### Summary size pair

| continent | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Oceania | 1156 | 3103 | -0.018 | +0.011 |
| Europe | 6011 | 14101 | +0.016 | +0.018 |
| Africa | 2240 | 6599 | +0.005 | +0.015 |
| Asia | 7657 | 10316 | -0.018 | -0.019 |
| South America | 991 | 3248 | +0.043 | +0.011 |
| North America | 2057 | 6999 | +0.012 | -0.001 |
