# 10 — Mechanical reference build: rolling bearing (from the canvas design)

**Delivers:** `example_bearing.py` — a workbook following the approved design "Bearing calculation – sheet design": bearing picked from a catalogue, interpolation of e/Y, X/Y branch, life L₁₀ₕ with a₁, static safety s₀, speed, minimum load, temperature; overview with the L₁₀ₕ(n) curve and a list of compliant bearings.

**Blocked by:** Nothing — can start now (work in the comments from the canvas first).

**Status:** ready-for-agent

**Reference:** ISO 281, ISO 76; check case 6206, F_r = 2 kN, F_a = 0.5 kN, n = 1450 min⁻¹ → P = 2.00 kN, L₁₀ = 1045.7 million rev., L₁₀ₕ = 12 019 h, s₀ = 5.60. Verify catalogue values against the manufacturer's current catalogue.

- [ ] `CalcSheet.interp()` — interpolation in a table with the `condition` "within table range" (compatible INDEX/MATCH)
- [ ] L₁₀ₕ(n) curve with the requirement line and the operating point
- [ ] Check case matches ±0.5 %
- [ ] verify exit 0, render matches the design
