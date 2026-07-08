# SOFTWARE TUTORIALS — COOL-LOOP
From zero to running MPC. Do these in order. Every section ends with a checkpoint — do not continue past a failed checkpoint.

---

## §1 THE TERMINAL (30 min)
The terminal is a text window where you type commands instead of clicking. Everything on the Pi happens here.

On your laptop: Mac → Terminal app; Windows → install "Windows Terminal" + Python from python.org (check "Add to PATH" during install).

The only commands you need at first:
```
pwd          # print working directory — "where am I"
ls           # list files here
cd foldername   # move into a folder      cd ..  # move up one
mkdir name   # make a folder
python3 file.py   # run a Python file
```
**Checkpoint:** make a folder `coolloop`, `cd` into it, and confirm `pwd` shows it.

## §2 PYTHON CRASH COURSE (4–6 hrs, one sitting if possible)
Work through these seven ideas by TYPING them (not reading them). Create `practice.py`, run it after each addition with `python3 practice.py`.

1. **Variables:** `temp = 23.5`, `name = "T1"` — a labeled box holding a value.
2. **Lists:** `temps = [23.5, 24.1, 24.8]`; `temps[0]` is the first item; `temps.append(25.2)` adds one.
3. **Dictionaries:** `reading = {"T1": 23.5, "T2": 21.0}` — labeled boxes inside a box. This is how every sensor snapshot is stored.
4. **Loops:** `for t in temps: print(t)` — do a thing to each item.
5. **If:** `if temp > 42.0: print("water event")` — decisions.
6. **Functions:** 
```python
def c_to_f(c):
    return c * 9/5 + 32
```
A reusable machine: input in, output out. Every controller in this project is just a function: measurements in, fan command out.
7. **Files/CSV:**
```python
import csv
with open("log.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time", "T1", "T2"])
    w.writerow([0, 23.5, 21.0])
```
**Exercises (do all):** (a) function that returns the average of a list; (b) loop that prints "EVENT" whenever a value in a list exceeds 42; (c) write 10 fake readings to a CSV and open it in a spreadsheet app.
**Checkpoint:** all three exercises run without errors and you can explain each line out loud.

## §3 RUN THE SIMULATOR (1 hr)
`src/thermal_sim.py` is a fake rig — the same physics equation the real rig obeys, in software. It exists so every controller gets debugged safely before touching hardware, and later so you can simulate a data-center-sized system.

```
cd src
pip3 install numpy matplotlib     # (on Pi later: add --break-system-packages)
python3 thermal_sim.py
```
It prints a table and saves `sim_output.png`. Open the image: heater turns on, T_fluid climbs, fan fights back.
**Checkpoint:** you changed `HEATER_W = 100` to `150` at the top of the file, re-ran it, and the curve climbed faster — and you can say why (more Q_in, same Q_out capacity).

## §4 PI SETUP (when hardware arrives, 1–2 hrs)
1. Raspberry Pi Imager on the laptop → Raspberry Pi OS (64-bit) → in settings (gear icon) set hostname `coolloop`, enable SSH, set username/password, add your WiFi. Flash the SD.
2. Boot the Pi. From the laptop terminal: `ssh katie@coolloop.local` — you are now typing commands *on the Pi* from your laptop. This is how all rig work happens (no monitor needed at the bench).
3. `sudo apt update && sudo apt install -y python3-pip git`
4. `pip3 install numpy matplotlib --break-system-packages`
5. Enable 1-Wire and I2C: `sudo raspi-config` → Interface Options.
6. `git clone <your repo URL>` so the code lives on the Pi and syncs through GitHub.
**Checkpoint:** from the laptop, SSH into the Pi and run `python3 --version`.

## §5 THE LOGGER (real data begins)
`src/logger.py` reads every sensor once per second and appends a row to a timestamped CSV. Two modes:
```
python3 logger.py --sim        # fake rig (works anywhere)
python3 logger.py              # real sensors (Pi only)
```
Read the file top to bottom once — every block is commented. The idea worth understanding: *the logger never controls anything.* Logging and controlling are separate programs so a controller crash never kills your data.
**Checkpoint:** 10 minutes of real T1/T2 data logged while you warm one probe in your hand; the CSV shows it.

## §6 CALIBRATION (Software side of Phase 2)
1. Ice bath: crushed ice + a little water, stir, wait 2 min, dip each probe → each should read 0.0 ± 0.5°C. Write each probe's offset (reading minus 0.0) into `config.py` → `SENSOR_OFFSETS`.
2. Room cross-check: bundle all probes together in still air 10 min → after offsets, spread ≤ 0.3°C.
**Why judges care:** "how do you know your sensors agree?" is a standard question; "±0.3°C after single-point calibration, offsets in version control" is a complete answer.

## §7 FIT THE THERMAL MODEL — `calibrate.py`
The whole rig obeys one equation: **C·dT/dt = Q_in − UA·(T_fluid − T_ambient)**.
- C: how much energy changes the temperature (J/K) — the "thermal inertia."
- Q_in: heater watts (you command this, so you know it).
- UA·(ΔT): heat escaping through the radiator; UA grows with fan speed.

The fitting trick, in plain English: during a heat-up with the fan OFF, UA is small, so the slope dT/dt ≈ Q_in/C → **the slope gives you C**. During cool-down with the heater OFF, the decay rate gives **UA at that fan speed**. Do cool-downs at 3 fan speeds → UA-vs-PWM curve.

Procedure: run the six curves listed in the roadmap Phase 3.1 (log with `logger.py`), then:
```
python3 calibrate.py data/raw/heatup_100w.csv --mode heatup --power 100
python3 calibrate.py data/raw/cooldown_pwm50.csv --mode cooldown
```
It prints fitted C and UA and saves overlay plots (model curve on top of data).
**Checkpoint (the gate):** predict a held-out heat-up within ±1.5°C over 20 min. If it fails: stir harder (stratification), check probe placement, or accept the tutorial's quadratic-UA option (flag in the file).

## §8 PID — `pid_controller.py`
PID is three reflexes summed into a fan command:
- **P**roportional: push harder the further you are from setpoint.
- **I**ntegral: if you've been off for a while, push harder still (kills steady offset).
- **D**erivative: if temperature is moving fast, brace early (damps overshoot).

Tuning recipe (conservative on purpose): start Kp=8, Ki=0.02, Kd=0. Run a workload step. Oscillating? Halve Kp. Sluggish with lasting offset? Nudge Ki up 50%. Stop when a step settles within ~2 min with ≤ ±1°C wobble. Log every attempt — the tuning history is a notebook page judges enjoy.
**Checkpoint:** 30-min stepped-load run, stable, saved plot.

## §9 REACTIVE MPC — `mpc_controller.py` (understand before running)
MPC in one paragraph, and this is the paragraph you say to judges: *"Every 30 seconds, the controller uses the calibrated physics model to simulate the next 20 minutes for many candidate fan plans, scores each plan on a cost function — water-event risk, fan energy, temperature-limit violations — picks the plan with the lowest cost, executes only its first step, then repeats with fresh measurements."* That's it. Plan, act once, re-plan. The re-planning is why model errors don't snowball.

Our implementation keeps the optimizer honest and explainable: instead of a black-box solver, it grid-searches candidate fan trajectories (coarse but transparent — and at a 30 s control step, plenty fast). "Reactive" means its forecast of the future ambient is just "same as right now."
**Checkpoint:** on the SIMULATOR first (`--sim`), then rig: a step load run where MPC visibly ramps the fan *before* temperature peaks (within its horizon) rather than after.

## §10 FORECAST-MPC + BANKING — `forecast_mpc.py`
Identical optimizer, one changed input: the future ambient/workload trajectory comes from `profiles.py` (the scripted climate), optionally corrupted with noise (the forecast-error experiments). Banking is not a separate module — it *emerges* from the cost function: when the forecast shows cheap-cooling-now / expensive-cooling-later, the lowest-cost plan naturally overcools early. There is also an explicit `BANK_DEPTH` parameter to force fixed depths for the sweep.
**Checkpoint (the money plot):** scripted heat-spike at t+15 min → forecast-MPC's fluid temp dips below setpoint BEFORE the spike; PID's does not. Save as `figures/banking_demo.png`.

## §11 PROFILES — `profiles.py`
Generates the time-compressed climates (mild / hot-dry / hot-humid / heat-wave), the workloads (steady / bursty), forecast-error corruption, and the seeded trial-order shuffle. Climate profiles modulate the *effective ambient* the controllers are told about and, for physical realism at rig scale, the trials rely on heater-side workload realism + the profile-fed model. The file's header explains exactly what is physically real vs scripted in a trial — read it, because a judge will probe this boundary and honesty here is a strength ("ambient stress is emulated through the model's boundary condition; workload heat is physically real").

## §12 ANALYSIS — `analyze.py`
Run after every session: `python3 analyze.py data/raw/`. It detects water events per the pre-registered trigger, aggregates by condition, runs the paired stats, and drafts the figures.
Plain-English stats used (and how to say them):
- **Wilcoxon signed-rank:** compares paired trials without assuming bell curves — right for small n.
- **Effect size (rank-biserial):** "how big is the difference," not just "is there one."
- **Bootstrap CI:** re-sample your own trials 10,000 times to see how much the result wobbles — an honest uncertainty bar for small experiments.
**Checkpoint:** after the first full weekend of trials, `analyze.py` produces a per-controller event-duration table and you can read it aloud correctly.
