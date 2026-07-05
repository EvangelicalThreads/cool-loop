"""
run_trial.py — the experiment program. One command = one complete trial:
pre-flight prompt -> warm-up to start band -> 30-min controlled trial ->
cooldown -> CSV saved with the protocol's exact schema and filename.

REHEARSE FIRST (no hardware needed, runs anywhere, time-accelerated):
  python3 run_trial.py --controller forecast --climate hot_humid --workload bursty --rep 1 --sim

REAL TRIAL (Pi, adult present, pre-flight done):
  python3 run_trial.py --controller pid --climate mild --workload steady --rep 1

Full matrix comes from:  python3 profiles.py --shuffle <SEED>
Forecast-error trials:   add  --error-sigma 3.0
Banking-depth sweep:     add  --bank-depth 2.0
"""
import argparse, csv, os, sys, time
from datetime import datetime
import numpy as np

import config as cfg
import profiles
from hardware import Rig
from pid_controller import PID
from mpc_controller import ReactiveMPC, ForecastMPC

WARMUP_FAN, WARMUP_HEAT = 40.0, 60.0
COOLDOWN_TIMEOUT_S = 1800


def build_controller(name):
    return {"pid": PID(), "reactive": ReactiveMPC(),
            "forecast": ForecastMPC()}[name]


def water_event_live(T, fan, state):
    """Pre-registered detector, incremental version (mirrors analyze.py)."""
    state["sat"] = state.get("sat", 0) + 1 if fan >= 99.5 else 0
    if not state.get("in_ev") and T > cfg.T_TRIGGER and state["sat"] >= cfg.FAN_SAT_WINDOW:
        state["in_ev"] = True
    if state.get("in_ev") and T < cfg.T_TRIGGER - cfg.HYSTERESIS:
        state["in_ev"] = False
    return 1 if state.get("in_ev") else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controller", required=True, choices=["pid", "reactive", "forecast"])
    ap.add_argument("--climate", required=True, choices=list(profiles.CLIMATES))
    ap.add_argument("--workload", required=True, choices=["steady", "bursty"])
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--bank-depth", type=float, default=None)
    ap.add_argument("--error-sigma", type=float, default=0.0)
    ap.add_argument("--trial-min", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sim", action="store_true", help="simulated rig, accelerated time")
    a = ap.parse_args()

    trial_s = a.trial_min * 60
    trial_id = f"{a.controller}_{a.climate}_{a.workload}_r{a.rep}"
    fname = f"../data/raw/{trial_id}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    os.makedirs("../data/raw", exist_ok=True)

    # ---- profiles: reality vs what the forecast controller is TOLD --------
    amb_true, stress_s = profiles.climate_trace(a.climate, trial_s)
    heat_true = profiles.workload_trace(a.workload, trial_s, seed=a.seed + a.rep)
    amb_fc = profiles.corrupt_forecast(amb_true, a.error_sigma, seed=a.seed + a.rep)

    ctl = build_controller(a.controller)
    rig = Rig(sim=a.sim)
    tick = 0.0 if a.sim else 1.0          # sim runs as fast as the CPU allows

    # ---- pre-flight --------------------------------------------------------
    if not a.sim:
        print("PRE-FLIGHT (02_SAFETY B.6): tray dry / clamps / probes clear /")
        print("fuses / pump swirl / fan spins / sensors sane / GFCI / e-stop / adult present")
        if input("All checked? type YES: ").strip() != "YES":
            sys.exit("Aborted. Do the pre-flight.")

    cols = ["timestamp", "trial_id", "controller", "climate", "workload", "repeat",
            "T_tank_hot", "T_tank_mid", "T_rad_in", "T_rad_out", "T_ambient",
            "RH_ambient", "heater_w_cmd", "heater_w_meas", "fan_pwm", "fan_w",
            "forecast_T", "forecast_RH", "bank_depth_cmd", "water_event_flag", "notes"]
    f = open(fname, "w", newline="")
    w = csv.writer(f); w.writerow(cols)

    def log(phase, i, r, fc_T="", flag=0, note=""):
        w.writerow([datetime.now().isoformat(timespec="seconds"), trial_id,
                    a.controller, a.climate, a.workload, a.rep,
                    r.get("T_tank_hot",""), r.get("T_tank_mid",""), r.get("T_rad_in",""),
                    r.get("T_rad_out",""), r.get("T_ambient",""), r.get("RH_ambient",""),
                    r.get("heater_w_cmd",""), "", r.get("fan_pwm",""), r.get("fan_w",""),
                    fc_T, "", a.bank_depth or "", flag, note or phase])
        f.flush()

    try:
        # ---- WARM-UP: reach the start band so every trial begins equal ----
        print(f"[{trial_id}] warm-up to {cfg.START_BAND}...")
        rig.set_fan(WARMUP_FAN); rig.set_heater_watts(WARMUP_HEAT)
        t0 = time.time(); i = 0
        while True:
            r = rig.read(); T = r.get("T_tank_hot")
            log("warmup", i, r); i += 1
            if isinstance(T, float) and cfg.START_BAND[0] <= T <= cfg.START_BAND[1]:
                break
            if isinstance(T, float) and T > cfg.START_BAND[1]:
                rig.set_heater_watts(0)      # overshoot: coast down into band
            if not a.sim and time.time() - t0 > cfg.WARMUP_S * 3:
                sys.exit("Warm-up timeout — check heater/oil level.")
            if a.sim and i > 20000:
                sys.exit("Sim warm-up runaway — check config physics values.")
            time.sleep(tick)
        print(f"  in band at {T:.2f} C. TRIAL START ({a.trial_min} min).")

        # ---- TRIAL: hands off ---------------------------------------------
        ev_state, fan = {}, WARMUP_FAN
        steps = ctl.horizon_steps if hasattr(ctl, "horizon_steps") else 0
        for t in range(trial_s):
            rig.set_heater_watts(heat_true[t])              # physically real load
            if t % int(cfg.CONTROL_DT) == 0:                # controller decides
                r = rig.read(); T = r["T_tank_hot"]
                amb_now = amb_true[t]                       # model boundary condition
                if a.controller == "pid":
                    fan = ctl.command(T)
                elif a.controller == "reactive":
                    fan = ctl.command(T, heat_true[t], amb_now,
                                      bank_depth=a.bank_depth)
                else:
                    sl = slice(t, t + steps * int(cfg.CONTROL_DT), int(cfg.CONTROL_DT))
                    fc = {"heater": heat_true[sl], "ambient": amb_fc[sl]}
                    # pad if near end of trace
                    for k in fc:
                        if len(fc[k]) < steps:
                            fc[k] = np.pad(fc[k], (0, steps - len(fc[k])), mode="edge")
                    fan = ctl.command(T, heat_true[t], amb_now, forecast=fc,
                                      bank_depth=a.bank_depth)
                rig.set_fan(fan)
            r = rig.read()
            flag = water_event_live(r["T_tank_hot"], r["fan_pwm"], ev_state) \
                   if isinstance(r["T_tank_hot"], float) else 0
            log("trial", t, r, fc_T=round(float(amb_fc[t]), 2), flag=flag)
            if isinstance(r["T_tank_hot"], float) and r["T_tank_hot"] >= cfg.T_EXPERIMENT_CAP:
                log("trial", t, r, flag=flag, note="ABORT_cap_reached")
                print("SAFETY CAP HIT — aborting to cooldown."); break
            if t % 300 == 0:
                print(f"  t={t//60:3d}m T={r['T_tank_hot']:.2f} fan={r['fan_pwm']:.0f}% ev={flag}")
            time.sleep(tick)

        # ---- COOLDOWN ------------------------------------------------------
        print("cooldown...")
        rig.set_heater_watts(0); rig.set_fan(100)
        t0 = time.time(); i = 0
        while True:
            r = rig.read(); T = r.get("T_tank_hot")
            log("cooldown", i, r); i += 1
            if isinstance(T, float) and T < cfg.START_BAND[1]:
                break
            if (not a.sim and time.time() - t0 > COOLDOWN_TIMEOUT_S) or (a.sim and i > 20000):
                break
            time.sleep(tick)
        print(f"DONE. Saved {fname}")
        print("Now: fill the notes column if anything odd happened, and the paper session log.")
    finally:
        rig.kill(); f.close()


if __name__ == "__main__":
    main()
