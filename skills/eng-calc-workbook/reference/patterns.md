# Pattern catalogue

Patterns taken from reference calculation workbooks. Each pattern: when to use it and how to
build it in the language of this skill.

| # | Pattern | When | Build |
|---|---|---|---|
| P1 | **Sheet title block** (project, calculation, sheet x/y, date, prepared, checked) | always | visual-language.md, rows 1–4 from `meta_*` |
| P2 | **Colour instructions** in the row below the title block | always | row 6 |
| P3 | **Label with symbol**: "Pipe diameter, D =" | always | col. C description + col. D `D =` |
| P4 | **Dynamic remark**: "Re > 4000 → turbulent" | regime / branch of the calculation | `remark` + `condition` |
| P5 | **Input sketch** (plate, beam, brick with dimensions) | geometry of the inputs | static picture in the input section |
| P6 | **Live sketch from a chart** (truss, section, bolts) | geometry depending on inputs | coordinates in `91_ChartData` → XY chart, hidden axes, equal range |
| P7 | **Standard reference at the relation** ("ASCE 7-02 Eq. 4-1") | every relation from a standard | col. H |
| P8 | **YES / NO condition** ("A_T·K_LL > 400 ft² → YES") | validity switch | `condition` |
| P9 | **Sections Inputs / Intermediate / Result** with bars (dark header) | always | `section()` |
| P10 | **Formula as a picture** next to the calculation | key relations | `equation()` (B), col. G Unicode (A) |
| P11 | **FDM / time grid with a colour scale** (temperature in nodes × time) | explicit / implicit scheme, transients | block nodes × steps in `91_ChartData`, 3-colour scale (min blue – max red), profile chart; stability condition (e.g. Fo ≤ 0.5) as a `condition` |
| P12 | **Table Description \| Formula \| Value \| Unit \| Remark (OK, ≥ TDH)** | equipment sizing (pump, tank) | calc pad; remark = `check`/`condition` |
| P13 | **Several panels on one page** (section calculator, joint check, interaction diagram) | overview | `01_Overview`: KPI + sketch + capacity chart + utilisation |
| P14 | **Selection from a standard database** (W shapes, IPE, cables) | catalogue members | `table()` + `select` + `index_match` |
| P15 | **Capacity envelope + effect point** (N–M interaction diagram, safe region) | interaction of two effects | envelope = block of points, effect = 1-point series, `condition` "point inside" |
| P16 | **Iteration written out in rows** (Colebrook in C91:C100) | implicit equation | column of iterations x_{k+1}=g(x_k), 8–20 rows, `condition` \|x_n−x_{n−1}\| < tol; no circular references, no Goal Seek as a calculation step |
| P17 | **Manual Goal Seek** as an instruction | inverse problem | replace with P16 or a closed form; if impossible, procedure in the README + `condition` residual ≈ 0 |
| P18 | **Variants in columns** | sensitivity, comparing designs | inputs as rows × variants in columns E, F, G…, identical formula across the row, a check per column |
| P19 | **Revision table and operating instructions** (TCC) | handover | README |
| P20 | **Unit switch US/SI** | international use | selection `cfg_units` + conversion factors in the `02_` constants; calculation always in SI |
| P21 | **Parametric part drawing** (flange section with dimensions, tolerances, GD&T, title block) | a part whose dimensions are inputs | [part-drawing.md](part-drawing.md), `example_flange.py`: polygons in `92_DrawingData` → `drawing_chart`, dimension texts from cells |
| P22 | **Parameters / Output panel** with the formula next to the result | small calculators on the overview | [dashboard-widgets.md](dashboard-widgets.md) §1, `FORMULATEXT` |
| P23 | **Slider / spinner on an input** | sensitivity, tuning a design | `ui_*` cell → `in_*` with limit validation (desktop) |
| P24 | **Level gauge + digital display** | illustrative output (level, speed, pressure) | 1-point column chart with a gradient + large framed cell |
| P25 | **Flowchart from shapes** | calculation procedure on the README | shapes + connectors, steps linking to sheets |
| P26 | **LAMBDA as a named function** (`=ms(M15)`) | repeated conversion / relation | Name Manager, description in the README (365) |
| P27 | **Automatic drawing scale** | drawing that must fit the sheet for any input | largest standard scale (ISO 5455) ≤ the scale that fits: `INDEX(db_scale_f,MATCH(need,db_scale_f,1))`, scale into the title block |
| P28 | **Live hatching** | section views | `DataSheet.hatch()` — one series per rectangle, moves along visible edges |
