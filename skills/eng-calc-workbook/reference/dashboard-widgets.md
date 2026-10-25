# Dashboard widgets and shapes

Interactive panels on `01_Overview` or next to the inputs: the user moves an input and sees
the gauge, chart and status immediately. The rules of the skill apply: a widget only **reads
or writes a named cell**, the calculation stays in formulas, statuses ✔/▲/✘ and the banner do
not change.

## 1. "Parameters / Output" panel

Small two-colour blocks: header `Parameters | Units` (NAVY / field accent, white font), rows
`quantity | value | unit`, below it a header `Output` and a row with the result and its formula
next to it (`FORMULATEXT`). The input cell has a **frame in the colour of its named range**
(matching how Excel colours references while editing a formula) — the reader pairs the input
with the formula. Names keep the skill convention: `in_h1`, `in_h2`, `out_v` (not `dash_h1_in`).

## 2. Form controls (desktop Excel)

| Control | Use | Link |
|---|---|---|
| **scroll bar** (Developer → Insert → Scroll Bar) | sensitivity to an input, smooth tuning | linked cell `ui_h1_raw` (integer 0–1000), input `=c_h1_min+ui_h1_raw*step` |
| **spinner** | stepping through a standard series | index into `lst_*` → `INDEX(lst_E12;ui_idx)` |
| **option button** | unit system, mode, variant | `ui_units` = 1/2 → `cfg_units = CHOOSE(ui_units;"SI";"US")` |
| **check box** / check box in a cell (365) | switch an effect on / off, YES/NO assumption | `condition` reads TRUE/FALSE |
| **combo box** | pick from a catalogue | prefer data validation with a list (works everywhere) |

Rules: the control writes into a `ui_*` cell; the real input `in_*` is computed from it and
**has limit validation** like every other input. Form controls do not work in Claude in Excel,
Excel for the web or openpyxl → there is always a plain input cell too, and the README says so.
No ActiveX.

**Unit switch**: calculation always in SI; display `=IF(cfg_units="SI";x;CONVERT(x;"m/s";"ft/s"))`
and unit `=IF(cfg_units="SI";"m/s";"ft/s")` (pattern P20).

## 3. Gauges

| Widget | Build |
|---|---|
| **tank level / fill column** | 1-point column chart, axis fixed 0–max, gradient fill (*Fill → Gradient*, light → `BLUE`), label "h₁ 41 m" from a cell; a second level (h₂, outlet) as an XY series with a horizontal line |
| **digital display** | one cell 24–28 pt bold, thick black frame, format `0.0`; above it a label with the unit `V (m/s)`; conditional formatting of the font colour by status |
| **speedometer / half-circle scale** | doughnut chart: 3 bands (✔ ▲ ✘ colours, the last half transparent) + a pie with a narrow slice as the needle from `chk_eta` |
| **thermometer / linear scale** | stacked bar chart: value + remainder to max, limit line as an XY series |
| **traffic light** | 3 circles (shapes) or cells with ●, colour by conditional formatting from the status |
| **KPI tiles** | see visual-language.md → Dashboard |

Gauge values are always named cells; axis and limits from `cfg_*`, not fixed in the chart.

## 4. Charts with a strong look

- **Area chart with a gradient** (e.g. two years of measurements on top of each other):
  *Fill → Gradient*, linear vertical, transparency 20–40 %, the older series behind. For
  technical x–y data always an XY chart; area charts only for categories (months, load cases).
- Derive gradient colours from the skill palette (`2E75B6`, `7030A0`…), not the default theme.
- Light plot background (`DEEBF7`), no 3D, axes with units.

## 5. Shapes and flowcharts (Insert → Shapes)

| Purpose | How |
|---|---|
| **flowchart of the calculation procedure** on the README | oval = start / end, rectangle = step (link to the sheet), diamond = decision (`condition`), arrows = connectors (*Lines → Connector*, snap to the shape's points) |
| idealised schematic (beam, supports, forces) | shapes + arrows, grouped; arrow text `=calc_F` |
| text linked to a cell | select the shape → formula bar `=out_v` (a single cell, not a formula) |
| switching visibility | not possible with formulas → two shapes + a conditionally formatted cell below them, or a macro (vba.md) |
| alignment | *Shape Format → Align / Distribute*, snap to grid, lock groups with sheet protection |

Path B: openpyxl **does not create shapes or form controls and drops existing ones when it
saves** — never open a workbook with shapes through openpyxl. Draw schematics as XY charts
(`drawing_chart`) or PNG (matplotlib), the procedure as a table of steps with hyperlinks; add
shapes in path A or with a macro.

## 6. Copyright and branding

A look copied from someone else's template (logo, © text, watermark) does not belong in the
workbook; use `meta_org`.
