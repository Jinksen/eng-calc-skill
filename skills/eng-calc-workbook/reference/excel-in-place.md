# Path A — live in the workbook (Claude in Excel / manual build)

Claude in Excel works directly on the open workbook: it writes values and formulas, formats,
adds conditional formatting and data validation, works across sheets. **It does not run
Python or VBA** and does not support What-If Data Tables. The whole standard therefore rests
on native Excel features — the result is the same as from path B.

## Build order

The state after every step must recalculate without errors. Work sheet by sheet, not layer by layer.

1. **Cell styles** (Home → Cell Styles → New Cell Style), names exactly: `ec_input`,
   `ec_select`, `ec_const`, `ec_calc`, `ec_link`, `ec_aux`, `ec_result`, `ec_h1`, `ec_h2`,
   `ec_colhead`, `ec_status`, `ec_note` — properties in [visual-language.md](visual-language.md).
   If the API cannot create styles, format directly with the same tokens and mention the style
   names in the README.
2. **`00_README`** — identification in C5:C13, each cell named `meta_project`, `meta_title`,
   `meta_subject`, `meta_org`, `meta_std`, `meta_author`, `meta_checker`, `meta_rev`,
   `meta_date`. The rest of the README at the end.
3. **`80_Checks`** — title block, `cfg_eta_warn` in E8 = 0.90 with validation 0.5–1.0,
   register header in row 10. Register rows are added with every check.
4. **Databases `9x_`** — an Excel table (Insert → Table) named `tbl_<x>`, values in the const
   style, a "Source: …" row above the table. Name the columns `db_<x>_<column>`, the key
   column `db_<x>_key` and the same range `lst_<x>` for dropdowns.
5. **Calculation sheet `1x_`** — column widths A–J, title block rows 1–7, freeze panes at A8,
   gridlines off. Then section by section (row types in SKILL.md §3, formulas in
   [conditions.md](conditions.md)). Name every value as you write it — and remember that names
   are case-insensitive.
6. **Checks** — for every `check`/`condition` add a row to the `80_Checks` register (numeric
   above conditions) and extend the names `chk_eta`, `chk_fail`, `chk_warn`.
7. **Banner** in row 5 of every sheet + conditional formatting (conditions.md §6–7).
8. **Charts** — data into `91_ChartData` (sketch coordinates, diagram points), XY scatter with
   lines and no markers; sketch: axes hidden, equal x and y range, square plot area. Drawings
   per [part-drawing.md](part-drawing.md). If a chart cannot be inserted in the environment,
   prepare the data block and tell the user in one sentence which range to insert as
   *Scatter with straight lines*.
9. **README** — purpose, scope of validity, assumptions, workflow, legend (a sample of every
   style), contents with `HYPERLINK("#'sheet'!A1",…)`, sources, revision log.
10. **Lock and print** — unlock inputs only, protect sheets without a password; print area,
    print rows 1–7 on every page, A4 fit to page width, footer.

## Changing an existing workbook

- First read the structure (sheets, names, where the inputs are) and propose a mapping to the
  standard; rebuild sheet by sheet keeping the results (compare key numbers before / after).
- Pull a hard-coded value out of a formula into a `const`/`input` row with a source.
- Confirm with the user before overwriting occupied cells.

## Substitutes for features out of reach

| I want | Native substitute |
|---|---|
| option button / check box (Form Controls, VBA) | dropdown `YES;NO` or 0/1 with data validation |
| iteration (Goal Seek, circular reference) | iteration written out in rows + `condition` convergence ([patterns.md](patterns.md)) |
| Data Table for sensitivity | variant columns with the same formula ([patterns.md](patterns.md)) |
| a "recalculate" button | not needed — everything is formulas |
| an equation picture | relation as written in col. G (Unicode: ², ³, √, ·, ≤, γ, η, σ, Δ) |

## Checklist before handover

```
[ ] No error value in the workbook
[ ] Every input: data validation + status in col. I; out of range → banner ✘ (tried)
[ ] Every constant and check: source in col. H
[ ] Every calculation: unit (F) and relation (G); no unexplained number in a formula
[ ] All checks in 80_Checks, the chk_* names cover the whole register
[ ] Banner on every sheet, status colours work
[ ] Reference case matches; one check recomputed by hand
[ ] README complete, revision recorded; sheets protected, printing set up
```
