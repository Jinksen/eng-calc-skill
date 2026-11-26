# Dense, editable sheet — use the width, keep the calculation editable

Two goals that the user named explicitly:

1. **Few sheets, full sheets.** Good engineering workbooks have 3–6 tabs, not 15. The working
   sheet carries ~80–90 % of the content and uses its full width; supporting tabs hold details,
   data and notes. Content stacked one block under another is *not* automatically clear — clarity
   comes from a grid, section bars and blocks placed side by side.
2. **The engineer can change the calculation, not only the inputs.** Adding a step, changing a
   formula or adding a check must not need any design work: formatting, statuses, the register
   and charts follow by themselves.

## What the two reference sheets do (copy this)

### RCC ribbed slab (RCC92, BS 8110) — one working sheet, 5 tabs

| Observed | Rule for the skill |
|---|---|
| tabs `MAIN · DETAILS · Weight · Graf · Notes` — MAIN holds everything the engineer needs | working sheet + 2–4 support tabs; never one tab per small step |
| job box across the full page width (Project / Client / Location · Made by / Date / Page · Checked / Revision / Job no) | title block spans the whole working width, not columns A–D |
| `DIMENSIONS` left and `MATERIALS` right **at the same rows**; `LOADING` left with the geometry sketch beside it and the bending moment diagram further right, all at the same height | blocks in 2–3 bands side by side; a sketch sits beside the block that drives it |
| results table across the full width: one column per position (END SUPPORTS · END SPANS · FIRST INT · INTERIOR …), one row per quantity, the clause (`Table 3.12`, `Fig 3.3`) in the last column | tables of results are wide: positions / cases as columns, the standard reference column on the right edge |
| `STATUS — VALID DESIGN` top right of the page | one status, always visible, top right |
| operating instructions, entry-error messages (pink), limits ("SHORTEST SPAN NOT < 6.12 m") and print buttons in a coloured panel **right of the print area** | help and messages are visible while typing but not printed (columns right of the page) |
| deflection results with "As auto increased by 17.8 %" | the sheet explains automatic decisions in one short line next to the value |
| ~40 rows visible at 75 % zoom, small 9–10 pt font, no wasted rows | dense rows; zoom 75–90 % is normal for a working sheet |

### Engineering change form — grid and section bars

| Observed | Rule for the skill |
|---|---|
| every section starts with a **full-width bar** (BASIC INFORMATION, CHANGE DESCRIPTION, IMPACT ASSESSMENT, COST ANALYSIS, APPROVAL PROCESS) of identical width | section bars span the whole content width; the same width everywhere gives the vertical rhythm |
| header info as **two pairs of label \| value side by side** (Change number … left, Date / Requested by … right) | short metadata and inputs go in 2 (or 3) label-value pairs per row, not one long list |
| all tables share **one column grid** — the label column of the header is also the first column of every table | one column grid for the whole sheet; blocks align to it, so the eye scans straight down |
| totals row in a darker band, bold | totals / governing values get one stronger band, nothing more |
| red / green fill only where the value means worse / better | colour = status, never decoration (Restraint) |
| approval block at the end: role · name · title · signature · date · comments | sign-off table at the end of the printed area (Prepared / Checked / Approved) |
| **flaws to avoid:** labels cut or overlapping ("Reason for / Change:"), headers wrapping in a too-low row ("Completion Date") | short labels (≤ 18 chars), row height fits the font, never a wrapped header in a 13.5 pt row |

## Width — how to fill it

- **Bands, not a column.** Think of the working sheet as horizontal bands. Each band holds 2–4
  blocks side by side that belong together: `INPUTS geometry | INPUTS materials | SKETCH`,
  then `LOADS | CALCULATION | DIAGRAM`, then a full-width `RESULTS` table, then `CHECKS | STATUS`.
- **One column grid.** Narrow uniform columns (≈ 6–9 wide); a block takes a whole number of them.
  Fixed positions for label / symbol / value / unit / reference inside every block.
- **The page is wide, not the font small.** Up to ~BB (SKILL.md hard rule 1); at 75–90 % zoom
  the whole first band and the status are visible. When printing, each band or block group is
  one A4 landscape page (or layout M blocks).
- **Supporting panels to the right** of the print area: instructions, input messages, limits.
- **No empty quarter.** If one block is shorter, put the sketch, a diagram or a small table
  beside it — content that answers something, never decoration.

## Editability — the calculation changes, the design stays

Research basis: ICAEW *Twenty principles* and the FAST Standard (separate inputs / workings /
outputs, one formula per row, no constants inside formulas, consistent column meaning),
IStructE guidance on calculation spreadsheets (separate regions, top-down / left-to-right flow,
consistent formatting). Apply them like this:

| Rule | How in Excel | Why the user can edit freely |
|---|---|---|
| **formatting by cell styles only** (`ec_input`, `ec_calc`, `ec_const`, `ec_h`, `ec_note`, …), never direct formatting per cell | path B: `engcalc.py` styles; path A: *Cell Styles* | a new row gets its look by applying one style; change a style once → the whole workbook follows |
| **conditional formatting on whole block ranges**, not on single cells | rule applies to `$E$20:$E$80`, not `$E$23` | a new step inside the block is coloured / statused automatically |
| **spare formatted rows** at the end of every calculation block (3–5, empty, styled, inside the CF range and the print area) | build them with the block | inserting a step = typing into a spare row, no reformatting |
| **tables (ListObjects) for anything list-like**: checks register, load cases, catalogues, schedules | *Insert → Table*, structured references | new row inherits formulas, formats, validation and is picked up by charts and totals |
| **names, not addresses** — every input `in_*`, every result `calc_*`, every check `chk_*` | Name Manager | blocks can move or grow without breaking formulas; formulas read like the hand calculation |
| **the shown relation is live**: the "relation" column uses `=FORMULATEXT(cell)` (or the substituted-value text built from the same names) | see report-sheet.md | changing a formula updates what the reader sees; no stale hand-typed formula text |
| **one formula per row**, same across columns of positions / variants; no constants inside formulas | constants in a sourced table or `k_*` names | the user edits one cell and copies across; Ctrl+\ finds inconsistencies |
| **checks register is a table**; banner and status read the whole column (e.g. `=MAX(tbl_Checks[η])`), never a list of cells | `80_Checks` as a table (path A: *Format as Table*) | adding a check = adding a row; the banner includes it with no edit |
| **charts and sketches read names or table columns**, never a fixed cell range | `91_ChartData` as a table / names | added points appear in the chart |
| **protection without a password**, inputs unlocked, *Format columns / rows* and *Insert rows* allowed | *Review → Protect sheet* options | the engineer can unprotect, edit a formula, protect again |
| **no merged cells** — section bars use *Center Across Selection* | alignment option | rows and columns can be inserted anywhere |
| README section **"How to change the calculation"**: where to add a step, a check, a load case, a catalogue row | 5–8 lines in `00_README` | the next engineer does not reverse-engineer the sheet |

### Editability test (part of SKILL.md §6, point 6)

1. Insert a new step into the main calculation block (use a spare row): it gets the right look
   and status without any formatting by hand.
2. Change one formula: the shown relation / report text follows.
3. Add a row to the checks register: the banner and the utilisation chart include it.
4. Add a load case / position column: totals, governing value and chart follow.

Any step that needs manual formatting or editing a second place is a finding.
