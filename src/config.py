"""
config.py — every tunable number in the project lives HERE and nowhere else.
Why: when a judge asks "what was your setpoint?", the answer is one file,
version-controlled, with history. Scattered magic numbers are how projects rot.
"""

# ---------- PHYSICS (update after calibration in Phase 3.1) ----------
C_THERMAL = 7600.0        # J/K  — thermal capacitance. Hand-calc first (M*cp), replace with fitted value.
UA_MIN    = 0.8           # W/K  — heat loss with fan OFF (natural convection). Fitted.
UA_MAX    = 6.0           # W/K  — heat rejection with fan at 100%. Fitted.
# UA(fan) modeled as: UA = UA_MIN + (UA_MAX-UA_MIN) * (pwm/100)**UA_EXP
UA_EXP    = 0.7           # fan effectiveness curve shape. Fitted.

# ---------- CONTROL ----------
SETPOINT      = 38.0      # °C — nominal fluid temperature target
CONTROL_DT    = 30.0      # s  — controller decision interval
MPC_HORIZON_S = 1200.0    # s  — 20-minute lookahead
FAN_MIN, FAN_MAX = 0.0, 100.0   # % PWM actuator limits (identical for ALL controllers — fairness rule)

# ---------- PRE-REGISTERED METRIC (copy from 01_PREREGISTRATION.md, then FREEZE) ----------
T_TRIGGER      = 42.0     # °C — water-equivalent event threshold
FAN_SAT_WINDOW = 60.0     # s  — fan must be pinned at 100% this long before events count
HYSTERESIS     = 1.0      # °C — event ends below T_TRIGGER - HYSTERESIS

# ---------- SAFETY ----------
T_EXPERIMENT_CAP = 45.0   # °C — software cap; controller sheds load / trial ends
T_HARDWARE_CUT   = 55.0   # °C — independent snap-switch (informational; hardware enforces it)

# ---------- TRIAL ----------
START_BAND = (30.0, 33.0) # °C — every trial starts inside this fluid-temp band
WARMUP_S, TRIAL_S, COOLDOWN_S = 600, 1800, 600

# ---------- SENSORS (fill during Build §7/§10; serials from /sys/bus/w1/devices) ----------
SENSOR_SERIALS = {
    "T_tank_hot": "28-XXXXXXXXXXXX",
    "T_tank_mid": "28-XXXXXXXXXXXX",
    "T_rad_in":   "28-XXXXXXXXXXXX",
    "T_rad_out":  "28-XXXXXXXXXXXX",
    "T_ambient":  "28-XXXXXXXXXXXX",
}
SENSOR_OFFSETS = {k: 0.0 for k in SENSOR_SERIALS}   # from ice-bath calibration (§6)

# ---------- PINS ----------
PIN_FAN_PWM    = 18       # GPIO for MOSFET fan board
PIN_HEATER_PWM = 13       # GPIO for DC cartridge-heater MOSFET (Tier C, DC path only)
