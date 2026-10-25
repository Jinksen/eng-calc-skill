# 11 — Complex numbers and a phasor diagram

**Delivers:** helpers `CalcSheet.complex_input(key, R, X)` and `phasor_chart()` + a reference build of an equivalent circuit (e.g. the T-circuit of an induction motor or the voltage drop on a line with R + jX): impedances, currents, powers P/Q/S and cos φ through the `IM*` functions, phasor diagram as a live sketch.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** textbook example of an equivalent circuit with a hand calculation; check P = Re(U·I*) against U·I·cos φ.

- [ ] Inputs R and X as numbers with data validation, the complex cell composed with `COMPLEX`
- [ ] Display magnitude + angle as numbers with units, not the text of the complex number
- [ ] Balance `check`: S² = P² + Q² (tolerance 1e-6)
- [ ] Only functions LibreOffice can read (no `_xlfn.IM…H`), verify exit 0
