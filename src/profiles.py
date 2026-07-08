"""
profiles.py — the scripted world: climates, workloads, forecast error, trial order.

WHAT IS PHYSICALLY REAL vs SCRIPTED IN A TRIAL (judges will probe this — own it):
  REAL:     heater watts (actual joules into actual oil), fan response, all temperatures.
  SCRIPTED: the *ambient/climate stress* is emulated as the boundary condition the
            controllers are told about (time-compressed profile), because we cannot
            command the weather in a garage. The honest sentence: "workload heat is
            physically real; ambient stress enters through the model boundary condition."
Time compression: 1 profile 'hour' = PROFILE_MIN_PER_HOUR rig-minutes, chosen so the
stress-window duration is comparable to the rig's coast time (see criterion worksheet).
"""
import numpy as np

PROFILE_MIN_PER_HOUR = 6.0     # 6 rig-minutes per profile-hour → a 3h heat wave ≈ 18 min

# Each climate: (ambient °C baseline, stress amplitude, stress window profile-hours, RH%)
CLIMATES = {
    "mild":      dict(base=22.0, amp=3.0,  window_h=2.0, rh=50),
    "hot_dry":   dict(base=30.0, amp=8.0,  window_h=3.0, rh=20),
    "hot_humid": dict(base=28.0, amp=7.0,  window_h=3.0, rh=75),
    "heat_wave": dict(base=32.0, amp=12.0, window_h=4.0, rh=45),
}
# Humidity effect: high RH degrades effective heat rejection — we model it as an
# effective-ambient uplift (wet-bulb-flavored). Simple, stated, defensible.
RH_UPLIFT_PER_PCT = 0.06       # °C of effective ambient per % RH above 40


def climate_trace(name, trial_s=1800, dt=1.0):
    """Effective-ambient trajectory for one trial (time-compressed)."""
    c = CLIMATES[name]
    t = np.arange(0, trial_s, dt)
    window_s = c["window_h"] * PROFILE_MIN_PER_HOUR * 60
    center = trial_s * 0.55                          # stress arrives mid-trial
    stress = c["amp"] * np.exp(-((t - center) / (window_s / 2.355)) ** 2)  # gaussian window
    rh_up = max(0.0, (c["rh"] - 40)) * RH_UPLIFT_PER_PCT
    return c["base"] + rh_up + stress, window_s      # (trace, stress duration for Π₁)


def workload_trace(kind, trial_s=1800, dt=1.0, seed=0):
    """Heater-watts trajectory. THIS part is physically real on the rig."""
    t = np.arange(0, trial_s, dt)
    if kind == "steady":
        return np.full_like(t, 100.0)
    if kind == "bursty":
        rng = np.random.default_rng(seed)
        w = np.full_like(t, 60.0)
        for start in rng.choice(np.arange(120, trial_s - 300, 60), size=5, replace=False):
           w[int(start):int(start) + 180] = 140.0   # 3-min training bursts (under 150 W hardware cap)
        return w
    raise ValueError(kind)


def corrupt_forecast(trace, temp_sigma=0.0, seed=0):
    """Forecast-error experiments: the controller sees THIS, reality runs the clean trace."""
    rng = np.random.default_rng(seed)
    return trace + rng.normal(0, temp_sigma, size=len(trace))


def trial_order(seed):
    """The frozen randomized order for the core matrix. Print once, follow exactly."""
    import itertools, random
    cells = list(itertools.product(["pid", "reactive", "forecast"],
                                   CLIMATES.keys(), ["steady", "bursty"], [1, 2, 3]))
    random.Random(seed).shuffle(cells)
    return cells


if __name__ == "__main__":
    import sys
    if "--shuffle" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--shuffle") + 1])
        for i, c in enumerate(trial_order(seed), 1):
            print(f"{i:3d}  {c[0]:<12} {c[1]:<10} {c[2]:<7} rep{c[3]}")
    else:
        for name in CLIMATES:
            trace, w = climate_trace(name)
            print(f"{name:<10} peak_eff_ambient={trace.max():5.1f}°C  stress_window={w/60:4.1f} min")
        print("\nStress windows vs your coast time → compute Π₁ per climate (worksheet §3).")
