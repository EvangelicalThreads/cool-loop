"""
thermal_sim.py — a fake rig in ~60 lines.

It obeys the SAME equation the real rig obeys:
        C * dT/dt = Q_in - UA(fan) * (T_fluid - T_ambient)
Read that aloud: "energy stored per second = heat coming in minus heat pushed out."
Everything in this project — calibration, PID, MPC, the criterion, the
scale-transfer study — is built on that one line.

Run it:   python3 thermal_sim.py
Try it:   change HEATER_W at the top, rerun, watch the curve change, explain why.
Scale-transfer mode (Phase 5): multiply C by 10,000+, stretch times, rerun.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")            # save images instead of opening windows (works over SSH)
import matplotlib.pyplot as plt
import config as cfg

HEATER_W  = 100.0    # watts of "GPU" load  <-- experiment with this
FAN_PWM   = 50.0     # constant fan for this demo
T_AMBIENT = 25.0     # °C room
SIM_MIN   = 60       # simulate one hour
DT        = 1.0      # 1-second physics steps


def ua_of_fan(pwm):
    """Heat-rejection coefficient as a function of fan speed (calibrated shape)."""
    frac = max(0.0, min(1.0, pwm / 100.0))
    return cfg.UA_MIN + (cfg.UA_MAX - cfg.UA_MIN) * frac ** cfg.UA_EXP


def step(T, heater_w, fan_pwm, t_ambient, dt=DT, C=cfg.C_THERMAL):
    """Advance the fluid temperature by one time step. THE core physics function —
    the simulator, the calibrator, and both MPCs all call this same logic."""
    q_out = ua_of_fan(fan_pwm) * (T - t_ambient)
    dT = (heater_w - q_out) / C * dt
    return T + dT


if __name__ == "__main__":
    T = 30.0                              # start temp
    n = int(SIM_MIN * 60 / DT)
    times, temps = [], []
    for i in range(n):
        T = step(T, HEATER_W, FAN_PWM, T_AMBIENT)
        times.append(i * DT / 60.0)       # minutes
        temps.append(T)
        if i % 600 == 0:
            print(f"t={times[-1]:5.1f} min   T_fluid={T:6.2f} °C")

    plt.figure(figsize=(8, 4.5))
    plt.plot(times, temps, lw=2)
    plt.axhline(cfg.SETPOINT, ls="--", c="gray", label=f"setpoint {cfg.SETPOINT}°C")
    plt.axhline(cfg.T_TRIGGER, ls="--", c="red", label=f"water-event trigger {cfg.T_TRIGGER}°C")
    plt.xlabel("time (min)"); plt.ylabel("T_fluid (°C)")
    plt.title(f"Simulated rig: {HEATER_W:.0f} W load, fan {FAN_PWM:.0f}%")
    plt.legend(); plt.tight_layout()
    plt.savefig("sim_output.png", dpi=150)
    print("\nSaved sim_output.png — open it. Where does the curve level off, and why?")
    # (Answer: equilibrium, where Q_in == Q_out. Solve for T and check yourself.)
