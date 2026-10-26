# 13 — verify: unit consistency (dimensional analysis)

**Delivers:** `verify.py --units` — parses the text in the unit column (col. F) of every calc pad row into an SI dimension and a scale factor (`kN·m` → M·L²·T⁻², ×10³), propagates dimensions through each formula by the named quantities it references and reports rows where the formula does not give the stated unit: adding kN to kN·m, a missing `/1000` between MPa·mm² and kN, a `check` whose value and limit differ in dimension. Catches the error class that Mathcad / SMath / CalcPad block by design and that Excel never sees.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** ISO 80000-1 (quantities and units, dimension of a quantity); SI Brochure, 9th ed. (prefixes, derived units).

**Rules:**
- Unit grammar: SI prefixes, `·` / `*`, `/`, `^n`, `²` `³`, `%`, `–` or empty = dimensionless, `°C`, `K`, `rad`, `°`, `‰`; unknown unit text → info finding, row skipped (never a false error).
- `+` `−` `MIN` `MAX` `IF` branches and comparisons need equal dimensions; `*` `/` combine; `^` only with a constant exponent; `SQRT` halves the exponents; `SIN` / `COS` / `EXP` / `LN` need a dimensionless argument.
- Allowed literals (`1000`, `1e6`, …) are dimensionless scale factors — the scale is checked, so `σ = F/A` with F in kN and A in mm² and no `*1000` gives "scale ×10⁻³ vs. MPa".
- Lookups (`INDEX` / `XLOOKUP` into `9x_` tables) take the unit from the table header row; no header unit → skip.
- Temperature: °C vs. K treated as equal dimension, a difference of two °C values is allowed, a sum is flagged.

- [ ] Unit parser with tests (≥ 40 unit strings incl. `kN·m/m`, `N/mm²`, `m³/h`, `kg·m²`, `W/(m·K)`)
- [ ] Deliberately broken fixture workbook (dimension mismatch, scale mismatch, check value vs. limit) → each one reported with sheet, row, formula and the two dimensions
- [ ] `example_ipe_beam.py` and `example_flange.py` pass with no unit finding
- [ ] Findings are `warn` (exit 1), unparsable units `info`; `--json` contains them
- [ ] `reference/review.md` and SKILL.md §6 list the new check; unit-string conventions written down once in `reference/visual-language.md`
