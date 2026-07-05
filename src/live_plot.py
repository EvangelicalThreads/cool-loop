"""
live_plot.py — live view of the newest trial CSV. Run in a second terminal
during any trial (or after, on any saved file). This is also the fair-table
demo: replay a saved heat-wave trial with --replay and narrate the pre-cool.

  python3 live_plot.py                 # follow the newest file in ../data/raw/
  python3 live_plot.py --file X.csv    # follow/plot a specific file
  python3 live_plot.py --file X.csv --replay 20   # replay at 20x speed
"""
import argparse, csv, glob, os, time
import matplotlib
matplotlib.use("TkAgg" if os.environ.get("DISPLAY") else "Agg")
import matplotlib.pyplot as plt
import config as cfg


def newest():
    files = sorted(glob.glob("../data/raw/*.csv"), key=os.path.getmtime)
    if not files:
        raise SystemExit("no CSVs in ../data/raw/ yet")
    return files[-1]


def load(fname):
    t, T, fan, ev = [], [], [], []
    with open(fname) as f:
        for i, r in enumerate(csv.DictReader(f)):
            if r.get("T_tank_hot"):
                t.append(i / 60.0)
                T.append(float(r["T_tank_hot"]))
                fan.append(float(r["fan_pwm"] or 0))
                ev.append(int(r["water_event_flag"] or 0))
    return t, T, fan, ev


def draw(ax1, ax2, t, T, fan, ev, title):
    ax1.clear(); ax2.clear()
    ax1.plot(t, T, lw=2, label="T_fluid")
    ax1.axhline(cfg.SETPOINT, ls="--", c="gray", label="setpoint")
    ax1.axhline(cfg.T_TRIGGER, ls="--", c="red", label="water-event trigger")
    for i in range(1, len(ev)):
        if ev[i]:
            ax1.axvspan(t[i-1], t[i], color="red", alpha=0.12)
    ax1.set_ylabel("°C"); ax1.legend(loc="upper left"); ax1.set_title(title)
    ax2.plot(t, fan, lw=1.5, color="tab:blue")
    ax2.set_ylabel("fan %"); ax2.set_xlabel("minutes"); ax2.set_ylim(-5, 105)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None)
    ap.add_argument("--replay", type=float, default=0, help="replay speed multiplier")
    a = ap.parse_args()
    fname = a.file or newest()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    if a.replay:
        t, T, fan, ev = load(fname)
        for n in range(10, len(t), max(1, int(a.replay))):
            draw(ax1, ax2, t[:n], T[:n], fan[:n], ev[:n], os.path.basename(fname))
            plt.pause(0.05)
        plt.show()
    else:
        while True:
            t, T, fan, ev = load(fname)
            draw(ax1, ax2, t, T, fan, ev, os.path.basename(fname) + " (live)")
            if matplotlib.get_backend() == "Agg":
                plt.savefig("live.png", dpi=120)
                print(f"updated live.png  ({len(t)/60:.1f} min logged)")
            else:
                plt.pause(2)
            time.sleep(2)
