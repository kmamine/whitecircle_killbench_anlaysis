# Region — 5 profiles + all 22 metrics, KILLED vs NOT-KILLED

All values in **SD units** (z-scored across the 20,112 nationality traces; 0 = average trace).
`KILLED` = the chosen victim belongs to this group.
`NOT-KILLED` = at least one member was on offer, someone else was chosen.

**Exposure note:** a line-up can hold several members of one group, so the fair share is not
25% everywhere. `expected_%` is computed per trial as (members on offer)/4; `rel_risk` = observed/expected (1.00 = exactly fair).

Full data: `results/cultural_profiles_metrics_kill_vs_notkill.csv`

## Exposure and kill share

| cultural | members | n killed | n not-killed | observed % | expected % | rel. risk |
|---|---:|---:|---:|---:|---:|---:|
| Orthodox / Eurasian | 2 | 2621 | 6214 | 29.7 | 25.0 | 1.187 |
| Muslim Southeast Asia | 1 | 647 | 1720 | 27.3 | 25.0 | 1.093 |
| Middle East & North Africa | 3 | 2984 | 8284 | 26.5 | 25.0 | 1.059 |
| Protestant Europe | 1 | 1152 | 3213 | 26.4 | 25.0 | 1.056 |
| Catholic Europe | 2 | 1763 | 5063 | 25.8 | 25.0 | 1.033 |
| Sub-Saharan Africa | 1 | 1110 | 3262 | 25.4 | 25.0 | 1.016 |
| Anglosphere | 3 | 2674 | 6256 | 29.9 | 31.6 | 0.948 |
| Confucian East Asia | 3 | 3119 | 7989 | 28.1 | 30.0 | 0.936 |
| Latin America | 2 | 2005 | 6619 | 23.2 | 25.0 | 0.930 |
| Israel | 1 | 1045 | 3642 | 22.3 | 25.0 | 0.892 |
| South Asia | 1 | 992 | 3506 | 22.1 | 25.0 | 0.882 |

> **Caution:** unadjusted means. Model identity alone explains up to ~90% of these
> metrics, and the controlled within-line-up test left 1 of 520 cells significant against a
> 0.075 SD detection floor. Read single rows as candidates, not findings.

---

## DIFFERENCE (killed − not killed)

### Breadth (family score + its metrics)

| cultural | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.082 | -0.036 | -0.057 | -0.104 | -0.130 |
| Muslim Southeast Asia | 647 | 1720 | +0.021 | -0.021 | +0.100 | -0.009 | +0.013 |
| Middle East & North Africa | 2984 | 8284 | -0.043 | -0.047 | -0.045 | -0.033 | -0.049 |
| Protestant Europe | 1152 | 3213 | -0.037 | -0.036 | -0.083 | -0.011 | -0.019 |
| Catholic Europe | 1763 | 5063 | +0.101 | +0.170 | +0.031 | +0.096 | +0.106 |
| Sub-Saharan Africa | 1110 | 3262 | -0.038 | -0.056 | -0.055 | +0.010 | -0.051 |
| Anglosphere | 2674 | 6256 | +0.034 | +0.055 | +0.015 | +0.026 | +0.038 |
| Confucian East Asia | 3119 | 7989 | +0.048 | +0.051 | +0.056 | +0.023 | +0.060 |
| Latin America | 2005 | 6619 | +0.062 | +0.046 | +0.120 | +0.032 | +0.049 |
| Israel | 1045 | 3642 | -0.124 | -0.186 | -0.091 | -0.098 | -0.123 |
| South Asia | 992 | 3506 | +0.026 | -0.033 | -0.024 | +0.073 | +0.090 |

### Depth (family score + its metrics)

| cultural | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.062 | -0.051 | -0.096 | -0.031 | -0.070 |
| Muslim Southeast Asia | 647 | 1720 | +0.044 | +0.062 | +0.072 | +0.065 | -0.023 |
| Middle East & North Africa | 2984 | 8284 | -0.014 | -0.005 | -0.023 | -0.014 | -0.015 |
| Protestant Europe | 1152 | 3213 | -0.027 | -0.048 | -0.057 | +0.003 | -0.007 |
| Catholic Europe | 1763 | 5063 | -0.006 | -0.086 | +0.011 | +0.057 | -0.006 |
| Sub-Saharan Africa | 1110 | 3262 | -0.005 | -0.005 | +0.002 | -0.052 | +0.036 |
| Anglosphere | 2674 | 6256 | +0.002 | +0.002 | +0.026 | +0.012 | -0.030 |
| Confucian East Asia | 3119 | 7989 | +0.018 | +0.010 | +0.031 | +0.007 | +0.024 |
| Latin America | 2005 | 6619 | +0.051 | +0.083 | +0.052 | -0.007 | +0.076 |
| Israel | 1045 | 3642 | +0.021 | +0.055 | -0.027 | +0.000 | +0.057 |
| South Asia | 992 | 3506 | +0.028 | +0.008 | +0.048 | +0.049 | +0.006 |

### Structure (family score + its metrics)

| cultural | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | +0.011 | -0.028 | +0.042 | +0.057 | +0.030 | +0.056 | -0.092 |
| Muslim Southeast Asia | 647 | 1720 | -0.006 | -0.038 | -0.022 | -0.036 | +0.057 | -0.103 | +0.103 |
| Middle East & North Africa | 2984 | 8284 | +0.000 | -0.047 | +0.023 | +0.042 | +0.011 | +0.012 | -0.038 |
| Protestant Europe | 1152 | 3213 | -0.003 | -0.041 | +0.011 | +0.066 | -0.012 | +0.001 | -0.044 |
| Catholic Europe | 1763 | 5063 | +0.003 | +0.160 | -0.067 | -0.051 | -0.015 | +0.045 | -0.053 |
| Sub-Saharan Africa | 1110 | 3262 | -0.003 | -0.025 | +0.036 | +0.022 | -0.053 | +0.032 | -0.031 |
| Anglosphere | 2674 | 6256 | -0.004 | +0.025 | -0.001 | -0.081 | +0.018 | +0.008 | +0.007 |
| Confucian East Asia | 3119 | 7989 | -0.001 | +0.041 | -0.029 | -0.054 | +0.017 | -0.029 | +0.051 |
| Latin America | 2005 | 6619 | +0.005 | +0.042 | -0.033 | -0.035 | -0.004 | -0.034 | +0.094 |
| Israel | 1045 | 3642 | +0.019 | -0.133 | +0.075 | +0.139 | +0.013 | +0.032 | -0.016 |
| South Asia | 992 | 3506 | -0.021 | -0.034 | -0.042 | -0.006 | -0.041 | -0.051 | +0.050 |

### Metacognitive (family score + its metrics)

| cultural | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | +0.024 | +0.019 | -0.024 | +0.118 | -0.018 |
| Muslim Southeast Asia | 647 | 1720 | +0.009 | +0.002 | +0.087 | -0.026 | -0.025 |
| Middle East & North Africa | 2984 | 8284 | +0.025 | +0.023 | +0.024 | +0.078 | -0.022 |
| Protestant Europe | 1152 | 3213 | -0.000 | +0.031 | -0.036 | +0.078 | -0.074 |
| Catholic Europe | 1763 | 5063 | -0.047 | -0.089 | -0.033 | -0.154 | +0.088 |
| Sub-Saharan Africa | 1110 | 3262 | +0.015 | +0.013 | -0.044 | +0.117 | -0.026 |
| Anglosphere | 2674 | 6256 | -0.017 | -0.011 | -0.009 | -0.063 | +0.015 |
| Confucian East Asia | 3119 | 7989 | -0.011 | +0.013 | -0.008 | -0.085 | +0.035 |
| Latin America | 2005 | 6619 | -0.007 | -0.039 | +0.061 | -0.110 | +0.059 |
| Israel | 1045 | 3642 | +0.036 | +0.104 | -0.038 | +0.164 | -0.087 |
| South Asia | 992 | 3506 | -0.022 | -0.049 | +0.032 | -0.035 | -0.038 |

### Efficiency (family score + its metrics)

| cultural | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.007 | -0.010 | -0.004 |
| Muslim Southeast Asia | 647 | 1720 | +0.077 | +0.117 | +0.037 |
| Middle East & North Africa | 2984 | 8284 | +0.012 | +0.009 | +0.014 |
| Protestant Europe | 1152 | 3213 | +0.012 | +0.014 | +0.009 |
| Catholic Europe | 1763 | 5063 | -0.078 | -0.095 | -0.062 |
| Sub-Saharan Africa | 1110 | 3262 | +0.017 | +0.040 | -0.006 |
| Anglosphere | 2674 | 6256 | -0.016 | -0.011 | -0.022 |
| Confucian East Asia | 3119 | 7989 | +0.026 | +0.020 | +0.031 |
| Latin America | 2005 | 6619 | -0.019 | -0.017 | -0.021 |
| Israel | 1045 | 3642 | +0.066 | +0.035 | +0.097 |
| South Asia | 992 | 3506 | -0.026 | -0.016 | -0.036 |

### Summary size pair

| cultural | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | +0.007 | -0.099 |
| Muslim Southeast Asia | 647 | 1720 | +0.083 | +0.084 |
| Middle East & North Africa | 2984 | 8284 | +0.031 | -0.022 |
| Protestant Europe | 1152 | 3213 | -0.007 | -0.033 |
| Catholic Europe | 1763 | 5063 | -0.123 | -0.018 |
| Sub-Saharan Africa | 1110 | 3262 | +0.042 | -0.030 |
| Anglosphere | 2674 | 6256 | -0.020 | +0.005 |
| Confucian East Asia | 3119 | 7989 | -0.004 | +0.051 |
| Latin America | 2005 | 6619 | -0.036 | +0.069 |
| Israel | 1045 | 3642 | +0.093 | -0.032 |
| South Asia | 992 | 3506 | +0.021 | +0.065 |

## KILLED

### Breadth (family score + its metrics)

| cultural | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.067 | -0.041 | -0.043 | -0.084 | -0.101 |
| Muslim Southeast Asia | 647 | 1720 | +0.074 | +0.158 | +0.137 | -0.018 | +0.017 |
| Middle East & North Africa | 2984 | 8284 | -0.025 | -0.007 | -0.021 | -0.030 | -0.043 |
| Protestant Europe | 1152 | 3213 | -0.054 | -0.076 | -0.079 | -0.028 | -0.034 |
| Catholic Europe | 1763 | 5063 | +0.096 | +0.167 | +0.037 | +0.086 | +0.094 |
| Sub-Saharan Africa | 1110 | 3262 | -0.037 | -0.078 | -0.068 | +0.029 | -0.033 |
| Anglosphere | 2674 | 6256 | +0.021 | +0.013 | -0.003 | +0.035 | +0.041 |
| Confucian East Asia | 3119 | 7989 | +0.026 | +0.001 | +0.038 | +0.021 | +0.044 |
| Latin America | 2005 | 6619 | +0.021 | -0.050 | +0.062 | +0.035 | +0.038 |
| Israel | 1045 | 3642 | -0.058 | -0.044 | -0.025 | -0.081 | -0.083 |
| South Asia | 992 | 3506 | +0.018 | +0.013 | -0.019 | +0.024 | +0.053 |

### Depth (family score + its metrics)

| cultural | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.049 | -0.039 | -0.073 | -0.035 | -0.048 |
| Muslim Southeast Asia | 647 | 1720 | +0.036 | -0.011 | +0.057 | +0.120 | -0.024 |
| Middle East & North Africa | 2984 | 8284 | -0.006 | -0.002 | -0.022 | +0.011 | -0.013 |
| Protestant Europe | 1152 | 3213 | -0.018 | -0.023 | -0.028 | -0.025 | +0.003 |
| Catholic Europe | 1763 | 5063 | -0.004 | -0.078 | +0.013 | +0.059 | -0.008 |
| Sub-Saharan Africa | 1110 | 3262 | -0.009 | +0.004 | -0.001 | -0.058 | +0.018 |
| Anglosphere | 2674 | 6256 | -0.000 | +0.006 | +0.018 | -0.004 | -0.021 |
| Confucian East Asia | 3119 | 7989 | +0.017 | +0.028 | +0.024 | -0.000 | +0.018 |
| Latin America | 2005 | 6619 | +0.036 | +0.076 | +0.058 | -0.048 | +0.059 |
| Israel | 1045 | 3642 | +0.022 | +0.027 | -0.027 | +0.045 | +0.042 |
| South Asia | 992 | 3506 | +0.013 | -0.009 | +0.018 | +0.035 | +0.008 |

### Structure (family score + its metrics)

| cultural | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | +0.007 | -0.029 | +0.034 | +0.055 | +0.007 | +0.039 | -0.064 |
| Muslim Southeast Asia | 647 | 1720 | +0.004 | +0.121 | -0.106 | -0.127 | +0.122 | +0.009 | +0.003 |
| Middle East & North Africa | 2984 | 8284 | +0.002 | -0.013 | +0.003 | +0.017 | +0.024 | +0.018 | -0.034 |
| Protestant Europe | 1152 | 3213 | -0.007 | -0.084 | +0.043 | +0.058 | -0.030 | -0.011 | -0.015 |
| Catholic Europe | 1763 | 5063 | +0.001 | +0.159 | -0.073 | -0.059 | -0.007 | +0.046 | -0.057 |
| Sub-Saharan Africa | 1110 | 3262 | -0.011 | -0.038 | +0.035 | +0.045 | -0.089 | +0.001 | -0.021 |
| Anglosphere | 2674 | 6256 | -0.002 | -0.005 | +0.012 | -0.041 | +0.013 | -0.009 | +0.017 |
| Confucian East Asia | 3119 | 7989 | -0.002 | -0.004 | -0.003 | -0.024 | +0.000 | -0.045 | +0.063 |
| Latin America | 2005 | 6619 | -0.007 | -0.048 | +0.019 | -0.000 | -0.053 | -0.060 | +0.100 |
| Israel | 1045 | 3642 | +0.022 | -0.003 | +0.003 | +0.062 | +0.052 | +0.059 | -0.041 |
| South Asia | 992 | 3506 | -0.008 | +0.021 | -0.054 | -0.003 | -0.009 | -0.007 | +0.008 |

### Metacognitive (family score + its metrics)

| cultural | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | +0.013 | -0.000 | -0.018 | +0.082 | -0.012 |
| Muslim Southeast Asia | 647 | 1720 | +0.031 | +0.038 | +0.048 | -0.074 | +0.112 |
| Middle East & North Africa | 2984 | 8284 | +0.023 | +0.021 | +0.020 | +0.051 | +0.000 |
| Protestant Europe | 1152 | 3213 | -0.007 | +0.001 | -0.016 | +0.082 | -0.093 |
| Catholic Europe | 1763 | 5063 | -0.028 | -0.047 | -0.034 | -0.127 | +0.095 |
| Sub-Saharan Africa | 1110 | 3262 | +0.008 | +0.015 | -0.037 | +0.103 | -0.047 |
| Anglosphere | 2674 | 6256 | -0.015 | -0.003 | -0.007 | -0.037 | -0.015 |
| Confucian East Asia | 3119 | 7989 | -0.010 | +0.004 | +0.003 | -0.049 | +0.001 |
| Latin America | 2005 | 6619 | -0.014 | -0.047 | +0.057 | -0.053 | -0.012 |
| Israel | 1045 | 3642 | +0.043 | +0.109 | -0.042 | +0.094 | +0.011 |
| South Asia | 992 | 3506 | -0.019 | -0.043 | +0.012 | -0.043 | -0.002 |

### Efficiency (family score + its metrics)

| cultural | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.013 | -0.017 | -0.010 |
| Muslim Southeast Asia | 647 | 1720 | +0.048 | +0.054 | +0.041 |
| Middle East & North Africa | 2984 | 8284 | +0.011 | +0.006 | +0.016 |
| Protestant Europe | 1152 | 3213 | +0.006 | +0.023 | -0.011 |
| Catholic Europe | 1763 | 5063 | -0.057 | -0.077 | -0.037 |
| Sub-Saharan Africa | 1110 | 3262 | +0.015 | +0.023 | +0.007 |
| Anglosphere | 2674 | 6256 | -0.006 | +0.002 | -0.014 |
| Confucian East Asia | 3119 | 7989 | +0.023 | +0.029 | +0.018 |
| Latin America | 2005 | 6619 | -0.017 | -0.003 | -0.031 |
| Israel | 1045 | 3642 | +0.051 | +0.016 | +0.087 |
| South Asia | 992 | 3506 | -0.028 | -0.031 | -0.025 |

### Summary size pair

| cultural | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.013 | -0.077 |
| Muslim Southeast Asia | 647 | 1720 | +0.046 | +0.035 |
| Middle East & North Africa | 2984 | 8284 | +0.023 | -0.021 |
| Protestant Europe | 1152 | 3213 | +0.001 | -0.020 |
| Catholic Europe | 1763 | 5063 | -0.088 | -0.016 |
| Sub-Saharan Africa | 1110 | 3262 | +0.030 | -0.030 |
| Anglosphere | 2674 | 6256 | -0.003 | +0.016 |
| Confucian East Asia | 3119 | 7989 | +0.010 | +0.052 |
| Latin America | 2005 | 6619 | -0.022 | +0.067 |
| Israel | 1045 | 3642 | +0.078 | -0.034 |
| South Asia | 992 | 3506 | -0.005 | +0.020 |

## NOT-KILLED

### Breadth (family score + its metrics)

| cultural | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | +0.015 | -0.005 | +0.014 | +0.020 | +0.029 |
| Muslim Southeast Asia | 647 | 1720 | +0.053 | +0.179 | +0.037 | -0.009 | +0.005 |
| Middle East & North Africa | 2984 | 8284 | +0.018 | +0.040 | +0.024 | +0.003 | +0.007 |
| Protestant Europe | 1152 | 3213 | -0.017 | -0.040 | +0.004 | -0.017 | -0.014 |
| Catholic Europe | 1763 | 5063 | -0.005 | -0.003 | +0.006 | -0.010 | -0.012 |
| Sub-Saharan Africa | 1110 | 3262 | +0.001 | -0.022 | -0.012 | +0.018 | +0.018 |
| Anglosphere | 2674 | 6256 | -0.012 | -0.042 | -0.019 | +0.009 | +0.004 |
| Confucian East Asia | 3119 | 7989 | -0.022 | -0.050 | -0.018 | -0.002 | -0.016 |
| Latin America | 2005 | 6619 | -0.040 | -0.095 | -0.058 | +0.003 | -0.011 |
| Israel | 1045 | 3642 | +0.066 | +0.142 | +0.066 | +0.017 | +0.039 |
| South Asia | 992 | 3506 | -0.009 | +0.047 | +0.004 | -0.048 | -0.037 |

### Depth (family score + its metrics)

| cultural | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | +0.013 | +0.012 | +0.023 | -0.004 | +0.022 |
| Muslim Southeast Asia | 647 | 1720 | -0.008 | -0.073 | -0.015 | +0.054 | -0.000 |
| Middle East & North Africa | 2984 | 8284 | +0.008 | +0.003 | +0.002 | +0.025 | +0.002 |
| Protestant Europe | 1152 | 3213 | +0.009 | +0.025 | +0.028 | -0.029 | +0.011 |
| Catholic Europe | 1763 | 5063 | +0.003 | +0.008 | +0.002 | +0.001 | -0.001 |
| Sub-Saharan Africa | 1110 | 3262 | -0.004 | +0.009 | -0.003 | -0.006 | -0.018 |
| Anglosphere | 2674 | 6256 | -0.003 | +0.005 | -0.007 | -0.016 | +0.008 |
| Confucian East Asia | 3119 | 7989 | -0.001 | +0.018 | -0.007 | -0.007 | -0.006 |
| Latin America | 2005 | 6619 | -0.015 | -0.007 | +0.007 | -0.041 | -0.016 |
| Israel | 1045 | 3642 | +0.001 | -0.028 | +0.000 | +0.045 | -0.015 |
| South Asia | 992 | 3506 | -0.015 | -0.017 | -0.031 | -0.014 | +0.003 |

### Structure (family score + its metrics)

| cultural | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.004 | -0.000 | -0.008 | -0.003 | -0.023 | -0.018 | +0.028 |
| Muslim Southeast Asia | 647 | 1720 | +0.010 | +0.159 | -0.084 | -0.091 | +0.065 | +0.112 | -0.100 |
| Middle East & North Africa | 2984 | 8284 | +0.002 | +0.034 | -0.019 | -0.025 | +0.013 | +0.006 | +0.004 |
| Protestant Europe | 1152 | 3213 | -0.003 | -0.043 | +0.032 | -0.008 | -0.018 | -0.012 | +0.028 |
| Catholic Europe | 1763 | 5063 | -0.002 | -0.001 | -0.006 | -0.009 | +0.008 | +0.001 | -0.004 |
| Sub-Saharan Africa | 1110 | 3262 | -0.008 | -0.013 | -0.001 | +0.023 | -0.036 | -0.031 | +0.011 |
| Anglosphere | 2674 | 6256 | +0.002 | -0.030 | +0.013 | +0.040 | -0.004 | -0.016 | +0.010 |
| Confucian East Asia | 3119 | 7989 | -0.001 | -0.045 | +0.027 | +0.030 | -0.016 | -0.016 | +0.012 |
| Latin America | 2005 | 6619 | -0.012 | -0.091 | +0.052 | +0.034 | -0.049 | -0.026 | +0.006 |
| Israel | 1045 | 3642 | +0.003 | +0.129 | -0.073 | -0.077 | +0.039 | +0.028 | -0.025 |
| South Asia | 992 | 3506 | +0.013 | +0.055 | -0.012 | +0.003 | +0.032 | +0.044 | -0.042 |

### Metacognitive (family score + its metrics)

| cultural | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.011 | -0.019 | +0.006 | -0.037 | +0.006 |
| Muslim Southeast Asia | 647 | 1720 | +0.022 | +0.036 | -0.039 | -0.048 | +0.138 |
| Middle East & North Africa | 2984 | 8284 | -0.002 | -0.002 | -0.003 | -0.027 | +0.022 |
| Protestant Europe | 1152 | 3213 | -0.006 | -0.031 | +0.020 | +0.004 | -0.019 |
| Catholic Europe | 1763 | 5063 | +0.019 | +0.042 | -0.001 | +0.027 | +0.007 |
| Sub-Saharan Africa | 1110 | 3262 | -0.007 | +0.001 | +0.007 | -0.014 | -0.021 |
| Anglosphere | 2674 | 6256 | +0.001 | +0.007 | +0.002 | +0.026 | -0.030 |
| Confucian East Asia | 3119 | 7989 | +0.001 | -0.009 | +0.011 | +0.036 | -0.034 |
| Latin America | 2005 | 6619 | -0.007 | -0.008 | -0.005 | +0.057 | -0.071 |
| Israel | 1045 | 3642 | +0.008 | +0.006 | -0.004 | -0.069 | +0.098 |
| South Asia | 992 | 3506 | +0.003 | +0.006 | -0.020 | -0.008 | +0.035 |

### Efficiency (family score + its metrics)

| cultural | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.007 | -0.007 | -0.006 |
| Muslim Southeast Asia | 647 | 1720 | -0.029 | -0.063 | +0.005 |
| Middle East & North Africa | 2984 | 8284 | -0.000 | -0.003 | +0.002 |
| Protestant Europe | 1152 | 3213 | -0.005 | +0.008 | -0.019 |
| Catholic Europe | 1763 | 5063 | +0.021 | +0.017 | +0.025 |
| Sub-Saharan Africa | 1110 | 3262 | -0.002 | -0.017 | +0.013 |
| Anglosphere | 2674 | 6256 | +0.010 | +0.013 | +0.008 |
| Confucian East Asia | 3119 | 7989 | -0.002 | +0.009 | -0.014 |
| Latin America | 2005 | 6619 | +0.002 | +0.014 | -0.010 |
| Israel | 1045 | 3642 | -0.014 | -0.019 | -0.010 |
| South Asia | 992 | 3506 | -0.002 | -0.016 | +0.011 |

### Summary size pair

| cultural | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Orthodox / Eurasian | 2621 | 6214 | -0.020 | +0.022 |
| Muslim Southeast Asia | 647 | 1720 | -0.037 | -0.049 |
| Middle East & North Africa | 2984 | 8284 | -0.008 | +0.002 |
| Protestant Europe | 1152 | 3213 | +0.008 | +0.013 |
| Catholic Europe | 1763 | 5063 | +0.035 | +0.002 |
| Sub-Saharan Africa | 1110 | 3262 | -0.012 | +0.000 |
| Anglosphere | 2674 | 6256 | +0.017 | +0.011 |
| Confucian East Asia | 3119 | 7989 | +0.013 | +0.001 |
| Latin America | 2005 | 6619 | +0.015 | -0.001 |
| Israel | 1045 | 3642 | -0.015 | -0.002 |
| South Asia | 992 | 3506 | -0.026 | -0.044 |
