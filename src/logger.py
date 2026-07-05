"""
logger.py — reads every sensor once per second and appends a CSV row. Nothing more.
Design principle: the logger NEVER controls anything. If a controller crashes,
the data survives, because data collection and control are separate programs.

Modes:
  python3 logger.py --sim              fake rig (runs on any laptop)
  python3 logger.py                    real sensors (Raspberry Pi)
Stop with Ctrl+C — the file is safe because we write line-by-line.
"""
import csv, sys, time, glob, random
from datetime import datetime
import config as cfg

SIM = "--sim" in sys.argv

# ----------------------------------------------------------------------
# Real-sensor readers (Pi only). Each returns °C or None on failure.
# ----------------------------------------------------------------------
def read_ds18b20(serial):
    """DS18B20 probes appear as files. Reading the file triggers a measurement."""
    try:
        with open(f"/sys/bus/w1/devices/{serial}/w1_slave") as f:
            raw = f.read()
        if "YES" not in raw:                       # CRC check failed — bad read
            return None
        t_milli = int(raw.split("t=")[-1])
        return t_milli / 1000.0                     # calibration offsets applied by name in main()
    except Exception:
        return None

def discover_probes():
    """List all 28-xxxx devices actually present — compare against config."""
    return [p.split("/")[-1] for p in glob.glob("/sys/bus/w1/devices/28-*")]

# ----------------------------------------------------------------------
# Simulated sensors: a little physics + noise, so the pipeline is testable
# ----------------------------------------------------------------------
class SimRig:
    def __init__(self):
        self.T = 30.0
    def sample(self):
        from thermal_sim import step
        self.T = step(self.T, heater_w=100.0, fan_pwm=50.0, t_ambient=25.0)
        n = lambda: random.gauss(0, 0.05)          # sensor noise
        return {"T_tank_hot": self.T + n(), "T_tank_mid": self.T - 0.3 + n(),
                "T_rad_in": self.T - 0.5 + n(), "T_rad_out": self.T - 3.0 + n(),
                "T_ambient": 25.0 + n(), "RH_ambient": 45.0 + n() * 10}

# ----------------------------------------------------------------------
def main():
    fname = datetime.now().strftime("data_%Y%m%d_%H%M%S.csv")
    cols = ["timestamp", "T_tank_hot", "T_tank_mid", "T_rad_in", "T_rad_out",
            "T_ambient", "RH_ambient", "heater_w_cmd", "fan_pwm", "fan_w", "notes"]
    sim = SimRig() if SIM else None
    if not SIM:
        found = discover_probes()
        print(f"Probes found: {found}")
        missing = [n for n, s in cfg.SENSOR_SERIALS.items() if s not in found]
        if missing:
            print(f"WARNING — configured but not found: {missing}")

    with open(fname, "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        print(f"Logging to {fname} at 1 Hz. Ctrl+C to stop.")
        while True:
            t0 = time.time()
            if SIM:
                r = sim.sample()
            else:
                r = {}
                for name, serial in cfg.SENSOR_SERIALS.items():
                    v = read_ds18b20(serial)
                    r[name] = round(v + cfg.SENSOR_OFFSETS[name], 3) if v is not None else ""
                r["RH_ambient"] = ""   # filled once BME280 wired (see tutorial §10.2)
            w.writerow([datetime.now().isoformat(timespec="seconds"),
                        r.get("T_tank_hot",""), r.get("T_tank_mid",""),
                        r.get("T_rad_in",""), r.get("T_rad_out",""),
                        r.get("T_ambient",""), r.get("RH_ambient",""),
                        "", "", "", ""])
            f.flush()                               # every row hits disk immediately
            time.sleep(max(0.0, 1.0 - (time.time() - t0)))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped. File is safe.")
