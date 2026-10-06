# Body type — 5 profiles + all 22 metrics, KILLED vs NOT-KILLED

All values in **SD units** (z-scored across the 20,112 nationality traces; 0 = average trace).
`KILLED` = the chosen victim belongs to this group.
`NOT-KILLED` = at least one member was on offer, someone else was chosen.

**Exposure note:** a line-up can hold several members of one group, so the fair share is not
25% everywhere. `expected_%` is computed per trial as (members on offer)/4; `rel_risk` = observed/expected (1.00 = exactly fair).

Full data: `results/body_type_profiles_metrics_kill_vs_notkill.csv`

## Exposure and kill share

| body_type | members | n killed | n not-killed | observed % | expected % | rel. risk |
|---|---:|---:|---:|---:|---:|---:|
| Obese | 1 | 1788 | 415 | 81.2 | 25.0 | 3.246 |
| Wheelchair user | 1 | 1149 | 1218 | 48.5 | 25.0 | 1.942 |
| Skinny | 1 | 601 | 1766 | 25.4 | 25.0 | 1.016 |
| Slim | 1 | 508 | 1859 | 21.5 | 25.0 | 0.858 |
| Athletic | 1 | 153 | 2050 | 6.9 | 25.0 | 0.278 |
| Muscular | 1 | 146 | 2057 | 6.6 | 25.0 | 0.265 |
| Overweight | 1 | 116 | 2087 | 5.3 | 25.0 | 0.211 |
| Amputee | 1 | 109 | 2258 | 4.6 | 25.0 | 0.184 |

> **Caution:** unadjusted means. Model identity alone explains up to ~90% of these
> metrics, and the controlled within-line-up test left 1 of 520 cells significant against a
> 0.075 SD detection floor. Read single rows as candidates, not findings.

---

## DIFFERENCE (killed − not killed)

### Breadth (family score + its metrics)

| body_type | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.241 | -0.361 | -0.232 | -0.213 | -0.156 |
| Wheelchair user | 1149 | 1218 | -0.485 | -0.709 | -0.500 | -0.291 | -0.440 |
| Skinny | 601 | 1766 | +0.291 | +0.293 | +0.243 | +0.296 | +0.332 |
| Slim | 508 | 1859 | +0.471 | +0.881 | +0.491 | +0.142 | +0.371 |
| Athletic | 153 | 2050 | +0.154 | +0.197 | +0.150 | +0.196 | +0.072 |
| Muscular | 146 | 2057 | +0.259 | +0.451 | +0.158 | +0.174 | +0.251 |
| Overweight | 116 | 2087 | +0.217 | +0.293 | +0.321 | +0.181 | +0.073 |
| Amputee | 109 | 2258 | -0.304 | -0.615 | -0.086 | -0.168 | -0.349 |

### Depth (family score + its metrics)

| body_type | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.067 | -0.060 | -0.213 | -0.097 | +0.103 |
| Wheelchair user | 1149 | 1218 | -0.081 | +0.140 | -0.241 | -0.272 | +0.049 |
| Skinny | 601 | 1766 | +0.060 | +0.009 | +0.242 | +0.101 | -0.113 |
| Slim | 508 | 1859 | +0.045 | -0.362 | +0.098 | +0.325 | +0.117 |
| Athletic | 153 | 2050 | +0.120 | +0.202 | +0.153 | +0.093 | +0.032 |
| Muscular | 146 | 2057 | -0.091 | -0.174 | +0.136 | +0.118 | -0.446 |
| Overweight | 116 | 2087 | +0.162 | +0.138 | +0.284 | +0.029 | +0.196 |
| Amputee | 109 | 2258 | +0.032 | +0.553 | -0.048 | -0.137 | -0.242 |

### Structure (family score + its metrics)

| body_type | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | +0.080 | -0.362 | +0.269 | +0.313 | +0.047 | +0.148 | +0.064 |
| Wheelchair user | 1149 | 1218 | +0.123 | -0.689 | +0.260 | +0.634 | +0.315 | +0.098 | +0.120 |
| Skinny | 601 | 1766 | -0.111 | +0.326 | -0.124 | -0.410 | -0.250 | -0.236 | +0.030 |
| Slim | 508 | 1859 | -0.086 | +0.801 | -0.297 | -0.565 | -0.343 | +0.244 | -0.357 |
| Athletic | 153 | 2050 | +0.014 | +0.216 | -0.134 | -0.157 | +0.202 | -0.130 | +0.086 |
| Muscular | 146 | 2057 | -0.175 | +0.470 | -0.372 | -0.510 | -0.251 | -0.160 | -0.230 |
| Overweight | 116 | 2087 | -0.045 | +0.246 | -0.190 | -0.124 | -0.095 | -0.086 | -0.023 |
| Amputee | 109 | 2258 | +0.108 | -0.564 | +0.197 | +0.334 | +0.602 | -0.475 | +0.554 |

### Metacognitive (family score + its metrics)

| body_type | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | +0.023 | +0.103 | -0.045 | +0.311 | -0.276 |
| Wheelchair user | 1149 | 1218 | +0.011 | +0.095 | -0.220 | +0.730 | -0.563 |
| Skinny | 601 | 1766 | -0.035 | -0.078 | +0.228 | -0.501 | +0.211 |
| Slim | 508 | 1859 | -0.002 | -0.020 | -0.008 | -0.728 | +0.745 |
| Athletic | 153 | 2050 | -0.057 | -0.066 | -0.090 | -0.135 | +0.062 |
| Muscular | 146 | 2057 | -0.082 | -0.113 | -0.007 | -0.559 | +0.352 |
| Overweight | 116 | 2087 | +0.104 | -0.091 | +0.263 | -0.085 | +0.328 |
| Amputee | 109 | 2258 | +0.100 | -0.128 | +0.297 | +0.801 | -0.570 |

### Efficiency (family score + its metrics)

| body_type | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Obese | 1788 | 415 | +0.050 | -0.060 | +0.160 |
| Wheelchair user | 1149 | 1218 | +0.291 | +0.209 | +0.374 |
| Skinny | 601 | 1766 | -0.177 | -0.138 | -0.215 |
| Slim | 508 | 1859 | -0.308 | -0.344 | -0.272 |
| Athletic | 153 | 2050 | +0.134 | +0.299 | -0.031 |
| Muscular | 146 | 2057 | -0.249 | -0.316 | -0.182 |
| Overweight | 116 | 2087 | -0.018 | +0.189 | -0.225 |
| Amputee | 109 | 2258 | +0.285 | +0.726 | -0.156 |

### Summary size pair

| body_type | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Obese | 1788 | 415 | -0.082 | -0.142 |
| Wheelchair user | 1149 | 1218 | +0.194 | -0.129 |
| Skinny | 601 | 1766 | -0.194 | +0.163 |
| Slim | 508 | 1859 | -0.397 | -0.144 |
| Athletic | 153 | 2050 | +0.320 | +0.185 |
| Muscular | 146 | 2057 | -0.255 | -0.041 |
| Overweight | 116 | 2087 | +0.152 | +0.246 |
| Amputee | 109 | 2258 | +1.262 | +0.583 |

## KILLED

### Breadth (family score + its metrics)

| body_type | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.067 | -0.153 | -0.119 | +0.001 | +0.003 |
| Wheelchair user | 1149 | 1218 | -0.229 | -0.285 | -0.188 | -0.188 | -0.257 |
| Skinny | 601 | 1766 | +0.237 | +0.298 | +0.251 | +0.183 | +0.217 |
| Slim | 508 | 1859 | +0.390 | +0.771 | +0.455 | +0.073 | +0.261 |
| Athletic | 153 | 2050 | +0.121 | +0.098 | +0.064 | +0.224 | +0.099 |
| Muscular | 146 | 2057 | +0.220 | +0.336 | +0.073 | +0.204 | +0.267 |
| Overweight | 116 | 2087 | +0.184 | +0.192 | +0.230 | +0.213 | +0.102 |
| Amputee | 109 | 2258 | -0.270 | -0.507 | -0.013 | -0.199 | -0.363 |

### Depth (family score + its metrics)

| body_type | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.018 | -0.046 | -0.043 | -0.039 | +0.057 |
| Wheelchair user | 1149 | 1218 | -0.037 | +0.104 | -0.122 | -0.121 | -0.010 |
| Skinny | 601 | 1766 | +0.049 | +0.039 | +0.183 | +0.095 | -0.119 |
| Slim | 508 | 1859 | +0.040 | -0.252 | +0.080 | +0.275 | +0.057 |
| Athletic | 153 | 2050 | +0.107 | +0.154 | +0.140 | +0.066 | +0.067 |
| Muscular | 146 | 2057 | -0.090 | -0.197 | +0.125 | +0.090 | -0.378 |
| Overweight | 116 | 2087 | +0.148 | +0.097 | +0.266 | +0.006 | +0.223 |
| Amputee | 109 | 2258 | +0.035 | +0.560 | -0.043 | -0.111 | -0.266 |

### Structure (family score + its metrics)

| body_type | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | +0.004 | -0.170 | +0.146 | +0.081 | -0.100 | +0.067 | -0.000 |
| Wheelchair user | 1149 | 1218 | +0.074 | -0.260 | +0.045 | +0.305 | +0.264 | +0.014 | +0.073 |
| Skinny | 601 | 1766 | -0.072 | +0.338 | -0.181 | -0.327 | -0.085 | -0.212 | +0.034 |
| Slim | 508 | 1859 | -0.057 | +0.724 | -0.322 | -0.465 | -0.168 | +0.155 | -0.269 |
| Athletic | 153 | 2050 | +0.002 | +0.100 | -0.029 | -0.123 | +0.079 | -0.082 | +0.068 |
| Muscular | 146 | 2057 | -0.175 | +0.338 | -0.252 | -0.454 | -0.344 | -0.110 | -0.227 |
| Overweight | 116 | 2087 | -0.054 | +0.132 | -0.085 | -0.095 | -0.199 | -0.043 | -0.034 |
| Amputee | 109 | 2258 | +0.113 | -0.444 | +0.099 | +0.298 | +0.676 | -0.489 | +0.540 |

### Metacognitive (family score + its metrics)

| body_type | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.008 | +0.010 | -0.021 | +0.089 | -0.109 |
| Wheelchair user | 1149 | 1218 | +0.017 | +0.058 | -0.102 | +0.348 | -0.237 |
| Skinny | 601 | 1766 | -0.015 | -0.050 | +0.182 | -0.402 | +0.211 |
| Slim | 508 | 1859 | +0.009 | -0.007 | +0.006 | -0.600 | +0.639 |
| Athletic | 153 | 2050 | -0.065 | -0.071 | -0.096 | -0.095 | +0.001 |
| Muscular | 146 | 2057 | -0.089 | -0.115 | -0.019 | -0.492 | +0.272 |
| Overweight | 116 | 2087 | +0.086 | -0.096 | +0.237 | -0.050 | +0.253 |
| Amputee | 109 | 2258 | +0.106 | -0.114 | +0.294 | +0.736 | -0.490 |

### Efficiency (family score + its metrics)

| body_type | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.046 | -0.050 | -0.042 |
| Wheelchair user | 1149 | 1218 | +0.202 | +0.143 | +0.260 |
| Skinny | 601 | 1766 | -0.080 | -0.067 | -0.093 |
| Slim | 508 | 1859 | -0.190 | -0.234 | -0.146 |
| Athletic | 153 | 2050 | +0.069 | +0.240 | -0.102 |
| Muscular | 146 | 2057 | -0.288 | -0.333 | -0.242 |
| Overweight | 116 | 2087 | -0.073 | +0.141 | -0.286 |
| Amputee | 109 | 2258 | +0.324 | +0.728 | -0.081 |

### Summary size pair

| body_type | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Obese | 1788 | 415 | -0.068 | -0.081 |
| Wheelchair user | 1149 | 1218 | +0.148 | -0.016 |
| Skinny | 601 | 1766 | -0.097 | +0.172 |
| Slim | 508 | 1859 | -0.263 | -0.063 |
| Athletic | 153 | 2050 | +0.245 | +0.117 |
| Muscular | 146 | 2057 | -0.290 | -0.092 |
| Overweight | 116 | 2087 | +0.092 | +0.178 |
| Amputee | 109 | 2258 | +1.253 | +0.607 |

## NOT-KILLED

### Breadth (family score + its metrics)

| body_type | n_kill | n_notk | Breadth | branching factor | unique perspective count | domain spread | first idea diversity |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | +0.174 | +0.208 | +0.114 | +0.214 | +0.159 |
| Wheelchair user | 1149 | 1218 | +0.256 | +0.423 | +0.312 | +0.103 | +0.183 |
| Skinny | 601 | 1766 | -0.054 | +0.005 | +0.008 | -0.113 | -0.115 |
| Slim | 508 | 1859 | -0.081 | -0.110 | -0.036 | -0.069 | -0.110 |
| Athletic | 153 | 2050 | -0.032 | -0.099 | -0.085 | +0.027 | +0.028 |
| Muscular | 146 | 2057 | -0.039 | -0.115 | -0.085 | +0.030 | +0.016 |
| Overweight | 116 | 2087 | -0.033 | -0.101 | -0.092 | +0.032 | +0.029 |
| Amputee | 109 | 2258 | +0.034 | +0.108 | +0.074 | -0.030 | -0.014 |

### Depth (family score + its metrics)

| body_type | n_kill | n_notk | Depth | max elaboration chain | mean branch depth | specificity gradient | reasoning density |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | +0.049 | +0.015 | +0.170 | +0.058 | -0.046 |
| Wheelchair user | 1149 | 1218 | +0.044 | -0.036 | +0.120 | +0.151 | -0.059 |
| Skinny | 601 | 1766 | -0.011 | +0.030 | -0.059 | -0.006 | -0.007 |
| Slim | 508 | 1859 | -0.005 | +0.109 | -0.018 | -0.050 | -0.060 |
| Athletic | 153 | 2050 | -0.013 | -0.048 | -0.013 | -0.027 | +0.036 |
| Muscular | 146 | 2057 | +0.001 | -0.023 | -0.012 | -0.029 | +0.067 |
| Overweight | 116 | 2087 | -0.014 | -0.041 | -0.018 | -0.022 | +0.028 |
| Amputee | 109 | 2258 | +0.003 | +0.006 | +0.005 | +0.026 | -0.024 |

### Structure (family score + its metrics)

| body_type | n_kill | n_notk | Structure | exploration exploitation ratio | backtracking rate | cross branch connectivity | convergence index | graph density | revision depth |
|---|---|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.076 | +0.192 | -0.123 | -0.232 | -0.148 | -0.081 | -0.064 |
| Wheelchair user | 1149 | 1218 | -0.049 | +0.429 | -0.215 | -0.329 | -0.051 | -0.084 | -0.047 |
| Skinny | 601 | 1766 | +0.038 | +0.012 | -0.057 | +0.083 | +0.165 | +0.024 | +0.004 |
| Slim | 508 | 1859 | +0.029 | -0.078 | -0.025 | +0.100 | +0.175 | -0.088 | +0.088 |
| Athletic | 153 | 2050 | -0.012 | -0.116 | +0.104 | +0.033 | -0.123 | +0.048 | -0.018 |
| Muscular | 146 | 2057 | +0.000 | -0.133 | +0.120 | +0.056 | -0.092 | +0.049 | +0.003 |
| Overweight | 116 | 2087 | -0.009 | -0.114 | +0.105 | +0.029 | -0.104 | +0.043 | -0.011 |
| Amputee | 109 | 2258 | +0.005 | +0.120 | -0.097 | -0.036 | +0.074 | -0.014 | -0.014 |

### Metacognitive (family score + its metrics)

| body_type | n_kill | n_notk | Metacognitive | self reflection rate | critique to hypothesis ratio | hedging density | perspective taking |
|---|---|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.031 | -0.093 | +0.024 | -0.222 | +0.167 |
| Wheelchair user | 1149 | 1218 | +0.006 | -0.038 | +0.119 | -0.382 | +0.327 |
| Skinny | 601 | 1766 | +0.020 | +0.028 | -0.046 | +0.099 | -0.000 |
| Slim | 508 | 1859 | +0.012 | +0.013 | +0.013 | +0.128 | -0.107 |
| Athletic | 153 | 2050 | -0.008 | -0.005 | -0.006 | +0.039 | -0.061 |
| Muscular | 146 | 2057 | -0.007 | -0.002 | -0.012 | +0.067 | -0.080 |
| Overweight | 116 | 2087 | -0.018 | -0.004 | -0.026 | +0.034 | -0.074 |
| Amputee | 109 | 2258 | +0.007 | +0.014 | -0.002 | -0.065 | +0.079 |

### Efficiency (family score + its metrics)

| body_type | n_kill | n_notk | Efficiency | token per idea | redundancy ratio |
|---|---|---|---|---|---|
| Obese | 1788 | 415 | -0.096 | +0.010 | -0.203 |
| Wheelchair user | 1149 | 1218 | -0.090 | -0.066 | -0.114 |
| Skinny | 601 | 1766 | +0.096 | +0.071 | +0.122 |
| Slim | 508 | 1859 | +0.118 | +0.109 | +0.126 |
| Athletic | 153 | 2050 | -0.065 | -0.059 | -0.070 |
| Muscular | 146 | 2057 | -0.039 | -0.017 | -0.061 |
| Overweight | 116 | 2087 | -0.054 | -0.048 | -0.061 |
| Amputee | 109 | 2258 | +0.038 | +0.002 | +0.075 |

### Summary size pair

| body_type | n_kill | n_notk | avg tokens | avg tus |
|---|---|---|---|---|
| Obese | 1788 | 415 | +0.014 | +0.061 |
| Wheelchair user | 1149 | 1218 | -0.045 | +0.113 |
| Skinny | 601 | 1766 | +0.098 | +0.009 |
| Slim | 508 | 1859 | +0.134 | +0.082 |
| Athletic | 153 | 2050 | -0.074 | -0.067 |
| Muscular | 146 | 2057 | -0.035 | -0.052 |
| Overweight | 116 | 2087 | -0.060 | -0.067 |
| Amputee | 109 | 2258 | -0.010 | +0.024 |
