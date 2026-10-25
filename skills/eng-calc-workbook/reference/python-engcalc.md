# Path B — generated file (`scripts/engcalc.py`)

Python 3.10+, `openpyxl>=3.1`, `Pillow`; `matplotlib` for equations and sketches; LibreOffice +
`pdftoppm` for `verify.py`. Copy the library next to the build script or add `scripts/` to `sys.path`.

## Procedure

1. Turn the specification (SKILL.md §1) into a build script `build_<name>.py` modelled on
   `scripts/example_ipe_beam.py` (or `example_flange.py` for a part with a drawing) — order:
   databases → calculation sheets → chart / drawing data → drawing → overview → README.
2. `python build_<name>.py out/<name>_v1.0_YYYY-MM-DD.xlsx`
3. `python scripts/verify.py out/<file>.xlsx --render out/render` → exit 0
   (1 = lint warnings, 2 = error values), look at the PNG pages.
4. Give the user the `.xlsx` (and the build script, if they will regenerate the workbook).

## API

```python
from engcalc import (EngWorkbook, Meta, Col, index_match, interval_lookup, tol_text,
                     xy_chart, sketch_chart, drawing_chart, DrawSeries, png_from_figure, fx, let)

book = EngWorkbook(Meta(project=…, title=…, subject=…, author=…, date=dt.date(…),
                        organisation=…, standard=…, domain="electrical"))   # | mechanical | civil

db = book.data_sheet("90_Database", "Databases", "purpose for the README")
db.table("cable", [Col("key", "Size"), Col("Iz", "Iz [A]", "0")], rows, source="IEC … Tab. …")
#  → tbl_cable, db_cable_Iz, db_cable_key, lst_cable
db.close()

s = book.calc_sheet("10_Calc", "Sheet title", "purpose for the README")
s.section("Input data");  s.subsection("…");  s.comment("…")
s.input("in_L", "Length", "L", 25, "m", lo=1, hi=500)                 # range mandatory
s.input("in_cs", "Size", "S", "16", "mm²", choices="lst_cable")
s.const("c_rho", "Resistivity Cu", "ρ", 0.0175, "Ω·mm²/m", source="…", fmt="0.0000")
s.calc("calc_R", "Line resistance", "R", "c_rho*2*in_L/in_S", "Ω", text="R = ρ·2L/S", fmt="0.000")
s.result("out_dU", …)
s.check("chk_dU", "Voltage drop", "η_ΔU", value="out_dU", limit="in_dUmax", unit="%", kind="le", dec=2, source="…")
s.condition("chk_rng", "Validity of the formula", "calc_Re>4000", ok="turbulent", fail="out of range", source="…")
s.remark("Regime", 'IF(calc_Re>4000,"turbulent","laminar")')
s.equation(r"R=\rho\,\frac{2L}{S}")      # matplotlib mathtext → picture
s.figure(png_bytes, width_px=430);  s.chart(chart, rows=16)
s.close()                                 # mandatory: status CF, input span, printing

gd = book.data_sheet("91_ChartData", …)
blk = gd.block("diag", [Col("x", "x [m]"), Col("M", "M [kNm]")], [("=…", "=…"), …], note="relations")
d = book.dashboard("01_Overview", "Overview", "…")
d.kpis([("label", "=out_x", "unit", "0.0"), …]);  d.chart(xy_chart(…), "E13")
d.utilization_chart("B39");  d.figure(png, "B28", width_px=250);  d.close(52)

book.readme(purpose=…, scope=[…], assumptions=[…], workflow=[…], sources=[…], revisions=[(…)])
book.save(path)                           # orders sheets, builds register, utilisation charts, README, protection
```

### Printable report (see [report-sheet.md](report-sheet.md), reference `example_ipe_beam.py` → `70_Report`)

```python
rp = book.report_sheet("70_Report", "Calculation report", "…")      # title, band, identification
rp.fields([("Span L", "=in_L", "m", "0.00")], title="Input data");  rp.figure(png, at="right")
rp.panel("Max utilisation η", "=out_eta", "", "0.00", tiles=[("M_Ed [kNm]", "=out_MEd", "0.0")]);  rp.status()
rp.section("Calculation procedure")
rp.step("out_MEd", "Design bending moment", "M_Ed", "q_Ed·L²/8", "kNm", values="{calc_qEd}·{in_L}²/8", fmt="0.0")
rp.check_step("chk_M", "Bending check", "M_Ed ≤ M_c,Rd")
rp.table(cols, rows, at="left", total={"M": "MAX"});  rp.chart(chart);  rp.checks();  rp.notes([…]);  rp.signatures()
rp.close()
```

### Drawing toolkit (see [part-drawing.md](part-drawing.md), reference `example_flange.py`)

```python
interval_lookup("db_iso286_IT7", "db_iso286_key", "in_dbore")  # value for the size range ⟨prev ; upper]
tol_text("calc_ES_hole/1000", "c_EI/1000", 3)                  # '+0.021/0', '±0.10' for dimension texts

gd = book.data_sheet("92_DrawingData", "Drawing coordinates", "…")
outline = gd.block("um", [Col("x", "x"), Col("y", "y")], [("=calc_ox+0*calc_sc", "=…"), …])
hatch = gd.hatch("h_hub_u", x0, x1, y0, y1, spacing="c_hatch", side="lower")  # one series per rectangle

items = [DrawSeries(outline, "x", "y", "outline"), DrawSeries(hatch, "x", "y", "hatch"),
         DrawSeries(dim, "x", "y", "dim", label="'92_DrawingData'!$B$40", label_pos="l", vertical=True),
         DrawSeries(circle, "x", "y", "outline")]   # circles: 72 points, never smooth
dw = book.drawing_sheet("20_Drawing", "Drawing", "…")
dw.chart(drawing_chart(items, x_range=(0, 200), y_range=(-75, 75), width_cm=24), "B8")
dw.gdt_frame(row, col, "⊥", "=FIXED(in_gt_perp,2)", "A", "flange face")
dw.title_block(row, 2, [("Part", "Flange"), ("Scale", '=out_scale&""'), …])
dw.close(last_row)
```

Every quantity is written under a name; formulas use names. The library itself: gives the
`ec_link` style to formulas reading another sheet, numbers the steps, creates data validation,
status formulas, the register, banner, utilisation chart, legend and README contents, and
**refuses names that differ only in case** (Excel would treat them as one).

## openpyxl pitfalls (the library handles them, hand-written code does not)

| Problem | Fix |
|---|---|
| Excel 2010+ functions (`IFS`, `XLOOKUP`, `SHEET`, `TEXTJOIN`, `CONCAT`, `MAXIFS`…) → `#NAME?` | prefix `_xlfn.` — `fx()` adds it automatically |
| `LET` / `LAMBDA` | parameters with `_xlpm.` — helper `let({"a": "…"}, "{a}*2")`; LibreOffice < 24.8 cannot |
| Dynamic arrays (`FILTER`, `SORT`, `UNIQUE`, `SEQUENCE`) | openpyxl writes them as legacy array formulas → `fx()` raises; write them by hand in Excel |
| `XLOOKUP` in LibreOffice < 24.8 | `index_match()` works everywhere |
| Size-range lookup (`MATCH(...,1)` puts x on a bound into the wrong interval) | `interval_lookup()` with `COUNTIF(bounds,"<"&x)+1` |
| Names `in_D` and `in_d` | the same name in Excel → `define()` raises |
| `TEXT(x,"0.0")` depends on the locale | `FIXED(x,1)` |
| An empty text cell in a reference shows 0 | `=meta_x&""` |
| openpyxl does not compute formula values | `verify.py` (LibreOffice headless) |
| openpyxl cannot create shapes or form controls and **drops them** when it saves an existing file | drawings as XY charts (`drawing_chart`), never re-save a workbook with shapes through openpyxl |
| Data bar / CF extensions after a LibreOffice save | only a warning when reading, the result in Excel is fine |
| Images from `BytesIO` | keep the buffer open until `save()` (the library keeps a reference) |

## Extending the library

Add a new row or chart type as a `CalcSheet` method / function in `engcalc.py`, use it in
`example_ipe_beam.py`, `example_flange.py` (or a new reference build) and verify with
`verify.py` — a new element without a reference use has no place in the library.
