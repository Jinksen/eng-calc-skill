# 14 — Verification cases: expected vs. actual (sheet `85_Verification`)

**Delivers:** `book.verification_sheet()` — sheet `85_Verification` that holds independent reference cases: for each case a set of input values, the expected results with their source (worked example from a standard / textbook, closed-form solution, catalogue value) and tolerance, the actual results computed by the **same formulas** as the calc pad, deviation and ✔ / ✘. `verify.py --cases` substitutes each case into the inputs, recalculates, compares and restores the design inputs. Covers what lint and `--stress` (08) cannot: a wrong method, a missing term, a forgotten row (Panko: error checkers are blind to omissions; IStructE calculation-model guidance: test against known results).

**Blocked by:** Nothing — can start now (08 shares the input-substitution machinery — whichever lands first, the other reuses it).

**Status:** ready-for-agent

**Reference:**
- IPE beam: simply supported beam, M = q·L²/8, w = 5·q·L⁴/(384·E·I) — closed form, tolerance 0.1 %; section properties against the catalogue table, tolerance 0.5 %.
- Flange: ISO 286-2 limit deviations, e.g. Ø50 H7 = 0 / +25 µm, Ø50 f6 = −25 / −41 µm — exact match.

**How it works:**
- Case = one column (`Case 1 … n`), rows = named inputs and named results; input values typed in the case column, expected values with a source cell and tolerance (absolute or %).
- Actual values: path B by `verify.py --cases` (writes them in, timestamped); path A (Claude in Excel / no Python) by a variant column with the identical formula — same mechanism as 07, described in `excel-in-place.md`.
- Summary line "Verification n / n ✔" feeds the banner: any ✘ → ✘, cases not yet run since the last formula change → ▲.

- [ ] `verification_sheet()` in `engcalc.py`, register / banner aware
- [ ] `example_ipe_beam.py` has ≥ 2 cases, `example_flange.py` ≥ 2 cases, all ✔
- [ ] Breaking one formula on purpose (e.g. L²/8 → L²/10) turns the case ✘ and the banner ✘
- [ ] `verify.py --cases` restores the original inputs (file byte-identical apart from the actual-value column)
- [ ] `reference/specification.md` asks for reference cases in §1; `reference/review.md` treats "no verification case" as a finding for consequence class CC2 / CC3
