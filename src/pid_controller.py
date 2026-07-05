"""
pid_controller.py — Controller A: the reactive baseline.
Three reflexes summed into one fan command (tutorial §8):
  P: push harder the further from setpoint
  I: if you've been off a while, push harder still
  D: if temperature is moving fast, brace early
It knows nothing about the future. That ignorance is the point — it's the baseline
that forecast-MPC must beat under identical conditions.
"""
import config as cfg

class PID:
    def __init__(self, kp=8.0, ki=0.02, kd=0.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.integral = 0.0
        self.prev_err = None

    def command(self, T_fluid, dt=cfg.CONTROL_DT):
        """Input: current fluid temp. Output: fan PWM 0-100.
        Note the sign: hotter than setpoint → positive error → MORE fan."""
        err = T_fluid - cfg.SETPOINT
        self.integral += err * dt
        # Anti-windup: cap the integral so a long hot spell can't lock the fan at max
        # long after the problem passed. Without this, PID overshoots badly on recovery.
        self.integral = max(-500.0, min(500.0, self.integral))
        deriv = 0.0 if self.prev_err is None else (err - self.prev_err) / dt
        self.prev_err = err
        pwm = self.kp * err + self.ki * self.integral + self.kd * deriv
        return max(cfg.FAN_MIN, min(cfg.FAN_MAX, pwm))

if __name__ == "__main__":
    # Bench test on the simulator: step load at t=20 min, watch PID respond AFTER the fact.
    from thermal_sim import step
    pid = PID()
    T, fan = 32.0, 30.0
    print("min   T_fluid   fan%   heater_W")
    for i in range(3600):
        heater = 60.0 if i < 1200 else 150.0      # workload step at 20 min
        if i % int(cfg.CONTROL_DT) == 0:
            fan = pid.command(T, cfg.CONTROL_DT)
        T = step(T, heater, fan, t_ambient=25.0)
        if i % 300 == 0:
            print(f"{i/60:4.0f}   {T:6.2f}   {fan:5.1f}   {heater:5.0f}")
