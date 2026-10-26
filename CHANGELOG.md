# Changelog

## 0.4.0 — 2026-10-26

- **Layout choice**: `reference/layouts.md` — catalogue with previews (S one-screen calculator,
  M mosaic of pages, K compact check sheet, V variants in columns, P calc pad, R report,
  D overview); SKILL.md §1 makes the layout a specification item the user picks.
- `ScreenSheet` (`book.screen_sheet`): one-screen calculator — inputs with ✔ / ✘, sketch,
  diagrams, key result, η with data bars and the live banner on one landscape page.
  `example_ipe_beam.py --screen` builds the same beam check with `02_Calculator`.
- `engcalc.py`: shared input validation `_bounded()`, report zones generalised, the register
  counts inputs out of range on any sheet / column.

## 0.3.0 — 2026-10-25

- **Everything in English**: skill, references, library texts written into workbooks
  (README sheet, legend, banner, register, statuses), reference builds, tickets, docs.
  Sheet names: `01_Overview`, `80_Checks`, `90_Database`, `91_ChartData`.
- **Reference build `example_flange.py`**: flange with hub — ISO 286 fit H7 / f6…p6,
  ISO 2768-1 general tolerances, worst-case and RSS tolerance chain, hole pattern and wall
  checks, position tolerance vs. fastener clearance, mass, automatic drawing scale (ISO 5455),
  live drawing (section A–A with hatching, view B with the bolt pattern, dimensions with
  tolerances linked to cells), GD&T frames and an ISO 7200 title block.
- `engcalc.py` drawing toolkit: `drawing_chart()` + `DrawSeries` (ISO 128 line types, arrowed
  dimension lines, dimension texts from cells, equal scale), `DataSheet.hatch()` (live hatching
  in one series per rectangle), `DrawingSheet` with `gdt_frame()` and `title_block()`,
  `interval_lookup()` for "over … up to" size ranges, `tol_text()` for dimension tolerances.
- `engcalc.define()` refuses names that differ only in case (`in_D` / `in_d` are one name in Excel).
- `verify.py`: scientific literals (`1e-6`) are no longer misread as the magic number `6`.
- Utilisation chart: the plot area leaves room for the title and axis title.
- New README with screenshots, badges and a quick start.
- **Printable calculation report (style R)**: `ReportSheet` (`book.report_sheet`) — title band,
  identification, label | value boxes, key result panel, DESIGN STATUS, numbered steps
  `symbol = relation = substituted values = result` (`subst()`), check steps, striped data tables
  with a total row, small sketches and charts side by side, summary of checks, assumptions,
  signatures, page breaks; `reference/report-sheet.md`; `example_ipe_beam.py` builds `70_Report`.

## 0.2.0 — 2026-10-25

- `SKILL.md`: "For the agent — what this is about" and a table of related skills the agent
  loads automatically (`xlsx`, `electrical-machine-calc`, `dataviz`, `freecad-qelectrotech`,
  `ilogic-inventor`, `pdf`); description extended with part visualisation and dashboards.
- `reference/part-drawing.md`: parametric part drawing / section in Excel — outline from
  dimensions, hatching, centre lines, dimensions with tolerances (ISO 286, ISO 2768), tolerance
  chain, GD&T (ISO 1101), title block (ISO 7200).
- `reference/dashboard-widgets.md`: Parameters / Output panels, sliders, spinners, option buttons,
  level gauge, digital display, scales, gradient charts, flowcharts from shapes; openpyxl limits on shapes.
- `excel-toolbox.md` §0: the engineer's core set (lookup, logic, statistics, bill of materials
  with `SUMIFS`, `RANK.EQ`/`PERCENTILE`, `CONVERT`, Bessel, complex numbers, bits, `ERF`, Solver).
- `patterns.md` P21–P26, `domains.md`: tolerances and fits, part from a drawing.
- Repository: a single copy of the skill in `skills/eng-calc-workbook/`;
  `.claude-plugin/marketplace.json` for installing through `/plugin`.

## 0.1.0 — 2026-10-25

- Merged the earlier skills `excel-design`, `python-openpyxl-engineering`, `vba-excel-engineering`.
- Visual language from reference engineering workbooks (title block, banner, calc pad, field accent).
- Three layers of conditions: inputs, checks η ✔/▲/✘ + validity conditions, banner; register sheet.
- Path A for Claude in Excel (native Excel only), path B `engcalc.py`, review, ticket mode.
- Reference build: IPE beam check (EN 1993-1-1), live section sketch, M(x), w(x), utilisation chart.
- `reference/excel-toolbox.md`: catalogue of Excel functions by task and version (lookup,
  interpolation, complex numbers, matrices, statistics, engineering functions, numerics, Power Query).
- `reference/sheet-styles.md`: compact TCC-style check sheet as the preferred main sheet;
  excel-toolbox §10–13 cell visuals, pictures in cells, shapes linked to cells, charts, inputs.
- `fx()`: `_xlfn.` prefixes also for Excel 2010+ statistical and Excel 2013+ functions.
- `verify.py`: LibreOffice recalculation, lint (magic numbers, volatile functions, inputs
  without validation, cross-sheet addresses), render.
