# Printable report sheet — style R (calculation report, data sheet)

A sheet meant to be **printed or exported to PDF** as an appendix to a technical report: the
calculation procedure with **substituted values**, data tables with totals, small sketches and
charts, a summary of the checks, and signatures. Its look comes from printable templates
(calculator / amortisation sheets): a coloured title band, label | value boxes, a highlighted
key result, striped tables, a total row.

| | Style K / P (calc sheet) | **Style R (report)** |
|---|---|---|
| Purpose | calculate, change inputs | print, hand over, sign |
| Content | inputs, logic, checks | **references only** (names from calc sheets), no inputs, no logic |
| Relations | relation as text, value in a cell | `symbol = relation = substituted numbers = result unit` |
| Grid | A–J calc pad | 12 equal columns B–M (8 characters each), A4 portrait |
| `engcalc.py` | `CalcSheet` | `ReportSheet` (`book.report_sheet`) |
| Sheet name | `1x_*` | `7x_*` (e.g. `70_Report`, `71_CableSchedule`) |

Use it when the user wants a "calculation report", "výpočtová zpráva", "printable", "PDF",
"data sheet", "schedule / list to print", or the workbook goes to a reviewer or an authority.
Build the calc sheets first; the report only reads from them.

## Anatomy (top to bottom)

1. **Title** 20 pt NAVY CAPITALS on the left, organisation on the right (field accent colour).
2. **Band** across the page (NAVY, white bold): subject. Rows 1–2 repeat on every printed page.
3. **Identification** in two boxes: Project · Calculation · Standard | Date · Revision ·
   Prepared by · Checked by (from `meta_*`).
4. **Input data** box on the left (label | grey value | unit), **sketch** on the right.
5. **Key result panel** (big number, three small tiles below) and **DESIGN STATUS** (✔ / ▲ / ✘
   from the check register) on the right, next to the material / section box.
6. **Calculation procedure** — numbered steps:

   ```
   1.2  Design bending moment                                    EN 1993-1-1, 6.2.5
        [rendered equation M_Ed = q_Ed·L²/8]          (optional)
        M_Ed = 16.01·6.00²/8 =                                      72.0  kNm
   1.7  Bending check                                               ✔ OK
        M_Ed ≤ M_c,Rd  →  72.0 ≤ 86.2 kNm                  η_M =   0.84
   ```

   Without an equation picture the line reads `M_Ed = q_Ed·L²/8 = 16.01·6.00²/8 = 72.0 kNm`.
7. **Data table** (striped rows, header band, **total row** with SUM / MAX…) on the left or
   across the page, live chart(s) next to it.
8. **Summary of checks** — every check and condition with inequality, η and status.
9. **Assumptions** a) b) c) in dark blue italics.
10. **Signatures**: Prepared by / Checked by / Approved by — name, line, "signature · date".

Footer from the shared page setup: `file | sheet | Page P / N`.

## Path B — `ReportSheet`

```python
from engcalc import Col, subst, xy_chart

rp = book.report_sheet("70_Report", "Calculation report", "purpose for the README")  # header + identification
rp.fields([("Span L", "=in_L", "m", "0.00"), ("Section", "=in_sec", "", "@")], title="Input data")  # at="left"
rp.figure(png, at="right", caption="Static scheme")          # small sketch, scaled to the half width
rp.panel("Maximum utilisation η", "=out_eta", "governing check", "0.00",
         tiles=[("M_Ed [kNm]", "=out_MEd", "0.0"), ("w [mm]", "=out_w", "0.0")])   # at="right"
rp.status()                                                    # DESIGN STATUS ✔ / ▲ / ✘

rp.section("Calculation procedure")                            # full width, numbered
rp.step("out_MEd", "Design bending moment", "M_Ed", "q_Ed·L²/8", "kNm", fmt="0.0",
        values="{calc_qEd}·{in_L}²/8", latex=r"M_{Ed}=\frac{q_{Ed}L^2}{8}", source="6.2.5")
rp.check_step("chk_M", "Bending check", "M_Ed ≤ M_c,Rd")

rp.table([Col("x", "x [m]", "0.00"), Col("M", "M [kNm]", "0.0")],
         [(f"=INDEX(gd_diag_x,{i})", f"=INDEX(gd_diag_M,{i})") for i in range(1, 22)],
         at="left", total={"M": "MAX"}, total_label="max")
rp.chart(xy_chart(…, width=9.5, height=6.0))                   # at="right"
rp.checks()                                                    # summary of all checks
rp.notes(["…", "…"])                                           # assumptions a) b) c)
rp.signatures()                                                # or [(role, name), …]
rp.page_break()                                                # optional: next block on a new page
rp.close()                                                     # print area, A4, rows 1–2 repeated
```

- **Flow**: `at="left"` (B–G) and `at="right"` (H–M) are two independent columns that fill
  downwards; `at="full"` starts below the longer of the two. Put a sketch / panel / chart on
  the right next to a box or table on the left.
- **`values`** is a template for `subst()`: `{name}` → `FIXED(name,2,TRUE)`, `{name:0}` sets
  the decimals, any expression works (`{calc_A*100:0}`). Write it with the same factors and
  unit conversions as the formula (`·10³`, `·10⁻⁶`), so a reader can repeat it on a calculator.
- `fields` rows are `(label, formula, unit, format)`; format `"@"` = text, left aligned.
- `table` `spans` divide the block width (6 or 12 columns), `fmt="@"` columns are left aligned.
- Everything is a formula reading a name — never type a number into the report.
- Reference build: `example_ipe_beam.py`, sheet `70_Report`.

## Path A — by hand / Claude in Excel

| Element | How |
|---|---|
| grid | 12 columns width 8, margins A and N width 1.5, gridlines off |
| title band | row 2 B–M fill NAVY, white bold, *Center Across Selection* (no merge) |
| label \| value box | label in the first cell, value cell grey `F2F2F2`, thin bottom line `D9D9D9`; numbers right aligned in the last-but-one column, unit in the last |
| substituted relation | `="M_Ed = q_Ed·L²/8 = "&FIXED(calc_qEd,2,TRUE)&"·"&FIXED(in_L,2,TRUE)&"²/8 ="` (`FIXED` does not depend on the locale, `TEXT` does); result `=out_MEd` in column L |
| equation picture | Insert → Equation, or a picture of the rendered equation above the substitution line |
| striped table | fill every other row `F2F6FC`, header fill `2E75B6` white bold, total row `D9E1F2` with a medium NAVY top line, `=MAX(…)` / `=SUM(…)` |
| status | `=` the banner formula (short form), conditional formatting ✔ green / ▲ amber / ✘ red |
| signatures | three boxes of 4 columns: role (7 pt grey), name, an empty 30 pt row with a bottom line |
| printing | Page Layout → Print Area, Print Titles rows `$1:$2`, A4 portrait, Fit to 1 page wide, margins ~1 cm, footer `&F | &A | Page &P / &N`; manual breaks with Page Break Preview |
| PDF | File → Export → PDF, "Active sheet" — the report is the only sheet that needs it |

## Rules

- The report never contains an input or a value that is not elsewhere in the workbook. A
  change in the calc sheet must show in the report without any edit.
- One step = one line of substitution. A longer derivation stays on the calc pad (style P);
  the report shows its result with a reference ("see 10_Beam, 3.4").
- Numbers in the substitution with the same decimals as the result; units only after the
  result (or in the brackets of a table header), never inside the substitution.
- Keep each block on one page (`page_break()` before a long table); a table taller than one
  page splits without a repeated header — split it into two tables instead.
- Sketches on the report are small (half width ≈ 9.5 cm) and only explain the scheme; the
  dimensioned drawing belongs to a `2x_` sheet ([part-drawing.md](part-drawing.md)).
- Verify the printed look: `verify.py --render` and look at the report pages (no `###`, nothing
  cut at the right margin, status coloured).
