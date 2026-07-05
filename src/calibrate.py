"""
calibrate.py — fits the physics model to YOUR rig's data.

The trick in plain English (tutorial §7):
  HEAT-UP, fan off:  C*dT/dt = Q_in - (small loss)  →  slope ≈ Q_in/C  →  C
  COOL-DOWN, heater off:  C*dT/dt = -UA*(T - T_amb) → exponential decay → UA at that PWM

Usage:
  python3 calibrate.py ../data/raw/heatup_100w.csv --mode heatup --power 100
  python3 calibrate.py ../data/raw/cooldown_pwm50.csv --mode cooldown --pwm 50
Run all six curves from roadmap Phase 3.1, write fitted values into config.py,
then VALIDATE on a held-out curve (this file, --mode validate).
"""
import csv, sys
import numpy as np

def load(fname, col="T_tank_hot", amb_col="T_ambient"):
    t, T, A = [], [], []
    with open(fname) as f:
        rd = csv.DictReader(f)
        rows = [r for r in rd if r[col]]
        t0 = None
        for r in rows:
            from datetime import datetime
            ts = datetime.fromisoformat(r["timestamp"]).timestamp()
            t0 = t0 or ts
            t.append(ts - t0); T.append(float(r[col]))
            A.append(float(r[amb_col]) if r.get(amb_col) else 25.0)
    return np.array(t), np.array(T), np.array(A)

def fit_heatup(t, T, power_w):
    """Linear fit to the early, near-linear rise → slope → C = Q/slope."""
    mask = t < min(600, t[-1] * 0.5)               # first 10 min or first half
    slope = np.polyfit(t[mask], T[mask], 1)[0]     # °C per second
    C = power_w / slope
    print(f"heat-up slope = {slope*60:.3f} °C/min  →  C ≈ {C:,.0f} J/K")
    print("Compare to your hand calculation (M*cp). Within ~30%? Good. If not, investigate.")
    return C

def fit_cooldown(t, T, A, C):
    """Exponential decay: T-T_amb shrinks by factor e every tau=C/UA seconds.
    Fit log(T - T_amb) vs t; slope = -UA/C."""
    dT = T - A
    mask = dT > 0.5                                # ignore the noisy tail
    k = -np.polyfit(t[mask], np.log(dT[mask]), 1)[0]
    UA = k * C
    print(f"decay rate k = {k:.5f} /s  →  UA ≈ {UA:.2f} W/K at this fan setting")
    return UA

def validate(t, T, A, C, UA, power_w):
    """Simulate the run with fitted params; report worst error. Gate: ±1.5°C / 20 min."""
    Tsim = [T[0]]
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        q_out = UA * (Tsim[-1] - A[i])
        Tsim.append(Tsim[-1] + (power_w - q_out) / C * dt)
    err = np.max(np.abs(np.array(Tsim) - T))
    print(f"max model error over run: {err:.2f} °C  →  {'PASS' if err <= 1.5 else 'FAIL — see tutorial §7 fixes'}")

if __name__ == "__main__":
    fname = sys.argv[1]
    mode = sys.argv[sys.argv.index("--mode") + 1]
    t, T, A = load(fname)
    import config as cfg
    if mode == "heatup":
        p = float(sys.argv[sys.argv.index("--power") + 1])
        fit_heatup(t, T, p)
    elif mode == "cooldown":
        fit_cooldown(t, T, A, cfg.C_THERMAL)
    elif mode == "validate":
        p = float(sys.argv[sys.argv.index("--power") + 1])
        validate(t, T, A, cfg.C_THERMAL, cfg.UA_MAX, p)
