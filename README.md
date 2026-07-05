# COOL-LOOP

Forecast-Aware Thermal Control Research Platform

## Overview

COOL-LOOP compares three cooling strategies for AI-inspired thermal systems:

- PID Controller
- Reactive MPC
- Forecast-Aware MPC

The project includes:

- Physics simulator
- Hardware abstraction layer
- Experiment runner
- Data logging
- Statistical analysis
- Raspberry Pi support

---

## Project Structure

```
COOL-LOOP
│
├── src/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── figures/
├── hardware/
├── paper/
├── safety/
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run the simulator

```bash
cd src
python thermal_sim.py
```

---

## Run a simulated experiment

```bash
python run_trial.py --controller forecast --climate hot_humid --workload bursty --rep 1 --sim
```

---

## Analyze trials

```bash
python analyze.py ../data/raw
```

---

## Controllers

- PID
- Reactive MPC
- Forecast MPC

---

## Hardware

Target platform:

- Raspberry Pi 5
- DS18B20 temperature sensors
- Arctic P12 PWM fan
- Cartridge heater
- INA219 power monitor
- BME280 temperature/humidity sensor

---

## License

Research prototype.