# PRE-REGISTRATION DOCUMENT — COOL-LOOP STUDY
**Complete every section, sign, date, commit to GitHub BEFORE the first comparison trial (Phase 4).**
**After signing, this file is never edited. Deviations get documented in a separate DEVIATIONS.md with reasons.**

## Why this document exists (read once, believe forever)
If you define your success metric after seeing the data, you can always find a definition that makes your method look good — and sharp judges know it. Pre-registration is how real scientists tie their own hands. It is also a weapon: when an STS judge asks "how do you know you didn't cherry-pick your water-event threshold?" you hand them this file with a git commit hash dated before your first trial. Almost no high school project can do that.

---

## 1. FROZEN DEFINITIONS

### 1.1 Water-equivalent cooling event (PRIMARY METRIC)
A real hybrid-cooled data center switches on evaporative (water-consuming) cooling when dry cooling can no longer hold safe temperatures. Our rig has no evaporative stage, so we define the moment one *would have been required*:

> A **water-equivalent event** begins when T_fluid exceeds **T_trigger = ____ °C** (recommended: 42.0°C, i.e., 4°C above the 38°C setpoint) while fan PWM has been at 100% for ≥ 60 continuous seconds (dry cooling saturated). The event ends when T_fluid falls below T_trigger − 1.0°C (hysteresis prevents flicker-counting).

Reported two ways per trial: **event count** and **total event duration (s)**.

*Justification (write in your own words before signing): T_trigger sits above normal control variation but safely below the 45°C experiment cap; the fan-saturation condition ensures we only count moments where dry cooling had genuinely run out, mirroring real fallback logic.*

- T_trigger chosen: ______ °C
- Fan-saturation window: ______ s
- Hysteresis: ______ °C

### 1.2 Safety thresholds (never change; not tunable)
- Experiment cap: 45.0°C fluid → controller must shed heat load / end trial.
- Hardware cutoff: 55.0°C (independent thermal cutoff device).
- Any trial reaching hardware cutoff is recorded as a failed trial, kept in the dataset, and reported.

### 1.3 Thermal banking depth
Depth = (T_setpoint − T_fluid) at the moment a forecasted stress window begins, in °C. Levels tested: 0 (banking disabled), 1, 2, 4 °C.

### 1.4 Trial validity
A trial is VALID unless any of: sensor dropout > 10 s total; leak; manual intervention after warm-up; starting T_fluid outside 30–33°C band; ambient conditions during trial deviating from the scripted profile beyond the noise spec. Invalid trials are kept in `/data/raw`, flagged `invalid` with reason, excluded from analysis, and counted in the paper ("N invalid trials excluded because…").

---

## 2. HYPOTHESES (state before data; report against each honestly)

- **H1 (primary):** Forecast-aware MPC produces fewer water-equivalent events than PID under hot-humid and heat-wave profiles. Expected magnitude: 10–35% reduction (per prior modeling; anything larger is suspicious — investigate before celebrating).
- **H2:** Forecast-aware MPC outperforms reactive MPC under the same stress profiles (i.e., the forecast itself adds value beyond MPC structure).
- **H3 (heterogeneity):** Under the mild profile, differences between all three controllers are small or nil. A near-zero result here is a FINDING, not a failure.
- **H4 (criterion, from 05_CRITERION_WORKSHEET.md):** Banking benefit becomes material when the dimensionless ratio Π₁ = t_coast / t_stress ≥ **____** (fill from Worksheet §3 derivation BEFORE trials; recommended prediction: Π₁ ≥ ~0.5), and forecast value collapses when forecast error exceeds ____ fraction of banking depth (recommended prediction: ~0.5·ΔT_bank).
- **H5 (tradeoff):** Forecast-MPC consumes equal or more fan energy (+0–15%) than PID. We predict a favorable Pareto trade (water saved per extra Wh), not a free lunch.

---

## 3. TRIAL MATRIX (frozen)
3 controllers × 4 climate profiles × 2 workloads × 3 repeats = 72 core trials, order randomized within controller-blocks using seed = ____ (pick a number, write it down, use `profiles.py --shuffle SEED`).
Plus: banking-depth sweep (forecast-MPC, hot-humid, bursty: 4 depths × 3) = 12 trials.
Plus: forecast-error trials (forecast-MPC, hot-humid + heat-wave, bursty: error levels perfect/±1°C/±3°C/RH±15%: 4 × 2 × 3) = 24 trials.
**Total planned: 108 valid trials minimum.**

## 4. ANALYSIS PLAN (frozen)
- Primary comparison: paired Wilcoxon signed-rank on water-event duration, pairing across identical profile+workload+repeat; report median difference, effect size (rank-biserial), and bootstrap 95% CI (10,000 resamples).
- Secondary: fan energy (Wh) by ANOVA or paired comparisons; peak T; time above trigger.
- Criterion test: scatter of banking benefit vs Π₁ across all conditions; pre-registered boundary overlaid; report whether observed transition falls within ±50% of predicted Π₁.
- No metric definitions, exclusions, or hypothesis wording change after signing. New *exploratory* analyses are allowed but must be labeled exploratory in the paper.

## 5. SIGNATURES
Student: ____________________  Date: ________
Advisor (Hayden): ____________________  Date: ________
Git commit hash after signing: ____________________
