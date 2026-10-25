# 07 — Variants in columns

**Delivers:** `VariantSheet` — a calc pad with N variant columns (inputs as rows, identical formula across the row, check and status for every variant, best variant highlighted) — pattern P18, a substitute for the What-If Data Table that Claude in Excel does not support.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** IPE reference build: variants IPE 200 / 220 / 240 / 270 with the same load.

- [ ] Names per variant (`out_MEd_v1`…) or column names; record the decision in python-engcalc.md
- [ ] The register distinguishes the variant; the banner evaluates the selected variant
- [ ] verify lint checks formula consistency across a row
