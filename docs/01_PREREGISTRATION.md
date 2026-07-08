# PRE-REGISTRATION DOCUMENT — COOL-LOOP STUDY
**Complete every section, sign, date, commit to GitHub BEFORE the first comparison trial (Phase 4).**
**After signing, this file is never edited. Deviations get documented in a separate DEVIATIONS.md with reasons.**

## Why this document exists (read once, believe forever)
If you define your success metric after seeing the data, you can always find a definition that makes your method look good—and sharp judges know it. Pre-registration is how real scientists tie their own hands. It is also a weapon: when an STS judge asks "how do you know you didn't cherry-pick your water-event threshold?" you hand them this file with a git commit hash dated before your first trial. Almost no high school project can do that.

---

# 1. FROZEN DEFINITIONS

## 1.1 Water-equivalent cooling event (PRIMARY METRIC)

A real hybrid-cooled data center switches on evaporative (water-consuming) cooling when dry cooling can no longer hold safe temperatures. Our rig has no evaporative stage, so we define the moment one *would have been required*:

> A **water-equivalent event** begins when **T_fluid exceeds T_trigger = 42.0°C** while fan PWM has remained at **100% for at least 60 continuous seconds** (dry cooling saturated). The event ends when **T_fluid falls below 41.0°C**, providing a **1.0°C hysteresis** to prevent repeated counting caused by small oscillations around the threshold.

Each trial reports:

- Water-equivalent event count
- Total water-equivalent event duration (seconds)

**Justification**

A trigger temperature of **42.0°C** was selected because it is sufficiently above the nominal operating setpoint (38.0°C) to avoid counting ordinary controller fluctuations while remaining below the experimental safety limit of 45.0°C. Requiring the cooling fan to remain at maximum speed for at least 60 continuous seconds ensures that dry cooling has reached sustained capacity before an event is recorded, approximating when a real hybrid-cooled facility would require evaporative cooling. A 1.0°C hysteresis prevents artificial inflation of event counts due to small temperature oscillations.

- **T_trigger chosen:** 42.0°C
- **Fan-saturation window:** 60 continuous seconds at 100% PWM
- **Hysteresis:** 1.0°C

These values are frozen in `src/config.py` (T_TRIGGER, FAN_SAT_WINDOW, HYSTERESIS) and implemented identically in the live detector (`run_trial.py`) and the post-hoc analysis (`analyze.py`).

---

## 1.2 Safety thresholds (never change)

- Experiment fluid temperature limit: **45.0°C**
- Independent hardware thermal cutoff: **55.0°C**
- Any trial reaching the hardware cutoff will be retained in the dataset, labeled as a failed trial, and reported in all analyses.

---

## 1.3 Thermal banking depth

Thermal banking depth is defined as

> **Depth = T_setpoint − T_fluid**

measured immediately before a forecasted stress period begins.

Levels tested:

- 0°C (banking disabled)
- 1°C
- 2°C
- 4°C

---

## 1.4 Trial validity

A trial is considered VALID unless one or more of the following occur:

- Sensor dropout exceeding 10 seconds total
- Leak detected
- Manual intervention after warm-up
- Initial T_fluid outside the 30–33°C starting band
- Ambient conditions deviate beyond the scripted climate profile tolerance

Invalid trials remain in `/data/raw`, are labeled `invalid` with a documented reason, are excluded from statistical analysis, and are reported in the manuscript.

---

## 1.5 Rig design point (Phase 0.1 physics check)

- Design thermal capacitance: **C ≈ 7,600 J/K** (≈ 4 kg mineral oil × ~1,900 J/kg·K), as configured in `src/config.py` (C_THERMAL).
- Stored banking energy at 3°C pre-cool: **ΔE = 7,600 × 3 = 22,800 J**
- Worst-case coast time at 100 W net load: **t = 22,800 / 100 = 228 s ≈ 3.8 minutes**

**Recorded design decision:** the 3.8-minute figure is a worst-case lower bound that assumes zero heat rejection during the coast; in practice the fan continues rejecting heat during stress, so effective net load is well below 100 W and realized coast times are longer. We accept this design point for the V1 build. If Phase 1 heat-up/cool-down curves show realized coast under ~3 minutes, we will add oil volume and/or aluminum thermal mass per the roadmap risk table and re-record this section in DEVIATIONS.md before any comparison trials.

Design C is provisional until Phase 3.1 calibration; the fitted value replaces it in `config.py` in a commit labeled "calibration." The metric definitions in §1.1 do not change with calibration.

---

# 2. HYPOTHESES

**H1 (Primary)**

Forecast-aware MPC produces fewer water-equivalent events than PID under hot-humid and heat-wave climate profiles.

Expected reduction:

**10–35%**

---

**H2**

Forecast-aware MPC outperforms reactive MPC under identical stress conditions, demonstrating that forecast information provides measurable value beyond MPC structure alone.

---

**H3**

Under the mild climate profile, differences among PID, Reactive MPC, and Forecast-aware MPC are expected to be small or statistically insignificant.

---

**H4**

The benefit of thermal banking becomes material when

> **Π₁ = t_coast / t_stress ≥ 0.5**

Forecast value is expected to decline substantially when forecast error exceeds approximately

> **0.5 × ΔT_bank**

(Boundary values derived and confirmed via `05_CRITERION_WORKSHEET.md` §2–3 prior to signing.)

---

**H5**

Forecast-aware MPC is expected to consume equal or moderately greater fan energy (approximately 0–15% more than PID) while reducing water-equivalent events, producing a favorable Pareto trade rather than a free improvement.

---

# 3. TRIAL MATRIX (FROZEN)

Core experiment:

- 3 controllers
- 4 climate profiles
- 2 workload profiles
- 3 repeats

**72 core trials**

Randomization seed:

**42**

Generated using

```bash
py src/profiles.py --shuffle 42
```

Workload profiles command a 60 W baseline with 140 W bursts, respecting the 150 W hardware ceiling recorded on ISEF Form 3 and enforced in `hardware.py` (MAX_HEATER_W).

Additional experiments:

### Banking-depth sweep

Forecast-aware MPC

Hot-humid climate

Bursty workload

4 banking depths × 3 repeats

**12 trials**

### Forecast-error sweep

Forecast-aware MPC

Hot-humid and heat-wave climates

Bursty workload

Forecast conditions:

- Perfect forecast
- ±1°C temperature error
- ±3°C temperature error
- ±15% relative humidity error

4 forecast conditions × 2 climates × 3 repeats

**24 trials**

**Minimum planned dataset: 108 valid trials**

---

# 4. ANALYSIS PLAN (FROZEN)

## Primary analysis

Paired Wilcoxon signed-rank test on total water-equivalent event duration.

Pairing is performed across identical:

- Climate profile
- Workload
- Repeat

Report:

- Median paired difference
- Rank-biserial effect size
- Bootstrap 95% confidence interval (10,000 resamples)

---

## Secondary analyses

- Fan energy consumption (Wh)
- Peak fluid temperature
- Time above water-equivalent threshold

---

## Criterion analysis

Scatter plot of banking benefit versus Π₁ across all conditions.

Overlay the pre-registered criterion boundary.

Report whether the observed transition falls within ±50% of the predicted Π₁ threshold.

---

## Simulation data

Simulation-mode output (files prefixed `sim_`) exists for pipeline validation only and is excluded from all hypothesis tests and reported statistics. Only hardware trials enter the analyses above.

---

## Missing data

Sensor dropouts shorter than 10 seconds may be linearly interpolated for visualization only.

Statistical analyses will use observed measurements only.

Missing values will never be used to create or remove water-equivalent events.

---

No metric definitions, hypotheses, exclusions, statistical procedures, or success criteria may be modified after signing.

Any analyses conceived after viewing the data will be explicitly labeled **Exploratory Analysis**.

---

# 5. SIGNATURES

**Student:** Katie Wang 

**Date:** 7/7/2026

**Supervising Adult:** Nora Wang 

**Date:** 7/7/2026

**Git commit hash after signing:**

8874c8e47da73dc34bcd009d045ee54e24291a5a

