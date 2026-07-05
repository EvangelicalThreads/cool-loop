"""
mpc_controller.py — Controllers B and C.

THE PARAGRAPH (say this to judges, tutorial §9):
Every 30 seconds the controller uses the calibrated physics model to simulate the
next 20 minutes for many candidate fan plans, scores each plan with a cost function
(water-event risk + fan energy + temperature violations), picks the cheapest plan,
executes only its FIRST step, then repeats with fresh measurements. Plan, act once,
re-plan — the re-planning is why model error doesn't snowball.

Controller B (ReactiveMPC): assumes the future ambient = right now. MPC structure, no foresight.
Controller C (ForecastMPC): is HANDED the future ambient/workload trajectory (from
profiles.py, optionally noise-corrupted). Same optimizer, one changed input — so any
performance difference between B and C is attributable to the forecast itself. That
isolation IS research question Q3.

Banking emerges from the cost function: if the forecast shows cheap cooling now and
expensive cooling later, the cheapest plan overcools early. BANK_DEPTH can also force
fixed depths for the sweep (research question Q2).

Optimizer choice: transparent grid search over candidate fan trajectories rather than
a black-box solver — coarse, but you can explain every line of it at a poster, and at
a 30 s control step it is more than fast enough.
"""
import itertools
import numpy as np
import config as cfg
from thermal_sim import ua_of_fan


def simulate_plan(T0, fan_plan, heater_traj, ambient_traj, dt):
    """Roll the physics forward under one candidate plan. Returns temp trajectory."""
    T, out = T0, []
    for fan, q, amb in zip(fan_plan, heater_traj, ambient_traj):
        T = T + (q - ua_of_fan(fan) * (T - amb)) / cfg.C_THERMAL * dt
        out.append(T)
    return np.array(out)


def cost(temps, fan_plan, dt, bank_target=None):
    """Score one plan. Lower = better. Weights are part of the frozen design —
    record any change in the notebook BEFORE trials, never between controllers."""
    # 1) Water-event risk: heavy penalty per second above trigger
    water = np.sum(temps > cfg.T_TRIGGER) * dt * 10.0
    # 2) Fan energy proxy: fan power scales roughly with pwm^2 (fan affinity laws)
    energy = np.sum((np.array(fan_plan) / 100.0) ** 2) * dt * 0.02
    # 3) Safety: enormous penalty for approaching the experiment cap
    safety = np.sum(temps > cfg.T_EXPERIMENT_CAP - 1.0) * dt * 1000.0
    # 4) Optional banking-depth tracking (for the fixed-depth sweep)
    bank = 0.0
    if bank_target is not None:
        bank = np.mean((temps - bank_target) ** 2) * 0.05
    return water + energy + safety + bank


class ReactiveMPC:
    """Controller B. Future = 'same as now'."""
    forecast_aware = False

    def __init__(self):
        self.horizon_steps = int(cfg.MPC_HORIZON_S / cfg.CONTROL_DT)
        # Candidate plans: piecewise-constant fan levels over two half-horizons.
        levels = [0, 25, 50, 75, 100]
        self.plans = [np.array([a] * (self.horizon_steps // 2) + [b] * (self.horizon_steps - self.horizon_steps // 2))
                      for a, b in itertools.product(levels, levels)]

    def command(self, T_fluid, heater_now, ambient_now, forecast=None, bank_depth=None):
        heater_traj = np.full(self.horizon_steps, heater_now)      # naive future
        ambient_traj = np.full(self.horizon_steps, ambient_now)
        return self._optimize(T_fluid, heater_traj, ambient_traj, bank_depth)

    def _optimize(self, T0, heater_traj, ambient_traj, bank_depth):
        bank_target = cfg.SETPOINT - bank_depth if bank_depth else None
        best_pwm, best_cost = 50.0, float("inf")
        for plan in self.plans:
            temps = simulate_plan(T0, plan, heater_traj, ambient_traj, cfg.CONTROL_DT)
            c = cost(temps, plan, cfg.CONTROL_DT, bank_target)
            if c < best_cost:
                best_cost, best_pwm = c, plan[0]                   # execute FIRST step only
        return float(best_pwm)


class ForecastMPC(ReactiveMPC):
    """Controller C. Identical optimizer; the future comes from the profile."""
    forecast_aware = True

    def command(self, T_fluid, heater_now, ambient_now, forecast=None, bank_depth=None):
        if forecast is None:
            raise ValueError("ForecastMPC requires forecast={'heater': array, 'ambient': array}")
        h = self.horizon_steps
        return self._optimize(T_fluid,
                              np.asarray(forecast["heater"][:h]),
                              np.asarray(forecast["ambient"][:h]),
                              bank_depth)


if __name__ == "__main__":
    # THE MONEY DEMO (tutorial §10 checkpoint): heat spike arrives at t=15 min.
    # Forecast-MPC pre-cools BEFORE it; ReactiveMPC reacts after. Watch column 2.
    from thermal_sim import step
    steps = int(cfg.MPC_HORIZON_S / cfg.CONTROL_DT)
    sim_min = 40
    n = sim_min * 60

    def heater_at(sec):   # bursty spike: 60 W baseline, 180 W between minutes 15-25
        return 180.0 if 900 <= sec < 1500 else 60.0

    for Ctl, label in [(ReactiveMPC, "REACTIVE"), (ForecastMPC, "FORECAST")]:
        ctl, T, fan = Ctl(), 36.0, 40.0
        print(f"\n--- {label} MPC ---\nmin   T_fluid   fan%")
        for i in range(n):
            if i % int(cfg.CONTROL_DT) == 0:
                fc = None
                if ctl.forecast_aware:
                    future = [i + k * int(cfg.CONTROL_DT) for k in range(steps)]
                    fc = {"heater": [heater_at(s) for s in future],
                          "ambient": [25.0] * steps}
                fan = ctl.command(T, heater_at(i), 25.0, forecast=fc)
            T = step(T, heater_at(i), fan, 25.0)
            if i % 180 == 0:
                print(f"{i/60:4.0f}   {T:6.2f}   {fan:5.1f}")
