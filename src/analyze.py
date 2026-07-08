"""
analyze.py — run after EVERY session:  python3 analyze.py ../data/raw/
Detects water events per the PRE-REGISTERED trigger, aggregates by condition,
runs paired stats, drafts figures. Analysis lives in code so every correction
is visible in git history — raw CSVs are never edited.
"""
import csv, glob, sys, os
from collections import defaultdict
import numpy as np

import config as cfg


def water_events(temps, fan_pwms, dt=1.0):
    """Pre-registered detector (01_PREREGISTRATION.md §1.1). Returns (count, total_s).
    Event begins: T > T_TRIGGER while fan pinned at 100% for >= FAN_SAT_WINDOW.
    Event ends:   T < T_TRIGGER - HYSTERESIS."""
    count, total, in_event, sat = 0, 0.0, False, 0.0
    for T, pwm in zip(temps, fan_pwms):
        sat = sat + dt if pwm >= 99.5 else 0.0
        if not in_event and T > cfg.T_TRIGGER and sat >= cfg.FAN_SAT_WINDOW:
            in_event, count = True, count + 1
        if in_event:
            total += dt
            if T < cfg.T_TRIGGER - cfg.HYSTERESIS:
                in_event = False
    return count, total


def load_trial(path):
    T, pwm, fan_w, meta = [], [], [], {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if r.get("T_tank_hot"):
                T.append(float(r["T_tank_hot"]))
                pwm.append(float(r["fan_pwm"] or 0))
                fan_w.append(float(r["fan_w"] or 0))
                meta = {k: r.get(k, "") for k in ("trial_id", "controller", "climate", "workload", "repeat")}
    return np.array(T), np.array(pwm), np.array(fan_w), meta


def bootstrap_ci(diffs, n=10000, seed=0):
    """Resample paired differences 10k times → honest 95% interval for the median."""
    rng = np.random.default_rng(seed)
    meds = [np.median(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(n)]
    return np.percentile(meds, [2.5, 97.5])


def main(folder):
    rows = []
    for path in sorted(glob.glob(os.path.join(folder, "*.csv"))):
        T, pwm, fw, meta = load_trial(path)
        if len(T) < 60:
            continue
        n_ev, dur = water_events(T, pwm)
        rows.append(dict(meta, events=n_ev, event_s=dur,
                         peak_T=float(T.max()), fan_Wh=float(np.sum(fw) / 3600.0)))

    # ---- summary table by controller x climate ----
    agg = defaultdict(list)
    for r in rows:
        agg[(r["controller"], r["climate"])].append(r["event_s"])
    print(f"{'controller':<14}{'climate':<11}{'n':>3}{'median event_s':>16}")
    for (c, cl), vals in sorted(agg.items()):
        print(f"{c:<14}{cl:<11}{len(vals):>3}{np.median(vals):>16.1f}")

    # ---- paired comparison: ForecastMPC vs PID on matched (climate, workload, repeat) ----
    key = lambda r: (r["climate"], r["workload"], r["repeat"])
   pid = {key(r): r["event_s"] for r in rows if r["controller"] == "pid"}
    fmp = {key(r): r["event_s"] for r in rows if r["controller"] == "forecast"}
    matched = sorted(set(pid) & set(fmp))
    if len(matched) >= 5:
        diffs = np.array([pid[k] - fmp[k] for k in matched])   # positive = forecast better
        try:
            from scipy.stats import wilcoxon
            stat, p = wilcoxon(diffs)
            print(f"\nWilcoxon (PID vs ForecastMPC, n={len(diffs)} pairs): p={p:.4f}")
        except ImportError:
            print("\n(scipy not installed — pip3 install scipy for the Wilcoxon test)")
        lo, hi = bootstrap_ci(diffs)
        print(f"median event-time saved: {np.median(diffs):.1f} s   95% CI [{lo:.1f}, {hi:.1f}]")
    else:
        print("\n(fewer than 5 matched pairs so far — stats activate as trials accumulate)")

    with open("summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["empty"])
        w.writeheader(); [w.writerow(r) for r in rows]
    print(f"\n{len(rows)} trials → summary.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../data/raw/")
