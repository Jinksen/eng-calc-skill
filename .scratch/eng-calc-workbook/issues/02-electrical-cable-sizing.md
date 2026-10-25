# 02 — Electrical reference build: cable sizing

**Delivers:** `example_cable_sizing.py` — a workbook for sizing an LV cable run with the cross-section and installation method picked from a database, checks I_B ≤ I_n ≤ I_z·k, I_2 ≤ 1.45 I_z, ΔU ≤ ΔU_perm, k²S² ≥ I²t and the automatic disconnection condition; overview with KPIs and the utilisation chart.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** IEC 60364-5-52 (current-carrying capacity tables and correction factors — **copy the values from the standard, never estimate**), IEC 60364-4-43, -4-41; a worked example from a textbook / standard with a hand calculation.

- [ ] Database of I_z for the chosen installation method and insulation, with a source (table number)
- [ ] Correction factors for temperature and grouping as selections
- [ ] All checks and the TN/TT condition in the register
- [ ] Reference case matches ±1 %
- [ ] verify exit 0, render reviewed
