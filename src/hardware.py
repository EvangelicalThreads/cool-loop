"""
hardware.py — the ONLY file that touches physical pins and buses.
Everything else (controllers, trial runner, analysis) talks to this layer,
so the same code runs in simulation on a laptop and for real on the Pi.

WIRING RECAP (matches 03_BUILD_TUTORIALS.md):
  DS18B20 probes  -> 3.3V / GND / GPIO4 (1-Wire bus, 4.7k pull-up)
  Fan (Arctic P12 4-pin): +12V and GND to the 12V supply;
      the fan's PWM control wire -> GPIO18 directly (3.3V logic is in spec).
      NOTE: with a 4-pin fan you do NOT need a MOSFET for the fan.
  DC cartridge heater (Tier C): 24V PSU -> fuse -> MOSFET board -> heater.
      MOSFET signal -> GPIO13. Grounds common (Pi GND to MOSFET GND).
  BME280 (ambient T/RH): 3.3V / GND / SDA=pin3 / SCL=pin5 (I2C addr 0x76/0x77)
  INA219 (fan power):    same I2C bus (addr 0x40), in series with fan +12V.

SAFETY DESIGN: heater duty can only be set through set_heater_watts(), which
clamps to MAX_HEATER_W and refuses if the last fluid reading exceeded the cap.
kill() zeroes both actuators; it runs on any crash via atexit.
"""
import atexit, glob, time
import config as cfg

MAX_HEATER_W = 150.0          # absolute ceiling; matches Form 3 risk assessment
FAN_PWM_HZ   = 25000          # Intel 4-pin fan spec (needs pigpio hardware PWM)
HEATER_PWM_HZ = 200           # fine for a resistive element through a MOSFET

# ---------------------------------------------------------------- detection
try:
    import pigpio
    _pi = pigpio.pi()
    ON_PI = _pi.connected
except Exception:
    _pi, ON_PI = None, False


class Rig:
    """One object = the whole physical rig. Use exactly one instance."""

    def __init__(self, sim=False):
        self.sim = sim or not ON_PI
        self._last_T = 25.0
        self._heater_w = 0.0
        self._fan_pct = 0.0
        if self.sim:
            from thermal_sim import step
            self._step = step
            self._sim_T = 31.0
            self._sim_amb = 25.0
        else:
            _pi.set_mode(cfg.PIN_FAN_PWM, pigpio.OUTPUT)
            _pi.set_mode(cfg.PIN_HEATER_PWM, pigpio.OUTPUT)
            self._probes = self._map_probes()
            self._bme = self._init_bme280()
            self._ina = self._init_ina219()
        atexit.register(self.kill)

    # ------------------------------------------------------------ actuators
    def set_fan(self, percent):
        """0-100. On hardware: 25 kHz hardware PWM on the fan's control wire."""
        p = max(cfg.FAN_MIN, min(cfg.FAN_MAX, float(percent)))
        self._fan_pct = p
        if not self.sim:
            _pi.hardware_PWM(cfg.PIN_FAN_PWM, FAN_PWM_HZ, int(p * 10000))

    def set_heater_watts(self, watts):
        """Commands heater power via MOSFET duty. Duty = watts / MAX (resistive
        element at fixed voltage: power scales ~linearly with duty)."""
        w = max(0.0, min(MAX_HEATER_W, float(watts)))
        if self._last_T >= cfg.T_EXPERIMENT_CAP:      # software safety gate
            w = 0.0
        self._heater_w = w
        if not self.sim:
            duty = int(w / MAX_HEATER_W * 1_000_000)
            _pi.hardware_PWM(cfg.PIN_HEATER_PWM, HEATER_PWM_HZ, duty)

    def kill(self):
        """Heater off, fan full (carry heat away). Safe in any state."""
        try:
            self._heater_w = 0.0
            if not self.sim:
                _pi.hardware_PWM(cfg.PIN_HEATER_PWM, HEATER_PWM_HZ, 0)
                _pi.hardware_PWM(cfg.PIN_FAN_PWM, FAN_PWM_HZ, 1_000_000)
        except Exception:
            pass

    # ------------------------------------------------------------- sensors
    def read(self):
        """One snapshot of everything. Missing sensors return ''.
        Keys match the data schema in 06_EXPERIMENT_PROTOCOL.md."""
        if self.sim:
            self._sim_T = self._step(self._sim_T, self._heater_w,
                                     self._fan_pct, self._sim_amb)
            self._last_T = self._sim_T
            return {"T_tank_hot": round(self._sim_T, 3),
                    "T_tank_mid": round(self._sim_T - 0.3, 3),
                    "T_rad_in":  round(self._sim_T - 0.5, 3),
                    "T_rad_out": round(self._sim_T - 3.0, 3),
                    "T_ambient": self._sim_amb, "RH_ambient": 45.0,
                    "heater_w_cmd": self._heater_w, "fan_pwm": self._fan_pct,
                    "fan_w": round(self._fan_pct * 0.02, 2)}
        out = {}
        for name, serial in cfg.SENSOR_SERIALS.items():
            v = self._read_ds18b20(serial)
            out[name] = round(v + cfg.SENSOR_OFFSETS[name], 3) if v is not None else ""
        if out.get("T_tank_hot") != "":
            self._last_T = out["T_tank_hot"]
        if self._bme:
            try:
                import bme280 as bmelib
                d = bmelib.sample(self._bus, self._bme_addr, self._bme)
                out["T_ambient"] = round(d.temperature, 2)
                out["RH_ambient"] = round(d.humidity, 1)
            except Exception:
                out.setdefault("T_ambient", ""); out.setdefault("RH_ambient", "")
        else:
            out.setdefault("T_ambient", ""); out.setdefault("RH_ambient", "")
        if self._ina:
            try:
                out["fan_w"] = round(self._ina.power() / 1000.0, 2)
            except Exception:
                out["fan_w"] = ""
        else:
            out["fan_w"] = ""
        out["heater_w_cmd"] = self._heater_w
        out["fan_pwm"] = self._fan_pct
        return out

    # ------------------------------------------------------ device helpers
    def _map_probes(self):
        found = [p.split("/")[-1] for p in glob.glob("/sys/bus/w1/devices/28-*")]
        configured = set(cfg.SENSOR_SERIALS.values())
        missing = configured - set(found)
        extra = set(found) - configured
        if missing:
            print(f"WARNING probes configured but absent: {missing}")
        if extra:
            print(f"NOTE unconfigured probes on bus (add to config.py): {extra}")
        return found

    def _read_ds18b20(self, serial):
        try:
            with open(f"/sys/bus/w1/devices/{serial}/w1_slave") as f:
                raw = f.read()
            if "YES" not in raw:
                return None
            return int(raw.split("t=")[-1]) / 1000.0
        except Exception:
            return None

    def _init_bme280(self):
        try:
            import smbus2, bme280 as bmelib
            self._bus = smbus2.SMBus(1)
            for addr in (0x76, 0x77):
                try:
                    params = bmelib.load_calibration_params(self._bus, addr)
                    self._bme_addr = addr
                    print(f"BME280 found at 0x{addr:02x}")
                    return params
                except Exception:
                    continue
        except Exception:
            pass
        print("BME280 not found (ok before Tier B).")
        return None

    def _init_ina219(self):
        try:
            from ina219 import INA219
            ina = INA219(shunt_ohms=0.1, address=0x40)
            ina.configure()
            print("INA219 found at 0x40")
            return ina
        except Exception:
            print("INA219 not found (ok before Tier B).")
            return None
