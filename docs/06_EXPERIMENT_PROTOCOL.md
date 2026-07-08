# EXPERIMENT PROTOCOL — COOL-LOOP
The document you hand to anyone who asks "how exactly did you run this?" Follow it identically every trial; identicality IS the experiment.

## §1 TRIAL ANATOMY (~50 min)
| Stage | Duration | What happens |
|---|---|---|
| Pre-flight | 5 min | 10-point checklist (safety doc B.6) |
| Warm-up | 10 min | Pump + fan at fixed 40% PWM, heater at baseline 60W, until T_fluid in the 30–33°C start band |
| Trial | 30 min | Controller under test takes over; scripted climate + workload profile runs; hands OFF |
| Cooldown | 10 min | Heater off, fan 100%, until T_fluid < 33°C |
| Export | 2 min | CSV auto-saved; fill notes field; log session sheet |

**The start-band rule:** every trial begins with fluid in the same 30–33°C band. If the previous cooldown didn't get there, wait. Uneven starting temperature is the sneakiest way to bias a controller comparison.

## §2 SESSION PRE-FLIGHT
Use the laminated checklist from `02_SAFETY_SRC_CHECKLIST.md` B.6. Plus one science item: confirm today's trial IDs against the randomized order list (generated once by `profiles.py --shuffle SEED`; printed; crossed off as completed). You run trials in that order, not in a convenient order.

## §3 FAIRNESS RULES (violating any of these invalidates the comparison)
1. All controllers: identical actuator limits (fan 0–100%, same slew), identical safety constraints, identical sensors.
2. All controllers see the same physical workload profile, byte-identical, replayed from file.
3. The operator does not touch anything during the 30-min trial window. If intervention is needed → trial is invalid, reason logged, re-run scheduled.
4. Randomized order (seeded). No "PID in the cool morning, MPC in the hot afternoon."
5. Ambient reality check: real room temp/RH logged every trial; sessions where the ROOM itself drifts > 3°C intra-session get flagged and reported.

## §4 DATA SCHEMA (one row per second)
`timestamp, trial_id, controller, climate, workload, repeat, T_tank_hot, T_tank_mid, T_rad_in, T_rad_out, T_ambient, RH_ambient, heater_w_cmd, heater_w_meas, fan_pwm, fan_w, forecast_T, forecast_RH, bank_depth_cmd, water_event_flag, notes`
Rules: raw CSVs are append-only and never edited; corrections happen in `analyze.py`, in code, visibly; every file committed weekly; filename = `trialID_controller_climate_workload_rep_YYYYMMDD.csv`.

## §5 SESSION LOG (paper sheet per session)
Date • operator • adult present • trials run (IDs) • room conditions • anomalies • invalid trials + reasons • oil level check • signature. Photograph each sheet into `/docs/session_logs/`.

## §6 CANONICAL FIGURE SET
1. System architecture (block diagram).
2. Temperature trajectories, 3 controllers overlaid, one hot-humid bursty trial — the pre-cooling dip visibly labeled.
3. Water-equivalent event duration: grouped bars, controller × climate, CI whiskers.
4. Forecast-error degradation: benefit vs error level (the Π₂ curve).
5. Pareto frontier: water saved vs added fan energy, one point per banking depth.
6. Climate-sensitivity heatmap + the Π₁ scatter with pre-registered boundary.
Standards: axis labels with units, readable at 50% size, colorblind-safe palette, same fonts throughout, captions that state the finding ("Forecast-MPC reduced event duration 28% in hot-humid trials") not the topic ("Results by controller").

## §7 PAPER SKELETON (15–20 pp)
Abstract (150 w, written last) → Intro (1 page, one idea: reactive cooling wastes water; does forecast help, and when?) → Background (½ page) → Methods (testbed / controllers / metrics / trial design / criterion derivation) → Results (figures in canonical order; criterion verdict; scale-transfer) → Discussion (what held, what didn't, why) → **Limitations before Conclusion** (single rig; time-compressed climates; simulated water events; lumped model; n=3/cell) → Conclusion (3 sentences, no hype) → References → Appendices (BOM, calibration data, code link, pre-registration hash).
