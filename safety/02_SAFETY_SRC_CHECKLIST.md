# SAFETY + SRC COMPLIANCE — COOL-LOOP
**Nothing in this project heats up until Section A is complete. No exceptions, including "just a quick test."**

---

## SECTION A — ISEF / OCSEF PAPERWORK (before ANY experimentation)

Why this matters: ISEF-affiliated fairs (OCSEF included) require certain approvals **before experimentation begins**. Forms are dated; SRCs check dates. Data collected before approval is unusable at the fair — the single most common way strong projects disqualify themselves. STS has its own (lighter) checklist, but doing ISEF-grade paperwork now satisfies both.

### A.1 People
- [ ] **Adult Sponsor** identified: a teacher/scientist who oversees the project overall. Best pick: an SMCHS science teacher (also becomes your fair contact and a future recommender). Name: ____________
- [ ] **Designated Supervisor** identified: the adult directly supervising hazardous steps (mains wiring, cartridge heater, hot-oil work). Can be Hayden or a parent with relevant competence. Name: ____________

### A.2 Forms (download current versions from societyforscience.org → ISEF forms)
- [ ] **Form 1** (Checklist for Adult Sponsor) — sponsor completes.
- [ ] **Form 1A** (Student Checklist) + **Research Plan attachment** — you complete. Research Plan template below.
- [ ] **Form 1B** (Approval Form) — signatures BEFORE experimentation. Date carefully.
- [ ] **Form 3** (Risk Assessment) — required because this project uses hazardous equipment (mains-powered heater, hot oil, rotating fan). List: mineral oil (slip/fire), mains electricity near fluid, surfaces to 55°C, SSR-switched heater. Mitigations: GFCI, wiring separation, thermal cutoffs, e-stop, adult supervision, containment tray. Designated Supervisor signs.
- [ ] Scan all signed forms → `/safety` in the repo + a cloud backup.
- [ ] Email OCSEF SRC: introduce project, attach Research Plan, ask their pre-approval procedure for summer-start projects. Keep the reply.

### A.3 Research Plan template (1–2 pages; required attachment to 1A)
1. **Rationale:** AI data-center cooling consumes vast water; controllers are reactive; question is whether forecast-driven pre-cooling reduces water-equivalent demand.
2. **Research questions / hypotheses:** copy H1–H5 from `01_PREREGISTRATION.md`.
3. **Methods:** benchtop mineral-oil immersion loop, 150W max cartridge heater under standalone PID with SSR and independent thermal cutoff, dry-cooling radiator with PWM fan, Raspberry Pi data acquisition (sensors only — Pi never switches mains), three-controller comparison, 108-trial matrix, time-compressed synthetic climate profiles.
4. **Risk analysis:** the hazards + mitigations from Form 3, plus supervision plan.
5. **Data analysis:** paired nonparametric comparisons, effect sizes, bootstrap CIs.
6. **Bibliography:** ≥ 5 sources (data-center water use, MPC basics, immersion cooling, WUE metrics, forecast-based building control).

### A.4 STS-specific notes (for Nov 2027)
- STS rules differ slightly from ISEF; keep every approval doc — STS asks for documentation of approvals with the application.
- STS requires *individual* work: no co-built trials, no splitting with another student. Katie builds, runs, and analyzes; adults supervise safety only. Log adult involvement honestly in the notebook — supervision is expected and disclosable; participation is not.

---

## SECTION B — PHYSICAL SAFETY SYSTEM (permanent rules)

### B.1 The two-worlds rule (memorize)
**MAINS world** (wall → GFCI → heater PID box → SSR → cartridge heater; and wall → GFCI → Pi's USB-C charger): adult-only, no exposed conductors, heater plugged in LAST, unplugged FIRST.
**LOW-VOLTAGE world** (12V PSU → fused terminal block → pump, fan, MOSFET board; Pi GPIO → sensors): safe to work on, but never touches the mains world. No shared wires, ever.

### B.2 Power-up order (every session)
1. Visual: oil level covers heater block + pump; tubing clamped; tray dry; no cables near fan.
2. 12V on → confirm pump swirl + fan spin.
3. Pi on → confirm all sensors reporting in logger.
4. GFCI test button → verify trip + reset.
5. Adult present → heater energized via PID box.
Shutdown = exact reverse. Heater dies first, pump/fan run 5 more minutes to carry heat out, Pi shuts down cleanly, 12V last.

### B.3 Instant-shutdown triggers (kill heater first, ask questions second)
Burning smell/smoke • oil on Pi/PSU/outlet • heater hissing or hard bubbling • pump silent with heater on • T_fluid past 45°C without controller response • anything painful to touch • GFCI trip.

### B.4 Cartridge-heater rules (Tier C)
- Heater element NEVER energized in air. Seated in the aluminum block, block submerged, then powered.
- The standalone PID controller + SSR is the ONLY thing switching heater power. The Pi reads temperatures and logs; it has no wire to the mains world.
- Independent thermal cutoff (separate from the PID box) set at 55°C. Test monthly by simulation (heat gun on its probe — adult present).
- E-stop mounted within arm's reach of the operator seat; tested at every session start (it's in the pre-flight).
- Max heater power for this project: 150W. The system is sized for it; more is scope creep with real risk.

### B.5 Hot-oil handling
- Oil ≤ 45°C in operation — warm, not scalding — but treat post-run oil as hot for 30 min.
- Tray + absorbent pads under everything. Oil-wet pads go in a sealed bag, not loose trash.
- Adding/removing components: heater off ≥ 15 min, oil verified < 35°C on the logger.

### B.6 Session pre-flight (print, laminate, tape to the bench)
- [ ] Tray dry, no residue
- [ ] Oil level at fill line
- [ ] All clamps finger-checked
- [ ] Probe wires clear of fan
- [ ] 12V fuses intact
- [ ] Pump swirl visible
- [ ] Fan spins at 30% PWM command
- [ ] All temp sensors reporting plausible values (within 2°C of each other at ambient)
- [ ] GFCI test/reset done
- [ ] E-stop tested
- [ ] Adult present & aware trial block is starting
