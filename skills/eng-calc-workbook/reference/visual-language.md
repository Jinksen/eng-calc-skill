# Visual language

The single source of truth for the look. `scripts/engcalc.py` (class `C`, `GRID`, `_style_defs`,
`_LINE`) implements it 1:1 — when you change one, change both.

## Colour tokens

| Token | Hex | Use |
|---|---|---|
| NAVY | `1F3864` | section heading (fill, white font), banner frame, title block lines, drawing outline |
| BLUE | `2E75B6` | chart series 1, links, calculation sheet tab |
| BLUE_LT | `D9E1F2` | subsection |
| BLUE_XLT | `F2F6FC` | column headers, KPI tiles |
| INPUT_FILL / INPUT_FONT | `FFF2CC` / `0000FF` | manual input (bold), frame `8EA9DB` |
| SELECT_FILL | `DDF4F7` | pick from a list (font `0000FF`) |
| CONST_FILL / CONST_FONT | `EDE4F5` / `5B2C83` | constant from a standard / catalogue |
| LINK_FONT | `00703C` | formula reading another sheet |
| MUTED | `7F7F7F` | units, auxiliary results (italic), sources (8 pt italic) |
| RESULT_FILL / RESULT_EDGE | `FCE4D6` / `C55A11` | key result, medium frame |
| NOTE_FONT | `1F4E79` | dynamic remark (bold italic) |
| OK | `C6EFCE` / `006100` | ✔ OK |
| WARN | `FFEB9C` / `9C5700` | ▲ low reserve |
| FAIL | `FFC7CE` / `9C0006` | ✘ fails / out of range / cannot evaluate |
| NA | `EDEDED` / `595959` | – not evaluated |
| Chart series | `2E75B6 C55A11 548235 7030A0 BF8F00 1F3864` | in this order |

**Field accent** (left block of the title block): electrical `BF8F00`, mechanical `2F5597`,
civil `548235`, general `1F3864`.

**Sheet tabs**: README `7F7F7F`, overview `1F3864`, calculation and drawing `2E75B6`,
checks `548235`, data `7030A0`, printable report `C55A11`.

Colour never carries information alone: a status always has a symbol and text too (✔ ▲ ✘ –),
black-and-white printing.

## Drawing lines (ISO 128)

| Kind | Colour | Width | Dash | Use |
|---|---|---|---|---|
| outline | NAVY | 2.0 pt | solid | visible edges |
| hidden | NAVY | 0.75 pt | dash | hidden edges |
| axis | `C00000` | 0.75 pt | long dash-dot | centre lines, pitch circles |
| hatch | `595959` | 0.5 pt | solid | section hatching 45° |
| dim | `262626` | 0.75 pt | solid, arrows | dimension lines |
| ext | `262626` | 0.5 pt | solid | extension lines |

## Fonts and numbers

- Calibri 10 pt; section heading 11 pt bold CAPITALS; result 11 pt bold; KPI 18 pt.
- Column "Relation" Cambria Math 10 pt. Dimension texts on drawings 9 pt NAVY.
- Format by quantity, no false precision: forces / moments `0.0`, stress in MPa `0`, factors
  `0.00`, utilisation η `0.00`, ε and small ratios `0.000`, dimensions in mm `0` or `0.0`,
  tolerances in mm `0.000`, deviations in µm `0`.
- The unit **always in the neighbouring column**, never as text in the cell with the number.
- Dates `yyyy-mm-dd`.

## Calc pad grid (columns A–J)

| Col. | Width | Role | Style |
|---|---|---|---|
| A | 1.5 | margin | — |
| B | 5 | step number `3.12` | unit |
| C | 30 | quantity (description) | label |
| D | 9 | symbol + ` =` | bold italic, right |
| E | 12 | **value** | by row type |
| F | 8 | unit | grey |
| G | 26 | relation as written / inequality text | Cambria Math |
| H | 18 | source / standard (clause) | 8 pt italic grey |
| I | 22 | limit / status | bold centred, colour by status |
| J | 1.5 | margin | — |

Content rows have only a thin bottom line `D9D9D9`; sheet gridlines off.

## Sheet title block (rows 1–7, repeated when printing)

| Row | B–C (field accent, white font) | D | E–G | H | I |
|---|---|---|---|---|---|
| 1 | `=meta_org` 11 pt bold | Project | `=meta_project` | Sheet no. | `=SHEET()&" / "&SHEETS()` |
| 2 | "Engineering calculation" | Calculation | `=meta_title` 12 pt NAVY | Date | `=meta_date` |
| 3 | `=meta_std` | Sheet | sheet name | Prepared by | `=meta_author` |
| 4 | `="Revision "&meta_rev` | Subject | `=meta_subject` | Checked by | `=meta_checker` |
| 5 | **banner** across B–I, height 26, 12 pt bold, NAVY medium frame, *centre across selection* |
| 6 | instruction 9 pt italic: what goes where + legend ✔ ▲ ✘ |
| 7 | column headers 8 pt bold NAVY on BLUE_XLT, medium bottom line; freeze panes below row 7 |

Title block labels (Project, Date…) 7 pt grey; values bold. Text `meta_*` are referenced with
`&""` so that an empty cell does not show 0. Identification lives only on `00_README`.

## Sections and headings

- Section: whole row B–I NAVY fill, number in B, name in C in CAPITALS, height 18, an empty row above.
- Subsection: BLUE_LT fill, NAVY bold font, NAVY bottom line.
- Comment: 9 pt italic grey in col. C.

## Dashboard

KPI tiles 4 side by side (B–C, D–E, F–G, H–I): label 9 pt grey, value 18 pt NAVY, unit;
BLUE_XLT fill, NAVY medium top line. Below a grid of charts: sketch / drawing left, diagrams
right, utilisation across the full width at the bottom.

## Printing

A4 portrait (data sheets landscape), fit to 1 page wide, margins 1 cm, print rows 1–7 on every
page, footer `file | sheet | Page P / N`, centred horizontally.

## Printable report (style R)

12 columns B–M of width 8 (A and N margins 1.5), A4 portrait, rows 1–2 repeated. Title 20 pt
NAVY CAPITALS, band NAVY with white bold text, section bars BLUE with white bold text, label |
value boxes (value fill `F2F2F2`), table header BLUE, striped rows `F2F6FC`, total row BLUE_LT
with a medium NAVY top line, substitution lines in Cambria Math 10 pt, results bold with a NAVY
bottom line. Details: [report-sheet.md](report-sheet.md).

## Protection

Only `input`, `select` and the revision log / identification fields on the README are unlocked.
Sheets protected without a password (protection against accidental overwriting, not secrecy).
Formulas are never hidden.
