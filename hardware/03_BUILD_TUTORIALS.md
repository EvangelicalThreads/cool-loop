# BUILD TUTORIALS — COOL-LOOP HARDWARE
Written for someone who has never wired anything. Every step says WHAT to do and WHY it matters — the "why" is what you'll be asked at judging.

---

## §1 SHOPPING SPECS (Tier A — buy week 1)

| Item | Spec that matters | Why |
|---|---|---|
| Raspberry Pi 4 (2GB+) kit w/ SD + USB-C PSU | Any Pi 4/5 | Reads sensors, logs, runs controllers |
| 2× DS18B20 probes, waterproof | Genuine or reputable clone, 1m+ cable | Your T1/T2. Cheap fakes read erratically — buy from a known electronics seller |
| 4.7kΩ resistor, jumper wires (M-F and M-M), mini breadboard | any | The 1-Wire bus needs the pull-up |
| Food-grade mineral oil, 2L (buy 4L if tank allows) | "light" mineral oil, USP | Dielectric = won't short electronics. Food-grade = safe to handle |
| Clear heat-safe container ~3–4L | polypropylene (PP, recycle #5) or glass; rigid | PP handles 100°C+; flimsy PET warps. Taller > wider (submersion depth) |
| 50W submersible aquarium heater | thermostatic | V1-only heat source; replaced in Tier C |
| 12V DC brushless submersible pump | 240–400 L/h, oil-tolerant seals (check listing/Q&A) | Circulation. Brushless = no sparks in fluid |
| 120mm PC water-cooling radiator | G1/4 threads + barb fittings sized to your tubing | Dry-cooler analog |
| 120mm 12V case fan | 3-pin fine; 4-pin (PWM) is BETTER — buy 4-pin now, saves a Tier B purchase | Airflow |
| Silicone tubing + worm-gear hose clamps + barbs | ID matched to pump outlet (usually 8–10mm) | Silicone tolerates heat and oil |
| 12V 3–5A PSU + screw-terminal adapter | fused or short-protected | Powers pump + fan |
| GFCI plug adapter | UL-listed | Non-negotiable shock protection |
| Plastic tray + absorbent pads | tray larger than tank footprint | Leak containment |

**Tier B (week 4):** 4× DS18B20, BME280 breakout (I2C, 3.3V), IRLZ44N/logic-level MOSFET fan-driver board (or "PWM fan controller module, 12V, GPIO input"), INA219 breakout, inline blade-fuse holders + 3A/5A fuses.
**Tier C (week 4–5, after adult review):** aluminum block (or 40×40mm heatsink block) drilled for a **12V or 24V DC cartridge heater, 150W** *(preferred over mains cartridge — keeps the heater in the low-voltage world; needs a 24V 8A PSU)* — if only a 110V cartridge is available, then: standalone PID temperature controller (REX-C100-style kit with SSR + heatsink + thermocouple), independent thermal cutoff (bimetal 55°C snap switch in series), e-stop mushroom switch, Kill-A-Watt meter.
> **Design choice to make with your Designated Supervisor:** DC cartridge heater (simpler, safer, Pi-controllable via a second MOSFET — recommended) vs mains cartridge + PID/SSR (more "industrial," more paperwork, adult must do all wiring). The roadmap assumes either works; the safety doc's mains rules apply only if you choose mains.

---

## §2 TANK
1. Wash and fully dry the container (water + oil = cloudy mess).
2. Place on tray on a stable table, ≥ 1m from any outlet, Pi shelf ABOVE oil level (drips fall down, not sideways).
3. Fill to ~70% with oil. Mark the fill line with tape. **Why 70%:** heater block, pump, and tubing displace volume; you need headroom or day one ends with an oil floor.
4. Wipe the outside. Oil film migrates — recheck every session.

## §3 HEATER (V1 aquarium type)
1. Find the minimum-submersion mark on the heater. It stays below oil ALWAYS.
2. Clip to the tank wall, fully submerged, cord routed up and over. **Do not plug in.** A heater energized in air cracks its glass or starts a fire — this is the #1 beginner accident.

## §4 PUMP LOOP
1. Pump flat on the tank floor, fully submerged. **Why the bottom:** the intake must never gulp air; air-locked pumps run silent and move nothing.
2. Push tubing over the outlet barb; clamp it. Hand-tight + a quarter turn — cracking the barb is the failure mode, not looseness.
3. Route this HOT line up out of the tank toward where the radiator will sit.
4. Cut and stage the RETURN line (radiator → tank).

## §5 RADIATOR + FAN
1. Mount the radiator slightly ABOVE tank level (books/bracket). **Why:** gravity drains it back to the tank when the pump stops — no siphon surprises.
2. HOT line → radiator INLET (top port). Clamp.
3. Radiator OUTLET (bottom port) → return line → into the tank. Clamp.
4. Fan on the radiator face blowing THROUGH the fins (check the airflow arrow on the fan frame). Wrong direction = it still spins, cooling quietly doesn't happen — a classic "why is T2 not dropping" bug.

## §6 LEAK PROTOCOL
Run the pump on 12V for 10 minutes with dry paper towel wrapped at every joint. Any spot on the towel = power off, re-seat, re-clamp, re-test. Ten boring minutes here saves the Pi's life.

## §7 SENSORS + PI WIRING (V1: two probes)
The DS18B20 is a digital thermometer; many share ONE data wire (the "1-Wire" bus). Each has a unique serial number, which is how the Pi tells them apart.

1. **Pi OFF.** All wiring happens powered-down. Why: shorting 3.3V to ground with tweezers is instant; GPIO pins die quietly.
2. Both probe RED wires → breadboard rail → Pi pin 1 (3.3V). **3.3V, never 5V** — the data pin is not 5V-tolerant in this wiring.
3. Both BLACK → rail → Pi pin 6 (GND).
4. Both YELLOW (data) → one row → jumper to Pi pin 7 (GPIO4).
5. 4.7kΩ resistor bridging the data row to the 3.3V rail. **Why:** 1-Wire is "open-drain" — devices can only pull the line LOW; the resistor is what pulls it back HIGH. No resistor = no sensors found, the single most common wiring bug.
6. Boot the Pi → `sudo raspi-config` → Interface Options → 1-Wire → enable → reboot.
7. `ls /sys/bus/w1/devices/` → you should see two folders starting `28-`. Those are your probes. `cat /sys/bus/w1/devices/28-*/w1_slave` shows raw readings (t=23562 means 23.562°C).
8. Identify which is which: pinch one probe in your fingers, watch which reading rises. Label the cable with tape (T1/T2) and record serials in `src/config.py`.
9. Placement: T1 in the oil beside the heater. T2 taped TIGHTLY to the radiator outlet tube with foam or cloth over it (insulation makes it read tube temperature, not room air — loose tape here produces mystery data).

## §8 FIRST HEAT TEST (adult present)
Follow the power-up order in `02_SAFETY_SRC_CHECKLIST.md` B.2. Success = over 15 minutes, T1 climbs gently toward ~32°C and T2 tracks a few degrees below it. If T2 ≈ T1: check fan direction (§5.4), probe contact (§7.9), and confirm flow (drop a tiny paper speck on the oil surface — it should drift).

## §9 TIER C — REAL HEAT SOURCE (adult present for everything)
Recommended DC path:
1. Cartridge heater seated in the aluminum block with thermal paste; block sits on the tank floor near T1 (this is your "GPU").
2. 24V PSU → fuse → logic-level MOSFET board #2 → cartridge heater. MOSFET gate → Pi GPIO13. Now the Pi commands heater power by PWM, which means **workload profiles are software** — `profiles.py` drives real bursty heat.
3. Independent 55°C thermal snap-switch zip-tied to the block, wired in series with the heater supply. If everything else fails, this opens the circuit.
4. E-stop in series with the 24V line to the heater.
5. Commissioning (adult): command 40% power 10 min → verify smooth rise on T1 and INA-measured watts ≈ expected → test e-stop → test snap-switch (heat gun) → full shutdown order.
If mains cartridge instead: the standalone PID box + SSR does ALL switching, the adult does ALL wiring, the Pi only reads, and workload steps are made on the PID box per a printed schedule and logged manually.

## §10 TIER B — INSTRUMENTATION
1. **Extra DS18B20s:** same three rails; the bus takes all six probes. Placement: tank-mid (stratification check), radiator inlet, ambient air (hanging free, 30cm from rig), spare. Identify each by pinch-test; record serials.
2. **BME280 (I2C):** VIN→3.3V (pin 1 is taken — use pin 17), GND→pin 9, SCL→pin 5, SDA→pin 3. Enable I2C in raspi-config. `sudo i2cdetect -y 1` should show `76` or `77`.
3. **MOSFET fan board:** 12V in from terminal block, fan on the output, signal wire → GPIO18, grounds COMMON (Pi GND to board GND — forgetting the shared ground makes PWM do nothing; second-most-common bug).
4. **INA219 (I2C, address differs from BME):** wired in SERIES with the fan's 12V positive lead (V+ in, V− out). It measures voltage and current → power.
5. Fuses: 3A on the pump/fan branch, 5A on the heater branch (DC path).
