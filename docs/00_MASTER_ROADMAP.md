# COOL-LOOP MASTER ROADMAP
**Forecast-Aware MPC for Water-Constrained AI Cooling — Complete Execution Plan**
Katie Wang | July 2026 → November 2026 | Compressed 19-week schedule
**Status last updated: July 7, 2026**

---

## HOW TO USE THIS DOCUMENT

This is the spine. Every phase below points to a companion document with full detail:

| File | What it is |
|---|---|
| `00_MASTER_ROADMAP.md` | This file. The schedule, checkboxes, and exit conditions. |
| `01_PREREGISTRATION.md` | Frozen definitions and hypotheses. **Sign and date before first comparison trial. Never edit after.** |
| `02_SAFETY_SRC_CHECKLIST.md` | ISEF paperwork + physical safety gates. Nothing heats up until this is done. |
| `03_BUILD_TUTORIALS.md` | Step-by-step hardware assembly with explanations of WHY each step matters. |
| `04_SOFTWARE_TUTORIALS.md` | From "what is a terminal" to running MPC. Written assuming zero Python confidence. |
| `05_CRITERION_WORKSHEET.md` | The banking criterion derivation — the result that makes this project generalize. |
| `06_EXPERIMENT_PROTOCOL.md` | Exact trial procedure, trial matrix, data rules. Hand this to any judge who asks "how did you run it." |
| `07_COMPETITION_MAP.md` | Which version of the work goes where, and when. **(Not yet written — create before Phase 6.)** |
| `src/` | Starter code, heavily commented. Runs in simulation mode before any hardware arrives. |

**Rules of the road:**
1. Do phases in order. Exit conditions are real — do not start the next phase hoping to backfill.
2. Every checkbox with 🔴 is a safety or integrity gate. Skipping one can disqualify the project or hurt you.
3. When stuck for more than 90 minutes on one problem, write down exactly what you tried and what happened, then move to a parallel task. Debugging notes ARE research notes.
4. Log everything. The lab notebook (paper or digital, dated entries) starts Day 1. Judges ask to see it.

---

## THE ONE-PARAGRAPH THESIS (memorize this)

Cooling systems today react to temperature after conditions degrade. This project tests whether a controller that sees the future — weather and workload forecasts — can pre-cool ("bank" thermal capacity) during favorable windows and coast through thermal stress without water-based fallback. Three controllers (PID, reactive MPC, forecast-aware MPC) run identical trials on a physical immersion-cooling rig. The headline deliverable is not "my controller won" — it is a **predictive criterion**: a dimensionless rule, derived from physics first and tested on hardware second, that tells any engineer whether thermal banking will pay off for their system in their climate before they build anything.

---

## BUDGET PLAN (lean first, level up on proof)

Spending is gated. You buy the next tier only when the current tier's exit condition is met.

| Tier | When | What | Est. cost |
|---|---|---|---|
| **A — Lean V1** | Week 1 | Pi kit, 2× DS18B20, resistor/breadboard/wires, 2L mineral oil, 3L container, 50W aquarium heater, 12V pump, 120mm radiator + fan, tubing/clamps/barbs, 12V 3A PSU + terminal block, GFCI adapter, tray + pads | ~$245 ($170 if Pi owned) |
| **B — Instrumentation** | Week 4, after V1 exit condition | 4× more DS18B20, BME280 (temp/humidity), MOSFET PWM fan board, INA219 power sensor, inline fuses | ~$70–110 |
| **C — Real heat source** | Week 4–5, after adult review + SRC sign-off | Aluminum block, 150W cartridge heater, standalone PID controller w/ thermal cutoff, SSR + heatsink, e-stop switch, Kill-A-Watt | ~$110–160 |
| **Total** | | | **~$425–515** |

Do NOT buy Tier B or C in week 1. If V1 reveals a pump/oil compatibility problem or a tank redesign, you want that money unspent.

---

# PHASE 0 — FOUNDATIONS & PAPERWORK
**Dates: July 6 – July 12 (Week 1) | ~20 hrs**
**Goal: legal to experiment, parts ordered, physics checked, software environment alive.**

### 0.1 The go/no-go physics check (DO THIS FIRST — 1 hour)
Before ordering anything, verify the thesis is testable at rig scale. Full walkthrough in `05_CRITERION_WORKSHEET.md`, Section 1.

- [ ] Compute thermal capacitance: C = M·cp. (2 kg oil × ~1,900 J/kg·K ≈ 3,800 J/K. With 4 kg oil: ~7,600 J/K.) *(Design value C = 7,600 J/K is in `config.py`; write the hand calculation in the notebook and check this box.)*
- [ ] Compute stored banking energy for 3°C of pre-cool: ΔE = C × 3.
- [ ] Compute coast time at 100W net load: t = ΔE / 100.
- [ ] 🔴 **Decision gate:** coast time must land between ~5 and ~30 minutes for experiments to be practical in attended sessions. If under 3 min → plan for 4–5L oil + aluminum mass in tank. If over 60 min → trials become too slow; reduce oil or raise load. Record the chosen design point in the pre-registration doc.
- [ ] Consequence to internalize: your "weather forecast" horizon at rig scale is 10–40 minutes, not hours. You will **time-compress** climate profiles (1 real hour of Houston = ~5–10 rig minutes). This is a strength — write down why (you can sweep regimes a real data center can't).

### 0.2 Research compliance (runs in parallel with everything)
Full detail in `02_SAFETY_SRC_CHECKLIST.md`.

- [ ] 🔴 Identify Adult Sponsor (science teacher at SMCHS is ideal) and Designated Supervisor for hazardous steps (Hayden or another qualified adult).
- [ ] 🔴 Draft ISEF Research Plan using the template in doc 02.
- [ ] 🔴 Complete Forms 1, 1A, 1B, and Form 3 (Risk Assessment — hazardous equipment: mains heater, hot oil).
- [ ] 🔴 Get every form **signed and dated BEFORE any data collection**. Dates are checked. Backdating is fraud.
- [ ] Email OCSEF SRC (contact via ocsef.org) introducing the project and asking their preferred pre-approval route for summer-start projects. Save the reply. *(OCSEF's own site says to contact info@ocsef.org for pre-approval needed before September — this project qualifies: heaters/hazards.)*
- [ ] Create the lab notebook. First entry: today's date, project title, the physics check numbers from 0.1.

### 0.3 Orders and accounts
- [ ] Order Tier A parts (list above; exact specs in `03_BUILD_TUTORIALS.md` §1).
- [x] Create GitHub repo `cool-loop` with folders: `/hardware /src /data/raw /data/processed /figures /paper /safety /docs`. **(Done — github.com/EvangelicalThreads/cool-loop. NOTE: the repo is PUBLIC, not private as originally planned. That's fine — it becomes the service artifact anyway — but it means nothing personal, no admissions material, and no unsigned forms ever get committed.)**
- [ ] Sign up for a free weather API key (Open-Meteo needs none — preferred; NWS/NOAA api.weather.gov also free).

### 0.4 Software foundations (start before parts arrive — biggest schedule win in the plan)
Follow `04_SOFTWARE_TUTORIALS.md` §1–3.

- [x] Tutorial 1: terminal basics + install Python on the laptop. **(Python working via `py` launcher on Windows.)**
- [ ] Tutorial 2: Python crash course (variables, lists, dicts, functions, loops, reading/writing CSV) — 4–6 hrs, do all exercises. *(Do this even though the pipeline already runs — Phase 3 requires reading and explaining every controller file.)*
- [x] Run `src/thermal_sim.py` — a fake rig in software. Confirm it produces a CSV and a plot.
- [x] Run `src/logger.py --sim` and watch it log the fake rig at 1 Hz.

### 0.5 Sim pipeline validation (added July 7 — COMPLETE)
- [x] Full trial pipeline run end-to-end in sim mode: warm-up → 30-min trial → cooldown → CSV with protocol schema.
- [x] Three bugs found and fixed during validation (see session log / git history, commits c542cd7 and 3e5ca1f):
  1. Controller-name mismatch between trial CSVs (`pid`/`forecast`) and analysis matching (`PID`/`ForecastMPC`) — paired stats could never activate.
  2. Bursty workload commanded 170 W against the 150 W hardware/Form-3 cap — silently clamped; reduced to 140 W.
  3. Sim physics advanced twice on controller ticks (double `rig.read()`) — systematic timing bias; now one read per second.
- [x] Sim trials regenerated with fixed code and committed with `sim_` filename prefix (sim data stays permanently separate from future hardware data).
- [x] Verified result shape: PID shows water-equivalent events under hot_humid/bursty; reactive and forecast MPC show zero. Matched-pair Wilcoxon machinery confirmed working (activates at ≥5 pairs).
- [x] Documentation set committed to repo: 00–06 docs in `/docs`, `/safety`, `/hardware`.

**PHASE 0 EXIT CONDITION:** forms signed/dated ☐, parts ordered ☐, coast-time design point recorded ☐, simulator running on laptop ✓.
**→ Status July 7: software leg COMPLETE and ahead of schedule. Forms and parts order are the open items and the critical path.**

---

# PHASE 1 — V1 BUILD: PROVE HEAT MOVES
**Dates: July 13 – July 26 (Weeks 2–3) | ~30 hrs**
**Goal: T2 reads lower than T1 under flow. A working, leak-free, logged thermal loop.**

Follow `03_BUILD_TUTORIALS.md` §2–8 step by step. Summary checklist:

- [ ] Tank filled ~70%, on tray, on stable surface, away from outlets.
- [ ] Aquarium heater fully submerged, NOT plugged in.
- [ ] Pump at tank bottom, hot-oil line clamped, routed to radiator inlet.
- [ ] Radiator mounted above tank, cooled return line clamped, fan blowing through fins.
- [ ] T1 probe in oil near heater; T2 probe taped firmly to radiator outlet tube.
- [ ] Pi wired: probes → 3.3V/GND/GPIO4 with 4.7k pull-up. Both `28-xxxx` sensors visible in `/sys/bus/w1/devices/`.
- [ ] Day-one Pi software check: `git clone` the repo on the Pi, `pip install -r requirements.txt`, run one `--sim` trial ON THE PI before wiring anything. If the sim runs on the Pi, the whole software stack is proven on target hardware.
- [ ] 🔴 Dry-fit test passed: pump + fan on 12V, Pi reading both probes, ZERO drips, heater still unplugged.
- [ ] 🔴 First heat test (adult present, GFCI verified, heater plugged in LAST, watched 15 min, heater unplugged FIRST). **Gated on signed forms — see 0.2.**
- [ ] `logger.py` (hardware mode) logging T1, T2 at 1 Hz to timestamped CSV.
- [ ] Collect first real dataset: 30-min heat-up curve + 30-min cool-down curve. Commit to GitHub.
- [ ] Take photos of everything. Photos are competition assets.

**Common failure points and where the fix lives:** sensors not appearing → Tutorials §7. Pump airlock → Build §5. Leaks → Build §6. T2 not below T1 → Build §8 (probe contact, fan direction, flow direction).

**PHASE 1 EXIT CONDITION:** a plot, from your own logged CSV, showing T1 rising and T2 sitting 2–5°C below T1 under flow. This plot goes in the notebook and eventually in every application.

---

# PHASE 2 — INSTRUMENT + REAL HEAT SOURCE
**Dates: July 27 – Aug 9 (Weeks 4–5) | ~35 hrs**
**Goal: research-grade sensing, controllable heat, PWM fan authority.**

### 2.1 Buy Tier B + C (gates passed)
- [ ] Tier B ordered (V1 exit met).
- [ ] 🔴 Tier C ordered ONLY after Designated Supervisor reviews the cartridge-heater wiring plan in `03_BUILD_TUTORIALS.md` §9 and SRC paperwork covers it (Form 3 must list it).

### 2.2 Instrumentation (Build §10)
- [ ] 4 additional DS18B20 on the same 1-Wire bus: tank-mid, radiator inlet, ambient air, spare. Label physically AND in software config.
- [ ] BME280 wired via I2C; ambient temp + RH logging.
- [ ] INA219 measuring fan power on the 12V side.
- [ ] MOSFET PWM board controlling fan speed from Pi GPIO18. Verify: 20% / 50% / 100% duty produces audibly/measurably different airflow. *(Note: if using a 4-pin PWM fan like the Arctic P12, the PWM control wire goes to GPIO18 directly — no MOSFET needed for the fan; see `hardware.py` docstring.)*
- [ ] Inline fuses on 12V lines.
- [ ] `logger.py` now writes the full schema (see `06_EXPERIMENT_PROTOCOL.md` §4): 6 temps, RH, fan PWM, fan power, timestamps.

### 2.3 Cartridge heater upgrade (Build §9 — 🔴 adult present for ALL of it)
The aquarium heater's 32°C thermostat cannot produce controlled thermal stress. This upgrade IS the experiment's heat source.
- [ ] Cartridge heater seated in aluminum block with thermal paste, fully submerged.
- [ ] Heater driven by standalone PID controller + SSR — **the Pi never switches mains.** The PID box holds heater power at commanded wattage; the Pi only *reads*.
- [ ] Independent thermal cutoff set at 55°C fluid temp (hard safety ceiling; experiments cap at 45°C).
- [ ] E-stop switch kills heater circuit; tested.
- [ ] 🔴 Full commissioning test with adult: step to 100W for 10 min, verify controlled rise, verify e-stop, verify cutoff logic, safe shutdown order.
- [ ] Workload emulation verified: heater PID setpoint can be stepped (e.g., 60W → 140W → 60W) to imitate bursty AI load. **(Burst level is 140 W — under the 150 W cap in `hardware.py` and Form 3. The code's bursty profile already commands 140 W.)**

### 2.4 Sensor calibration (Software §6)
- [ ] Ice-bath check: all DS18B20 read 0.0 ± 0.5°C; record offsets.
- [ ] Room-temp cross-check: all probes agree within 0.3°C after offsets; offsets stored in `config.py`.

**PHASE 2 EXIT CONDITION:** one logged run showing a commanded heater step, fluid temp responding, fan PWM change visibly altering the cooling slope, all sensor columns populated, no leaks after 2 hours hot.

---

# PHASE 3 — MODEL + CONTROLLERS
**Dates: Aug 10 – Aug 30 (Weeks 6–8) | ~35 hrs (school starts ~Aug 19 — front-load)**
**Goal: calibrated physics model; PID, reactive MPC, forecast-MPC all running on the rig.**

### 3.1 Calibrate the lumped thermal model (Software §7)
The model: **C·dT/dt = Q_in − Q_out**, where Q_out = UA(fan) · (T_fluid − T_ambient).
- [ ] Run 3 heat-up curves at different fixed heater powers, 3 cool-down curves at different fan PWMs.
- [ ] Run `src/calibrate.py` to fit C and the UA-vs-PWM curve.
- [ ] 🔴 Validation gate: model predicts a held-out heat-up curve within ±1.5°C over 20 minutes. If not, the MPC will be garbage — fix the model (usual culprits: stratification → stir better; probe placement; UA nonlinearity → add a quadratic term).
- [ ] Record fitted C. Compare to the Phase 0 hand calculation — they should be within ~30%. Explain any gap in the notebook (components add mass; tank walls lose heat).
- [ ] Update `config.py` physics values (C_THERMAL, UA_MIN, UA_MAX, UA_EXP) with fitted numbers, in one commit labeled "calibration."

### 3.2 PID baseline (Software §8)
- [ ] `pid_controller.py` holds T_fluid at setpoint (38°C) by driving fan PWM. Tune conservatively (tutorial gives starting gains and a tuning recipe). **All sim-era tuning is provisional — retune against the real rig.**
- [ ] 30-min run under a step workload: stable, no oscillation worse than ±1°C.

### 3.3 Reactive MPC (Software §9)
- [ ] Understand the MPC tutorial BEFORE running code. You must be able to explain to a judge, in one minute, what the optimizer minimizes and subject to what. The explanation lives in the `mpc_controller.py` docstring ("THE PARAGRAPH") — rehearse it.
- [ ] `mpc_controller.py` (ReactiveMPC) running: uses calibrated model, 20-min horizon, assumes future ambient = current ambient (that's what makes it "reactive").
- [ ] Verify it behaves sanely on a step load (anticipates within its horizon, no actuator thrashing).

### 3.4 Forecast-aware MPC + banking (Software §10)
- [ ] ForecastMPC running: same optimizer, but future ambient/workload trajectories come from `profiles.py` (the synthetic climate/workload generator).
- [ ] Banking logic verified in a scripted test ON HARDWARE: given a forecast heat spike at t+15 min, the controller measurably pre-cools below setpoint BEFORE the spike. Save this plot — it is Figure 2 of every paper and the poster centerpiece. *(The sim version of this demo already exists: `py src/mpc_controller.py`.)*
- [ ] 🔴 Fairness rule check: all three controllers use identical actuator limits, identical safety constraints, identical sensor inputs. Any asymmetry invalidates the comparison. *(Enforced in `config.py`: FAN_MIN/FAN_MAX shared by all controllers.)*

### 3.5 Freeze the science
- [ ] Complete `01_PREREGISTRATION.md`: water-event trigger definition, hypotheses (including the criterion's predicted boundary from `05_CRITERION_WORKSHEET.md` §2–3), trial matrix, analysis plan. Sign it. Date it. Commit it to GitHub. **It does not change after this.**
  *(Status July 7: the metric values are already frozen in code — T_TRIGGER 42.0, FAN_SAT_WINDOW 60 s, HYSTERESIS 1.0 — and the doc template is committed. Katie fills the blanks, writes the justification in her own words, signs, commits. The criterion boundary (Π) may be finalized after calibration per the worksheet's two-stage design — state that explicitly in the doc. Do this BEFORE the first comparison trial at the latest; sooner is better.)*

**PHASE 3 EXIT CONDITION:** three controllers each complete a 30-min scripted trial hands-off; the pre-cooling demonstration plot exists; pre-registration committed.

---

# PHASE 4 — THE TRIAL GAUNTLET
**Dates: Aug 31 – Oct 4 (Weeks 9–13) | ~60 hrs, mostly weekends**
**Goal: the full comparison dataset. This phase is wall-clock bound and cannot be rushed by cleverness.**

Full procedure in `06_EXPERIMENT_PROTOCOL.md`. The matrix:

| Factor | Levels |
|---|---|
| Controller | PID, reactive MPC, forecast MPC |
| Climate profile (time-compressed) | mild, hot-dry, hot-humid, heat-wave |
| Workload | steady, bursty |
| Repeats | 3 (randomized order within blocks) |

Core matrix = 3 × 4 × 2 × 3 = **72 trials** @ ~50 min each (10 warm-up + 30 trial + 10 cooldown) ≈ 60 rig-hours, attended.
Then: banking-depth sweep (forecast-MPC only, 4 depths × 3 reps = 12 trials) and forecast-error trials (4 error levels × 2 climates × 3 reps = 24 trials) ≈ 30 more rig-hours.

- [ ] 🔴 Mains heater NEVER runs unattended. Sessions are attended blocks; automate everything except presence.
- [ ] Generate and freeze the randomized trial order before the first trial: `py src/profiles.py --shuffle <SEED>`. Print it, tape it in the notebook, follow it exactly.
- [ ] Weekend session template: 5–6 trials/day. School-night template: 1–2 trials.
- [ ] Before each session: run the 10-point pre-flight in Protocol §2 (also enforced interactively by `run_trial.py`).
- [ ] After each trial: CSV auto-saved, notes field filled (anomalies, ambient conditions), photo if anything odd.
- [ ] Analyze AS YOU GO (`py src/analyze.py data/raw/` after every session). A broken trial found in week 9 costs one re-run; found in week 14 it wrecks the schedule.
- [ ] Weekly GitHub commit of raw data. Raw files are never edited — corrections happen in processing scripts, visibly. **Hardware CSVs have no `sim_` prefix; that prefix is reserved for simulation output and the analysis must exclude `sim_*` files from hardware results.**

**Milestones:**
- [ ] Sept 13: core matrix ≥ 50% done.
- [ ] Sept 27: core matrix 100% done.
- [ ] Oct 4: banking-depth sweep + forecast-error trials done.

**PHASE 4 EXIT CONDITION:** ≥ 108 valid trials, raw data committed, session log complete, no unresolved anomalies.

---

# PHASE 5 — ANALYSIS + THE CRITERION
**Dates: Oct 5 – Oct 18 (Weeks 14–15) | ~25 hrs**
**Goal: figures, statistics, and the criterion tested against its pre-registered prediction.**

- [ ] Run full analysis pipeline (`analyze.py`): per-condition means, paired comparisons (Wilcoxon signed-rank for water events; report effect sizes + bootstrap 95% CIs — tutorial explains each in plain English).
- [ ] Produce the canonical figure set (Protocol §6): (1) architecture, (2) temperature trajectories with visible pre-cooling, (3) water-equivalent events by controller × climate, (4) forecast-error degradation curve, (5) Pareto frontier (water saved vs fan energy), (6) climate-sensitivity heatmap.
- [ ] 🔴 Criterion test (`05_CRITERION_WORKSHEET.md` §4): plot banking benefit vs the dimensionless number Π for every trial condition. Does the benefit "turn on" near the pre-registered boundary? Honest answer only — a partial match with explanation beats a forced fit.
- [ ] Scale-transfer simulation (Worksheet §5): run `thermal_sim.py` at data-center parameters (C ×10,000), same criterion, show where rig results do and don't extrapolate. This section is what elevates the paper.
- [ ] Write the Limitations list BEFORE the conclusions. Minimum entries: single rig, time-compressed climates, simulated water events, lumped model, small n per cell.

**PHASE 5 EXIT CONDITION:** all six figures exported at print quality; stats table complete; criterion verdict written (supported / partially supported / not supported, with numbers).

---

# PHASE 6 — MANUSCRIPT + PACKAGE
**Dates: Oct 19 – Nov 15 (Weeks 16–19) | ~35 hrs**
**Goal: the paper, the repo, the reusable assets. Competitions come after — see `07_COMPETITION_MAP.md` (write it at the start of this phase; deadline data verified July 7 2026: MIT THINK Jan 1 2027 · Conrad Innovation Stage ~Jan 8 2027 · Davidson ~mid-Feb 2027 · OCSEF submission ~late Feb 2027 · SJWP CA April 15 2027 · CJSJ window July–Sept 2027 · STS Nov 2027 · JEI/NHSJS/JHSS rolling · I-SWEEEP defunct · Spellman = ISEF special award, no separate entry).**

- [ ] Draft the paper in this order: Methods → Results → Discussion → Intro → Abstract. (Methods is easiest and builds momentum; the abstract is written last because it summarizes what now exists.) Target 15–20 pages, structure per Protocol §7.
- [ ] Claims audit: every sentence in Results traceable to a figure/table; every claim in the abstract hedged to exactly what the data shows ("we evaluate," "under tested conditions"). No "first ever."
- [ ] AI-assistance disclosure section drafted: software pipeline built with AI assistance as a disclosed instrument; bugs found/fixed in validation logged in git history; all physical work, data collection, justifications, and interpretations are the student's. Match wording to each venue's disclosure rules (Davidson explicitly screens for AI-generated text — the paper prose must be Katie's).
- [ ] Two external reads: one adult for clarity (Hayden), one technical if available (this is the Kammen follow-up email — send with Figure 2 + Figure 4 attached and two specific questions).
- [ ] GitHub repo public with: cleaned code, README with reproduction steps, BOM with prices, safety doc, the V1 build manual → this is simultaneously the Rise service artifact. **(Repo is already public — keep it clean as you go rather than cleaning at the end.)**
- [ ] 3-minute video: rig tour + one live trial replay (`py src/live_plot.py --file <trial>.csv --replay 20`). Phone + tripod is fine.
- [ ] JEI or NHSJS submission package prepared (their format), submitted by ~Dec 1. **(Decision point: JEI review runs 7–8 months — publication may miss fall-2027 applications; NHSJS reviews in weeks. Also: no simultaneous submission to multiple journals — pick one. JEI requires an adult senior mentor as last author; line that up before choosing JEI.)**
- [ ] Archive: freeze a `v1.0` release of the repo. This exact state is what every competition entry cites.

**PHASE 6 EXIT CONDITION:** manuscript complete and externally read; repo public; video done; journal submission out. **The research is finished. Everything after this is packaging — open `07_COMPETITION_MAP.md`.**

---

## SCHEDULE RISK TABLE (check weekly)

| Risk | Early warning sign | Response |
|---|---|---|
| Parts delayed | Not all Tier A arrived by July 14 | Reorder critical-path items (probes, pump) from a second seller immediately; keep building software |
| SRC approval slow | No reply by July 20 | Adult Sponsor calls OCSEF directly; do NOT heat-test while waiting — build, wire, simulate |
| Coast time wrong in practice | Phase 1 curves show <3 min coast | Add oil volume + aluminum mass; re-run 0.1 numbers; adjust profiles |
| Model won't validate | >±1.5°C error persists after fixes | Fall back: rule-based forecast controller replaces MPC-C (pre-registered fallback, still publishable) |
| School crushes weekday hours | <10 hrs logged in a school week | Shift all trials to weekends; extend Phase 4 two weeks; Nov 30 finish still clears every deadline |
| A controller misbehaves mid-gauntlet | Anomalies clustering on one controller | STOP the gauntlet, fix, restart that controller's block from zero (partial blocks are not comparable) |

Two of these firing = finish ~Dec 15. Still clears OCSEF (Feb), SJWP (Apr), STS (Nov 2027). The plan bends; it doesn't break.

---

## WEEKLY RHYTHM (print this)
- [ ] Monday: 15-min plan — which checkboxes this week, which session days.
- [ ] Every work session: notebook entry (date, what, result, next).
- [ ] Friday: commit to GitHub; run analyze.py on any new data.
- [ ] Sunday: check this roadmap's phase milestones; update risk table.
