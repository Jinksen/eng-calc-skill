---
name: eng-calc-workbook
description: >
  Engineering calculation workbooks in Excel (electrical, mechanical, civil): calculators,
  design checks, sizing, test reports or dashboards with pass / fail conditions, including
  visualisation inside the workbook — parametric part drawings and sections with dimensions
  and tolerances, live sketches, interactive dashboards (sliders, option buttons, gauges),
  shapes and diagrams. Use when the user creates, rebuilds or reviews an .xlsx with a
  technical calculation, wants to draw or visualise a part, cross-section, assembly or
  diagram in Excel, wants a printable calculation report / data sheet (formulas with
  substituted values, tables with totals, small sketches, signatures), asks how to lay out a calculation in Excel,
  builds catalogues / databases in a workbook (sections, cables, materials, registers) with
  dropdowns, dependent dropdowns and lookup functions, works directly in a workbook
  through Claude in Excel, or wants to split a larger calculation workbook into tickets.
  Also applies to LibreOffice Calc.
---

# Engineering calculation workbook

## For the agent — what this is about (read first)

- **Who and why**: the user is an engineer (electrical / mechanical / civil). They want
  workbooks that hold up as an appendix to a technical report: traceable inputs, sources from
  standards, visible checks, and **plenty of visuals** — part sketches and drawings, charts,
  controls.
- **What you deliver**: either changes directly in the open workbook (Claude in Excel) or an
  `.xlsx` generated with `scripts/engcalc.py`. Always verified (§6), with a hand check in your
  answer.
- **Language**: reply in the user's language and write the workbook in it too (sheet labels,
  README); the reference builds are in English. Standards EN / ISO (national editions such as
  ČSN EN are fine), SI units.
- **Visualisation is calculation**: every picture, shape, dimension or gauge is linked to a
  cell and follows the inputs. Part drawings → [reference/part-drawing.md](reference/part-drawing.md),
  dashboards with controls → [reference/dashboard-widgets.md](reference/dashboard-widgets.md).
- **Never guess**: a value from a standard without a source, extrapolation outside a table or
  an invented input is an error. Ask, or record it as an assumption in the README.

### Related skills — load them automatically when available

A skill cannot start another skill; you (the agent) can. When you have a skills tool and the
task matches a row, **load that skill right after this one, without asking**. If it is not
available, continue with this one.

| When the task involves | Load | For |
|---|---|---|
| reading / writing `.xlsx` files, recalculating formulas | `xlsx` | file handling, recalculation |
| induction motor, transformer, generator, CT / VT | `electrical-machine-calc` | machine design method |
| charts, series colours, dashboards outside Excel (HTML) | `dataviz` | chart rules |
| electrical installation schematics, drawings in QElectroTech / FreeCAD | `freecad-qelectrotech` | drawings outside Excel |
| a part from Inventor (parameters, iLogic) | `ilogic-inventor` | taking over dimensions and parameters |
| a PDF of a standard or catalogue as a source | `pdf` | extracting tables |

This skill **replaces** the earlier `excel-design`, `python-openpyxl-engineering` and
`vba-excel-engineering`. If they are enabled at the same time, the rules of this skill win.

---

Goal: a **calc pad** — a workbook that reads like a hand calculation in a report. Top to
bottom: title block → **status banner** → inputs → calculation steps → **checks** → result.
Every condition has a utilisation **η** and a status ✔ / ▲ / ✘; one banner at the top says
whether the result may be used. Anyone a year from now must be able to answer: where does this
number come from, what may I change, what verifies it, where does validity end.

The visual language (colours, column grid, styles, title block) has a **single source of
truth** in [reference/visual-language.md](reference/visual-language.md). Status formulas, the
banner and conditional formatting rules are in [reference/conditions.md](reference/conditions.md).
Both build paths (A and B) use them unchanged. Colour means a cell's role or a status, never
decoration: no colours outside the tokens, no emoji, gradients, shadows or marketing headings —
follow *Restraint* in visual-language.md so the result looks like a design office sheet, not AI slop.

## 0. Choose the path

| Environment | Path |
|---|---|
| Claude in Excel, or the user wants changes in the open workbook | **A – live in the workbook** → [reference/excel-in-place.md](reference/excel-in-place.md) |
| You have a shell + Python (claude.ai, Claude Code) and the output is a file | **B – generated file** → [reference/python-engcalc.md](reference/python-engcalc.md) |
| The user brought an existing workbook for review | **C – review**: step 1, then [reference/review.md](reference/review.md) |
| More than ~3 calculation sheets or more checks than fit into one session | **D – tickets** → [reference/tickets.md](reference/tickets.md), then A/B ticket by ticket |

Done when the path is chosen and its reference file is loaded.

## 1. Calculation specification (before the first cell)

Write down this table and have the user confirm it — nothing is built without it. The rows
marked → spec are detailed in [reference/specification.md](reference/specification.md): what to
ask, the defaults to offer, and where each answer lives in the workbook.

| Item | Content |
|---|---|
| Purpose and field | what is checked; electrical / mechanical / civil (sets the accent colour) |
| **Requirements** → spec §1 | ID, requirement, **origin** (standard / contract / client spec / internal rule), limit; every requirement gets a check |
| **Normative basis** → spec §2 | standard + **edition** + national annex + options chosen (NDPs, method alternatives) |
| **Safety concept** → spec §3 | partial factors / global safety factor / rating with derating / acceptance criterion; class; `cfg_eta_warn` |
| Inputs | symbol, description, SI unit, **min–max** or **list**, source and **status** (confirmed / measured / standard / assumed → spec §6) |
| **Cases** → spec §4 | load cases, operating states or scenarios, combination rule; a single case is stated as such |
| **Conventions** → spec §5 | axes and origin, positive directions, electrical reference system, angle units |
| Tolerances (optional) → spec §7 | nominal or unfavourable values; input tolerances, measurement uncertainty |
| Constants | value, unit, **standard + clause / table** |
| Databases | catalogues (sections, cables, materials, tolerances) → sheets `9x_`; master tables, keys, dependent dropdowns → [reference/databases.md](reference/databases.md) |
| Steps | relation as written + source, in calculation order |
| Checks | "effect ≤ resistance" or "value ≥ minimum" → η, requirement ID, source of the condition |
| Validity conditions | assumptions of the method (regime, range, class) → `condition` rows |
| Test data (optional) → spec §8 | when measurements are judged: instruments with calibration, test conditions, **decision rule** |
| Reference case | a known result (worked example from a standard / textbook, hand calculation) |
| Target platform | Excel 365 / 2021 / 2016 / LibreOffice — decides which functions you may use |
| **Layout** | **the user chooses** — S one-screen calculator · M mosaic of pages · K compact check sheet · V variants in columns · P calc pad · R printable report ([reference/layouts.md](reference/layouts.md)) |

Ask in groups ([reference/specification.md](reference/specification.md) "How to ask"), not
item by item. Do not make up a missing parameter — ask, or record it in the assumption register
as **TO CONFIRM** (spec §6); the banner then shows ▲ until it is confirmed.
Done when every requirement has a check, every check both sides of the inequality and a
source, every input a range and a status, the edition of every standard is known (or an
assumption), the cases are listed, and the user picked a layout.

**Layout is the user's choice, not yours.** Show the table and the previews from
[reference/layouts.md](reference/layouts.md) (`AskUserQuestion` with previews when you have it),
recommend one (default **S + P**, + **R** for a report) and build what they pick. Dense layouts
(S, M, K) show inputs, sketch and checks on one screen, so a wrong value is noticed at once.

For the field, see [reference/domains.md](reference/domains.md) (typical checks and limits
for electrical / mechanical / civil).

## 2. Workbook skeleton

| Sheet | Content |
|---|---|
| `00_README` | identification (named `meta_*`), purpose, scope of validity, assumptions, workflow, legend, contents with links, sources, revision log |
| `01_Overview` | dashboard: banner, KPI tiles, live sketch / drawing, diagrams, utilisation chart — **references only** |
| `02_Calculator` | **one-screen calculator** (layout S): the inputs + everything that reacts to them — [reference/layouts.md](reference/layouts.md) |
| `1x_*` | calculation sheets (calc pad), one per logical unit |
| `2x_*` | drawings (part drawing, schematic) — [reference/part-drawing.md](reference/part-drawing.md) |
| `7x_*` | **printable report** (style R): procedure with substituted values, tables, sketches, signatures — [reference/report-sheet.md](reference/report-sheet.md) |
| `80_Checks` | register of all checks and conditions, `cfg_eta_warn`, totals `chk_eta/chk_fail/chk_warn` |
| `9x_*` | databases (Excel tables, one record per row, unique key, source row) and chart / drawing data — [reference/databases.md](reference/databases.md) |

Data flows one way: inputs → calculation → checks → overview. Sheet names `NN_Ascii`.
No hidden sheets / rows. Done when all sheets exist with a title block and banner.

## 3. Calculation sheet

**Style** per the chosen layout ([reference/layouts.md](reference/layouts.md)) and
[reference/sheet-styles.md](reference/sheet-styles.md): the main check as a
**compact check sheet K** (TCC style: red section headings, blue underlined inputs, sketch with
loads top right, design status with a utilisation chart, load case table with relations,
assumptions a)–f)); long derivations as **calc pad P**; for printing / PDF add a **report sheet R** that only reads
from them ([reference/report-sheet.md](reference/report-sheet.md)). Content and rules below apply to all.

**Use the visuals fully, but only where they carry meaning** (Restraint in
[reference/visual-language.md](reference/visual-language.md)): cell styles and the theme, custom number formats, conditional
formatting, data bars, sparklines, pictures in cells driven by a selection, shapes with text
linked to cells, live sketches from charts, linked pictures — catalogue in
[reference/excel-toolbox.md](reference/excel-toolbox.md) §10–13.

### Row by row

One row = one quantity. Columns B–I: `# | Quantity | Symbol = | Value | Unit |
Relation / condition | Source / standard | Limit / status`. Row types:

| Type | Value cell | Status (col. I) | Required |
|---|---|---|---|
| **input** | yellow, blue font, unlocked, data validation | ✔ within limits / ✘ out of range | min–max or list |
| **select** | teal, list from `lst_*` (dependent list below its parent) | ✔ from list / ✘ not in list | lookup table in `9x_` |
| **const** | purple | — | source (standard, clause) |
| **calc** | formula, black (green = from another sheet) | — | relation as written in col. G |
| **check** | η = effect / resistance | ✔ / ▲ / ✘ | both sides + source |
| **condition** | YES / NO | ✔ text / ✘ text | text of the assumption |
| **remark** | dynamic text (`IF` on the regime) | — | — |
| **result** | orange, bold frame | — | — |

Every quantity gets a **named range** (`in_`, `c_`, `calc_`, `out_`, `chk_`, `db_`, `lst_`,
`gd_`, `cfg_`, `meta_`) and formulas work with names: `=calc_qEd*in_L^2/8`. **Names are
case-insensitive** — `in_D` and `in_d` are the same name; use `in_D` and `in_dbore`.
A number in a formula only as part of the written relation (in col. G) or a unit conversion.
Done when no row has an empty symbol, unit or (for const/check) source.

**The full Excel arsenal.** For every step pick the strongest function the target platform
offers — catalogue lookup, interpolation in a standard's table, complex numbers for phasors,
matrices for systems of equations, statistics and regression for measurements, `CONVERT` for
units, `LET`/`LAMBDA` for readability, Power Query and pivot tables for data. A hand-made
substitute for an existing function is a finding. Catalogue "task → function → version":
[reference/excel-toolbox.md](reference/excel-toolbox.md). The minimum Excel version goes into
the README.

## 4. Conditions — make "within limits" visible

Three layers, all mandatory ([reference/conditions.md](reference/conditions.md)):

1. **Inputs**: data validation (stop) + a status cell that also catches values pasted in.
2. **Checks and validity conditions**: η, the inequality as text with numbers (`FIXED`),
   status ✔/▲/✘, colour by status, data bar on η in the register.
3. **Banner** on every sheet: `✔ ALL CHECKS AND CONDITIONS SATISFIED` / `▲ … low reserve` /
   `✘ FAILS – n` + `η max`. An input out of range also switches the banner to ✘.

Done when changing any input beyond its limit switches the banner to ✘ (try it).

## 5. Graphics

- **Live sketch**: XY chart from cells with coordinates computed from the inputs (section,
  truss, bolt pattern, phasor diagram). Follows the selection — prefer it to a picture.
- **Static sketch / schematic**: a picture (matplotlib, CAD export) next to the inputs.
- **Diagrams**: XY chart from a table of points in `91_ChartData` (M(x), characteristic, heating).
- **Capacity envelope**: resistance as a curve + effect as a point (interaction diagram).
- **Utilisation**: bar chart of η from the register, axis 0–1.2.
- Key relations as a rendered equation next to the section (path B: `equation()`).
- **Part drawing / section**: outline from the dimensions (XY chart), hatching, centre lines,
  dimensions with tolerances from cells, GD&T frames, title block —
  [reference/part-drawing.md](reference/part-drawing.md).
- **Dashboard widgets**: slider and spinner on an input, unit switch, level gauge / scale,
  digital display, gradient area charts, flowchart from shapes —
  [reference/dashboard-widgets.md](reference/dashboard-widgets.md).

Axes always with units, no 3D, series colours from the palette.

## 6. Verification (never hand over without it)

1. Zero error values (`#DIV/0!`, `#NAME?`, `#REF!`, `#VALUE!`).
2. The reference case from the specification matches (deviation stated in the README or as a `check`).
3. Hand check of at least one check (compute it independently, tell the user).
4. Condition test: one input beyond its limit → banner ✘; revert.
5. Traceability ([reference/specification.md](reference/specification.md)):
   - every requirement has a check (`req_status` without ✘);
   - every standard has its edition and national annex in the README;
   - every factor of the safety concept is applied once, visibly in col. G;
   - every check names its governing case (or the README says "single case");
   - every input has a status; unconfirmed assumptions are listed in your answer and the
     workbook is marked PRELIMINARY while any remain;
   - test data: every instrument calibrated on the test date, the decision rule in the README.
6. Path B: `python scripts/verify.py file.xlsx --render out/` → exit 0, look at the PNGs.
   Path A: go through the checklist in [reference/excel-in-place.md](reference/excel-in-place.md).

Done when all 6 points passed; the result of the hand check and the list of unconfirmed
assumptions go into your answer.

## Supporting files

- `scripts/engcalc.py` — library (path B)
- `scripts/example_ipe_beam.py` — reference build: IPE beam check (EN 1993-1-1) with a printable report `70_Report`; `--screen` builds the one-screen calculator `02_Calculator` (layout S)
- `scripts/example_flange.py` — reference build: flange with ISO 286 fit, ISO 2768, tolerance chain and a live drawing
- `scripts/verify.py` — LibreOffice recalculation, lint, render
- `reference/vba.md` — macros for desktop Excel only (Claude in Excel does not run VBA)
- `reference/patterns.md` — catalogue of patterns from reference workbooks (iteration, FDM grid, variants)
- `reference/part-drawing.md` — parametric part drawing in Excel (outline, dimensions, tolerances, GD&T, title block)
- `reference/dashboard-widgets.md` — controls, gauges, shapes, flowcharts
- `reference/specification.md` — what to ask before building: requirements, normative basis, safety concept, cases, conventions, input status, tolerances, test data
- `reference/layouts.md` — layout catalogue with previews (S, M, K, V, P, R, D) — the user picks one
- `reference/report-sheet.md` — printable calculation report / data sheet (style R, `ReportSheet`)
- `reference/databases.md` — writing catalogues and registers as Excel tables, dropdowns (dependent, filtered), lookup functions, integrity conditions, entry forms, literature
