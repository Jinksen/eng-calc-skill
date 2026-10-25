# 01 — Live test in Claude in Excel

**Delivers:** proof that path A works without Python: Claude in Excel with the skill enabled builds the IPE beam check in an empty workbook (same brief as `example_ipe_beam.py`) and the result matches the reference build.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** `scripts/example_ipe_beam.py` (η_M = 0.84; η_w = 0.97 for IPE 240, S235, L = 6 m, g_k = 6, q_k = 5 kN/m).

- [ ] Skill uploaded and enabled, prompt "Build an IPE beam check with the eng-calc-workbook skill"
- [ ] Record what Claude in Excel can / cannot do: cell styles, named ranges, CF with formulas, data validation, charts (incl. a drawing chart), sheet protection, printing
- [ ] η_M and η_w ±0.01 against the reference; the banner reacts to L = 15 m (out of range)
- [ ] Differences reflected in `reference/excel-in-place.md` (table of substitutes)
