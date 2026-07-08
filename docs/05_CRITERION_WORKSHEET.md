# THE BANKING CRITERION — DERIVATION WORKSHEET
This is the deliverable that turns "my rig improved" into "here is a rule any engineer can use." Work through it with a pencil BEFORE trials; the prediction gets frozen into `01_PREREGISTRATION.md` H4. The sequence matters: **derive → predict → then test.** Done in that order it's science; done backwards it's curve-fitting.

---

## §1 THE THREE NUMBERS THAT RUN EVERYTHING (also your Phase 0 go/no-go)

**1. Thermal capacitance** — how much energy it takes to change your system's temperature:
> C = M·cp   [J/K]
Fill in: oil mass M = ____ kg × cp ≈ 1,900 J/kg·K (+ ~900 J/kg·K × aluminum mass) → C = ____ J/K

**2. Banked energy** — the buffer stored by pre-cooling ΔT_bank below setpoint:
> ΔE = C · ΔT_bank   [J]
At ΔT_bank = 3°C → ΔE = ____ J

**3. Coast time** — how long the buffer survives once cooling collapses:
> t_coast = ΔE / (Q_load − Q_reject,degraded)   [s]
With Q_load = ____ W and degraded rejection Q_reject ≈ ____ W → net = ____ W → **t_coast = ____ min**

**Go/no-go:** t_coast between ~5 and ~30 min → build as planned. Under 3 min → add oil/aluminum mass. Over 60 min → trials too slow; reduce mass or raise load. Chosen design point: M = ____ kg, Q_load,max = ____ W, t_coast(3°C) ≈ ____ min.

---

## §2 THE INSIGHT
Banking is a bet: *pay fan energy now to buy coast time later.* The bet pays only if the stress window you must survive is **shorter than the coast time you can bank** — and only if the forecast is accurate enough that you bank for real events, not phantom ones. Both conditions are ratios. Ratios of like quantities are dimensionless. Dimensionless numbers generalize across scale. That's the whole trick — it is exactly why Reynolds number lets a wind-tunnel model predict a real airplane.

## §3 THE TWO DIMENSIONLESS NUMBERS (derive, then predict)

**Π₁ — coverage ratio:**
> Π₁ = t_coast / t_stress = C·ΔT_bank / [(Q_load − Q_reject,degraded) · t_stress]
where t_stress = duration of the forecasted degraded-cooling window.
- Π₁ ≥ 1: the bank alone rides out the whole window → banking can fully substitute for water fallback.
- Π₁ ≈ 0.3–1: partial coverage → banking shortens, but may not eliminate, water events.
- Π₁ « 0.3: the bank is a rounding error → banking cannot help, no matter how smart the controller.
**Pre-registered prediction (write it):** banking benefit becomes material above Π₁ ≈ ____ (defensible default: 0.5) and saturates above Π₁ ≈ ____ (default: ~1.5 — banking deeper than the stress window wastes fan energy).

**Π₂ — forecast quality ratio:**
> Π₂ = σ_forecast / ΔT_bank
where σ_forecast = forecast temperature error (°C). When the forecast error is as large as the banking depth itself, the controller banks at the wrong times: it either misses real events or pre-cools for phantoms (burning fan energy).
**Pre-registered prediction:** forecast-MPC's advantage over reactive MPC collapses when Π₂ ≳ ____ (defensible default: ~0.5–1).

*(Optional third: Π₃ = t_forecast_horizon / t_coast — the forecast must see at least one coast-time ahead to be useful. On the rig this is satisfied by construction; note it, report it, move on.)*

## §4 HOW THE TRIALS TEST IT
Every trial condition in the matrix has computable Π₁ (from its climate profile's stress window and the fitted C) and Π₂ (from its forecast-error level). After the gauntlet:
1. For each condition, compute **banking benefit** = (PID water-event duration − forecast-MPC duration) / PID duration.
2. Scatter benefit vs Π₁ (color by climate). Overlay the pre-registered boundary as a vertical line.
3. Scatter forecast-MPC-minus-reactive-MPC benefit vs Π₂. Overlay the predicted collapse point.
4. Verdict language (pick honestly): *supported* (transition within ±50% of prediction) / *partially supported* (transition exists, location off — say by how much and hypothesize why) / *not supported* (no transition — report it; a clean negative on a pre-registered prediction is still publishable and still rare at this level).

## §5 SCALE TRANSFER (the section that answers "so what, it's a fish tank")
The criterion contains no rig-specific constants — only C, loads, durations, and errors. So:
1. In `thermal_sim.py`, set data-center-ish parameters: C ×10,000+ (tons of coolant), Q_load in the 100s of kW, real diurnal stress windows of 2–6 hours, real forecast errors (~1–2°C at 6h lead).
2. Compute Π₁, Π₂ for several real climate profiles (pull historical hot-humid days: Houston; hot-dry: Phoenix; mild: San Diego).
3. Show the simulation's banking benefit obeys the SAME Π₁/Π₂ map your hardware traced.
4. The claim you can then legitimately make: *"A benchtop system swept the dimensionless regime; the criterion it validated predicts full-scale behavior in simulation. Banking pays in climate X because Π₁ ≈ __, and cannot pay in climate Y because Π₁ ≈ __."*
This paragraph — small rig, law-like rule, named climates — is the one judges repeat to each other. It is also the honest version: you validated the *criterion* at small scale and the *extrapolation* in simulation, and you say exactly that.
