# Excel tools — what to use for which task

Rule: use **the strongest function the target version offers** and write the minimum version
into the README (`Requires: Excel 365 / 2021 / 2016 / LibreOffice ≥ 24.8`). Find the target
version in the specification; if nobody says, assume Excel 365 and for every 365-only function
give a fallback for older versions in col. H.

Versions: **365** = Microsoft 365, **21** = Excel 2021/2024, **16** = Excel 2016/2019,
**LO** = LibreOffice Calc (24.2 / 24.8). ✔ = supported, ✘ = not supported.

## 0. The engineer's core set (quick overview)

The minimum the agent keeps in mind; details and versions in the sections below.

| Group | Functions | Typical use | § |
|---|---|---|---|
| lookup | `XLOOKUP`, `INDEX`+`MATCH` | material specs, part numbers, suppliers, sections from a catalogue | 1 |
| logic and errors | `IF`, `IFS`, `AND`, `OR`, `IFNA`, `IFERROR` (only with a reason) | model branches, trapping `#DIV/0!` as status "cannot evaluate" | 3 |
| summaries | `SUM`, `AVERAGE`, `MIN`, `MAX`, `STDEV.S` (sample) / `STDEV.P` (whole population) | measurement statistics, dataset summary | 6 |
| conditional sums | `SUMIFS`, `COUNTIFS`, `AVERAGEIFS`, `MAXIFS` | **bill of materials** (quantities and costs by part type), failure counts by cause | 6 |
| rank and distribution | `RANK.EQ`, `PERCENTRANK.INC`, `PERCENTILE.INC`, `QUARTILE.INC` | governing load case, strength quantile, worst variant | 6 |
| regression | `LINEST`, `TREND`, `RSQ` | curve fitting of tests, characteristics | 2, 6 |
| units | `CONVERT` | °F→°C, psi→Pa, ft→m — only at the boundary, calculation in SI | 7 |
| Bessel functions | `BESSELJ/Y/I/K` | heat conduction (fins), acoustics, skin effect | 7 |
| complex numbers | `COMPLEX`, `IMABS`, `IMCONJUGATE`, `IMSUM`, `IMPRODUCT` | AC circuits, phasors, vectors | 4 |
| bits and bases | `BIN2DEC`, `HEX2DEC`, `BITAND`, `BITOR` | MCU registers, protocols, status words | 7 |
| error function | `ERF`, `ERFC` | heat conduction in a half-space, probability | 7 |
| size ranges | `INDEX(values,COUNTIF(upper_bounds,"<"&x)+1)` | ISO 286, ISO 2768 and other "over … up to" tables | 2 |
| what-if | Goal Seek, Solver | inverse problem, optimisation (min. mass at a required load) — **design only**, the result is written as an input | 8, P17 |

## 1. Lookup, catalogues, databases

| Task | Function | 365 | 21 | 16 | LO |
|---|---|---|---|---|---|
| value from a catalogue by key | `XLOOKUP(key;db_x_key;db_x_C)` | ✔ | ✔ | ✘ | ≥24.8 |
| the same, compatible | `INDEX(db_x_C;MATCH(key;db_x_key;0))` | ✔ | ✔ | ✔ | ✔ |
| next higher standard value (section series, E12, breakers) | `XLOOKUP(x;series;series;;1)` / `INDEX(series;MATCH(TRUE;series>=x;0))` | ✔ | ✔ | ✔* | ✔ |
| all items that comply | `FILTER(tbl[Name];(cond1)*(cond2);"none complies")` | ✔ | ✔ | ✘ | ≥24.8 |
| sort a catalogue by utilisation | `SORTBY(tbl[Name];eta_column;1)` | ✔ | ✔ | ✘ | ≥24.8 |
| dependent dropdown | data validation with source `=FILTER(...)` through a named range | ✔ | ✔ | ✘ | — |
| table columns / rows | `CHOOSECOLS`, `TAKE`, `DROP`, `VSTACK`, `HSTACK` | ✔ | 24 | ✘ | ✘ |

`*` in 16 as an array formula. A catalogue is always an Excel table; structured references
`tbl_brg[C]` in table formulas, `db_*` names outside them.

## 2. Interpolation and approximation (tables from standards, characteristics)

| Task | Function |
|---|---|
| linear interpolation in a table | `LET(k;XMATCH(x;X;-1);FORECAST.LINEAR(x;INDEX(Y;k):INDEX(Y;k+1);INDEX(X;k):INDEX(X;k+1)))`; compatible: `MATCH(x;X;1)` and the line formula |
| bilinear interpolation (2D table) | linear twice via `INDEX` of row and column, or a `LAMBDA` `INTERP2` |
| size-range table ("over a up to b", x on a bound belongs to the lower range) | `INDEX(values;COUNTIF(upper_bounds;"<"&x)+1)` — `engcalc.interval_lookup()` |
| fitting a line / polynomial | `LINEST(y;x^{1,2,3};TRUE;TRUE)` (coefficients + R², standard errors), `TREND`, `SLOPE`, `INTERCEPT`, `RSQ`, `STEYX` |
| exponential / power law | `LOGEST`, `GROWTH`; linearise a power law with `LINEST(LN(y);LN(x))` |
| value outside the table range | **never extrapolate silently** → `condition` "x within table range" |

## 3. Logic, branches, readability

| Task | Function |
|---|---|
| calculation branches | `IFS`, `SWITCH` (bearing type → exponent, system TN/TT/IT → condition) |
| named intermediate results in one formula | `LET` (365/21, LO ≥ 24.8) |
| custom functions without VBA | `LAMBDA` saved in the Name Manager: `L10H = LAMBDA(C;P;p;n; 10^6*(C/P)^p/(60*n))` (365) |
| element-wise array calculation | `MAP`, `BYROW`, `BYCOL`, `MAKEARRAY`, `SCAN` (accumulation), `REDUCE` (365) |
| targeted error handling | `IFNA` on lookups; `IFERROR` only with a reason text, never blanket |
| choose a range by index | `INDEX(CHOOSE(k;range1;range2;…);row)` — tolerance field / class column |

## 4. Complex numbers (electrical: phasors, impedances, AC circuits)

A complex number in Excel is **text** `"3+4j"`; it is created and read with the `IM*`
functions (all versions and LibreOffice).

| Task | Function |
|---|---|
| creation | `COMPLEX(R;X;"j")`; from polar form `IMPRODUCT(abs;IMEXP(COMPLEX(0;RADIANS(φ);"j")))` |
| arithmetic | `IMSUM`, `IMSUB`, `IMPRODUCT`, `IMDIV`, `IMPOWER`, `IMSQRT`, `IMCONJUGATE` |
| magnitude and phase | `IMABS`, `DEGREES(IMARGUMENT(z))`, `IMREAL`, `IMAGINARY` |
| functions | `IMEXP`, `IMLN`, `IMSIN`, `IMCOS`, `IMSINH`, `IMCOSH`, `IMTAN` (from 2013; stored with `_xlfn.` — LibreOffice 24.2 cannot read such a file, `verify.py` then reports `#NAME?`, Excel is fine; for LO use `IMEXP`: sinh z = (e^z − e^−z)/2) |
| parallel impedance | `IMDIV(IMPRODUCT(Z1;Z2);IMSUM(Z1;Z2))` or a LAMBDA `ZPAR` |
| power | `S = IMPRODUCT(U;IMCONJUGATE(I))` → P = `IMREAL(S)`, Q = `IMAGINARY(S)`, cos φ = `P/IMABS(S)` |

Rules: show **magnitude and angle as numbers** (`IMABS`, `DEGREES(IMARGUMENT())`) with a
standard format and unit — the text of a complex number cannot be rounded by a format.
Enter inputs as R and X (two numeric cells with data validation) and compose the complex cell
from them. Phasor diagram = live sketch (XY chart from `IMREAL`/`IMAGINARY`).

## 5. Matrices and systems of equations

| Task | Function |
|---|---|
| system A·x = b (node voltages, truss, statics) | `MMULT(MINVERSE(A);b)` |
| determinant (singularity → `condition`) | `MDETERM(A)`; condition `ABS(MDETERM(A))>tol` |
| transformations (abc → dq0, coordinates) | `MMULT`, `TRANSPOSE`, `MUNIT` |
| complex system | `MMULT` cannot do complex → expand into a real 2n×2n system `[[R;−X];[X;R]]` |

A matrix always as a named range (`calc_A`); check its size with `ROWS`/`COLUMNS` in a `condition`.

## 6. Statistics and data analysis (measurements, tests, reliability)

| Task | Function / tool |
|---|---|
| describing a dataset | `AVERAGE`, `MEDIAN`, `STDEV.S`, `VAR.S`, `MIN`, `MAX`, `PERCENTILE.INC`, `QUARTILE.INC`, `COUNT` |
| sample vs. population | `STDEV.S` / `VAR.S` for a sample (tests, measurements), `STDEV.P` / `VAR.P` only for the complete population |
| confidence interval | `CONFIDENCE.T(α;s;n)`, `T.INV.2T(α;n−1)` |
| distributions | `NORM.DIST`, `NORM.INV`, `LOGNORM.DIST`, `WEIBULL.DIST` (bearing reliability, fatigue), `EXPON.DIST` (failure rate), `BINOM.DIST`, `POISSON.DIST` |
| tests | `T.TEST`, `F.TEST`, `CHISQ.TEST` |
| correlation and regression | `CORREL`, `LINEST` with full statistics, `FORECAST.LINEAR`, `TREND` |
| rank and position | `RANK.EQ` (governing load case), `PERCENTRANK.INC`, `LARGE`, `SMALL` |
| conditional aggregation | `SUMIFS`, `AVERAGEIFS`, `COUNTIFS`, `MAXIFS`, `MINIFS`, `AGGREGATE` (ignores errors and hidden rows) |
| bill of materials / cost roll-up | Excel table of parts + `SUMIFS(tbl[Qty]*…)` by type, `SUMPRODUCT(qty;unit_cost)` |
| histogram | `FREQUENCY` or `COUNTIFS` per bin + column chart; in 365 the Histogram chart |
| outliers | `condition` `ABS(x−mean) ≤ k·s` or quartile fences |
| import and cleaning of measurements | **Power Query** (CSV from an oscilloscope / DAQ → table, types, units), result as an Excel table |
| summaries | pivot table + slicers, pivot chart |
| spectrum, FFT | Analysis ToolPak → Fourier Analysis (desktop), or `=PY()` |
| regression with diagnostics | Analysis ToolPak → Regression (desktop); turn the result into `LINEST` formulas so it recalculates |
| Python in a cell | `=PY()` (Microsoft 365, where available): numpy/scipy for what formulas cannot do; always bring the result back into a named cell with a source |

## 7. Engineering and mathematical functions

| Task | Function |
|---|---|
| unit conversion | `CONVERT(x;"hr";"yr")`, `CONVERT(t;"C";"K")`, `CONVERT(p;"bar";"Pa")`, `CONVERT(P;"HP";"W")` — calculation always in SI, conversion at the boundary |
| error function (heat conduction, diffusion, noise) | `ERF`, `ERFC`, `ERF.PRECISE` |
| Bessel functions (skin effect, fins, membrane vibration) | `BESSELJ`, `BESSELY`, `BESSELI`, `BESSELK` |
| gamma and factorial | `GAMMA`, `GAMMALN.PRECISE`, `FACT`, `COMBIN` |
| angles | `RADIANS`, `DEGREES`, `PI()`, `ATAN2(x;y)` (note: order x, y) |
| step functions, tolerances | `DELTA`, `GESTEP`, `SIGN`, `ABS` |
| rounding to a series / manufacturing step | `MROUND`, `CEILING.MATH`, `FLOOR.MATH`, `ROUNDUP` (always to the safe side) |
| registers, protocols | `BIN2DEC`, `HEX2DEC`, `DEC2HEX`, `BITAND`, `BITOR`, `BITXOR`, `BITLSHIFT` |

## 8. Numerics without macros

| Task | Procedure |
|---|---|
| weighted sum, equivalent load | `SUMPRODUCT`: `P_eq = (SUMPRODUCT(P^3;q)/SUM(q))^(1/3)` |
| integral from a table (trapezoid) | `SUMPRODUCT((x2−x1)*(y1+y2)/2)` with shifted ranges; in 365 `DROP` |
| derivative from a table | central difference in a helper column |
| implicit equation (Colebrook, equilibrium) | iteration written out in rows + `condition` convergence ([patterns.md](patterns.md) P16) |
| series of points for a chart | `SEQUENCE(n;1;start;step)` (365) or a column `=start+(ROW()-r0)*step` |
| ODE / transient | explicit scheme in a grid + stability `condition` (P11) |
| optimisation | Solver only as a **design** tool, the result is written as an input; the calculation must not depend on Solver |
| tolerance stack-up | worst case `ΣT_i`, statistical `SQRT(SUMSQ(T))` (RSS) — `condition` on the assumption of a normal distribution |

## 9. Documentation and self-checking

| Task | Function |
|---|---|
| show the actual formula next to the value | `FORMULATEXT(E41)` (review, debugging, report appendix) |
| numbers in status texts | `FIXED(x;n)` (not `TEXT` — depends on the locale) |
| joining texts | `TEXTJOIN(", ";TRUE;range)`, `CONCAT` |
| symbols | `UNICHAR(8804)` ≤, `UNICHAR(951)` η, `UNICHAR(8730)` √ |
| links in the README | `HYPERLINK("#'10_Sheet'!A1";"10_Sheet")` |
| sheet number in the title block | `SHEET()`, `SHEETS()` |
| type checks | `ISNUMBER`, `ISTEXT`, `ISBLANK`, `ISFORMULA` (no input may be a formula and vice versa) |

## 10. Cell visuals — use everything Excel offers

The look is part of the calculation: the reader must see at a glance what is an input, what a
result and what fails. Formatting is done with **cell styles and rules**, not cell by cell.

| Element | Use |
|---|---|
| **cell styles** (Home → Cell Styles) | `ec_*` per [visual-language.md](visual-language.md) / [sheet-styles.md](sheet-styles.md); changing a style repaints the workbook |
| **workbook theme** (Page Layout → Themes) | theme colours and fonts = tokens; charts and shapes inherit them |
| **custom number format** | unit shown, value stays a number: `0.0" kN"`, `# ##0" h"`, `0.00" ‰"`; three sections `positive;negative;zero`; conditions `[<1]0.000;0.0`; colours `[Green]0.00;[Red]-0.00`; text `@" ✔"`; engineering notation `##0.0E+0`; fractions `# ?/?` |
| symbols and indices | in cell text *Format Cells → Superscript / Subscript* on selected characters, or Unicode (², ³, ⁻¹, ₀–₉, ᵣ, ₐ, η, σ, τ, γ, Δ, ≤, ≥, √, ·, ×, ⟨⟩, Ø, ±) |
| alignment | *Centre Across Selection* instead of merging; indent sub-levels; rotated text in narrow headers; *Wrap Text* only in notes |
| borders | thin under content rows, medium under headers, double above a total / result, frame around the result |
| **conditional formatting with formulas** | statuses ✔ ▲ ✘ (conditions.md), highlight the governing load case, grey font in an inactive branch of the calculation |
| **data bars** | η in the register and directly in the calc sheet (0–1.25, solid bar, red above 1 via a second rule) |
| **colour scales** | FDM grids, temperature maps, sensitivity matrices, catalogue tables by utilisation |
| **icon sets** | only with custom thresholds (≥ 1 ✘, ≥ 0.9 ▲, otherwise ✔) and always with text next to them |
| **sparklines** | a trend next to a number: L₁₀ₕ across load cases, temperature over time, η across variants |
| comments / notes | source or derivation of a constant (hover), not instead of the Source column |
| input message of data validation | unit and range when the input is clicked |
| hyperlinks | from the register to the check row, from the README to sheets, from a constant to the PDF of the standard |
| view | frozen panes under the title block, hidden gridlines, zoom 100 %, page layout for printing, named sheet views |

## 11. Pictures, shapes and sketches

| Element | Use |
|---|---|
| **picture in a cell** (`=IMAGE(url)` or Insert → Pictures → Place in Cell, 365) | icon of a member type in a catalogue, schematic of the variant chosen in a list — the picture changes with the selection: `=XLOOKUP(in_type;tbl_type[key];tbl_type[picture])` |
| picture over cells | input sketch next to the input section (PNG/SVG from CAD, matplotlib); *Format → Properties → Move but don't size with cells* |
| **SVG icons** (Insert → Icons) | symbols of loads, supports, statuses; colour from the theme |
| **shapes and groups** | idealised schematic (beam, supports, force arrows, dimensions); group, lock |
| **shape text linked to a cell** (select the shape, type `=calc_h` in the formula bar) | dimensions and force values in the sketch follow the inputs |
| **linked picture** (Copy → Paste Special → Linked Picture, *Camera*) | live snapshot of a result table on the overview or in a report |
| **live sketch from a chart** | XY scatter from coordinates computed from the inputs (section, truss, bolts, phasors) — hidden axes, equal x/y scale |
| **part drawing from a chart** | outline, hatching, centre lines, dimensions with tolerances, automatic scale — [part-drawing.md](part-drawing.md) |
| equation (Insert → Equation) | key relations in a text box next to the section; LaTeX-like syntax |
| SmartArt / flowchart | calculation procedure on the README ([dashboard-widgets.md](dashboard-widgets.md) §5) |
| watermark in the header | "DRAFT" until approved (picture in the page header) |

Pictures never carry numbers that are not calculated: every value in a sketch is linked to a cell.

## 12. Charts

| Element | Use |
|---|---|
| XY scatter | diagrams, characteristics, live sketches, drawings; never a line chart for x–y data |
| utilisation bar chart | colours by point, axis 0–125 %, 100 % line |
| combo chart, secondary axis | two quantities with different units (M and w) |
| error bars | measurement tolerance, ±η_warn band, limit line |
| area series under a curve | compliant region (n ≤ n_max), safe region of an interaction diagram |
| data labels from cells (*Value From Cells*) or the series name as a label | operating point, variant name, dimension texts (series name from a cell works in Excel and LibreOffice) |
| chart template (.crtx) | consistent look of all charts in the workbook |
| waterfall / histogram / box chart (365) | loss balance, distribution of measurements |
| dynamic range | chart data from an Excel table or named range, not fixed addresses |

## 13. Inputs and protection

| Element | Use |
|---|---|
| data validation | decimal min–max, list, custom formula (`=AND(ISNUMBER(E12);E12>0)`) + input message + Stop error alert |
| form controls (desktop) | check box, option button, spinner, scroll bar for sensitivity — linked to a cell; in Claude in Excel replaced by a list ([dashboard-widgets.md](dashboard-widgets.md) §2) |
| check boxes in cells (365) | YES/NO assumptions (Insert → Checkbox) |
| sheet protection | only inputs unlocked, no password; allow column formatting |
| scenario manager | named sets of inputs (load cases) — desktop |
| Goal Seek / data table | desktop, not in Claude in Excel; substitute: variants in columns (P18) |

When writing the file with openpyxl, `fx()` and `let()` from `engcalc.py` handle the
`_xlfn.`/`_xlpm.` prefixes; dynamic arrays (`FILTER`, `SORT`, `SEQUENCE`…) cannot be written
into the file — write them in Excel (path A) or leave an instruction in the README.
