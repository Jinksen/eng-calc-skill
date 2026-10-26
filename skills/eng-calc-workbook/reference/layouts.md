# Workbook layouts — let the user choose

The same calculation (same names, checks, banner, register) can be laid out in several ways.
The layout decides **how much the engineer sees at once**. Dense layouts (S, M, K) put
inputs, sketch, results and checks on one screen, so a wrong input value shows its
consequence immediately: a bar jumps, a sketch distorts, a ✔ turns ✘. Long layouts (P, R)
read like a report but hide the consequence a few screens below the input.

**Ask before building** (SKILL.md §1, row *Layout*). Show the table and the previews below
(with `AskUserQuestion` and its `preview` field when available) and recommend one. Several
layouts can be combined in one workbook, because they only read the same names.

| | Layout | What is on one screen | Best for | Print | `engcalc.py` |
|---|---|---|---|---|---|
| **S** | **One-screen calculator** | inputs ✔/✘ · sketch · diagrams · η and status | design by trial: change a value, see everything react | 1 page landscape | `ScreenSheet` |
| **M** | **Mosaic of pages** (TCC wide sheet) | several A4 calc blocks side by side + plan views | one element with many parts (pile cap, foundation, joint) | each block = 1 A4 page | path A (by hand) |
| **K** | **Compact check sheet** | 1 A4 page: sketch with loads, LC table, checks, assumptions | standard member check, handover to a checker | 1 page portrait | path A |
| **V** | **Variants in columns** | the same rows for 3–10 variants next to each other | comparing designs, sensitivity, choosing a size | landscape | `CalcSheet` + pattern P18 |
| **P** | **Calc pad** | 1 quantity per row, top to bottom | long derivations, design methods, review | portrait, many pages | `CalcSheet` |
| **R** | **Printable report** | procedure with substituted values, tables, signatures | appendix to a technical report, PDF | portrait | `ReportSheet` |
| **D** | **Overview dashboard** | KPI tiles, sketch, diagrams, utilisation | management summary of a finished workbook | 1 page | `Dashboard` |

**Default recommendation**: **S + P** (+ **R** if the result goes into a report). S is where
the engineer works; P keeps every step traceable; R prints it. For a standard member check
handed over on paper: **K**. For comparing options: **V**. For one large element with many
sub-checks: **M**.

## Previews

```
S — ONE-SCREEN CALCULATOR (landscape, 18 columns, zones left | mid | right)
┌──────────────────────────────────────────────────────────────────────────┐
│ BEAM CALCULATOR             project · title · rev · author        org    │
│ ▲ OK WITH LOW RESERVE – checks: 1          η max = 0.97   (banner, live) │
├────────────────────┬────────────────────────┬────────────────────────────┤
│ INPUTS             │  [static scheme]       │ Utilisation η max          │
│ Span L    6.00 m ✔ │                        │        0.97                │
│ g_k       6.00   ✔ │  ┌ M_Ed(x) ─────────┐  │ M_Ed │ M_c,Rd │ w          │
│ Section  IPE240  ✔ │  │      ╭──╮        │  │ 72.0 │  86.2  │ 23.3       │
│ ...                │  │   ╭─╯   ╰─╮      │  ├────────────────────────────┤
│ SECTION · LOAD     │  └──────────────────┘  │ CHECKS        η        ✔/✘ │
│ h        240 mm    │  ┌ w(x) ────────────┐  │ Bending      0.84 ████  ✔  │
│ [live section]     │  │                  │  │ Deflection   0.97 █████ ▲  │
└────────────────────┴────────────────────────┴────────────────────────────┘

M — MOSAIC OF PAGES (one wide sheet, zoom 50–70 % shows the whole design)
┌─ A4 block 1 ─┬─ A4 block 2 ─┬─ A4 block 3 ──┬─ plan views ──────────────┐
│ inputs+sketch│ pile loads   │ reinforcement │ [plan 1] [plan 2]         │
│ 2 qty / row  │ table LC1..n │ checks ✔/✘    │ [plan 3] [plan 4]         │
│ checks       │ checks       │ schedule      │ revision table            │
└──────────────┴──────────────┴───────────────┴───────────────────────────┘

K — COMPACT CHECK SHEET (A4 portrait)        V — VARIANTS IN COLUMNS
┌──────────────────────────────┐            ┌────────────┬──────┬──────┬──────┐
│ TITLE            [sketch with│            │ quantity   │ V1   │ V2   │ V3   │
│ DIMENSIONS (mm)   loads]     │            │ L [m]      │ 6.0  │ 7.5  │ 9.0  │
│ b = 300   h = 500            │            │ section    │IPE240│IPE270│IPE300│
│ LOADS   LC1  LC2  │ STATUS OK│            │ M_Ed       │ 72.0 │ 112  │ 162  │
│ CHECKS  LC1  LC2 √  relation │            │ η_M        │ 0.84 │ 0.98 │ 1.07 │
│ ASSUMPTIONS a) b) c)         │            │ status     │  ✔   │  ▲   │  ✘   │
└──────────────────────────────┘            └────────────┴──────┴──────┴──────┘
```

## S — one-screen calculator (`ScreenSheet`)

Zones: `left` B–G inputs and section data, `mid` H–M sketch and diagrams, `right` N–S key
result, effect / resistance and the check list; `wide` = mid + right, `full` = everything.
Row 2 is the live banner. Everything fits one landscape page (`fitToHeight = 1`).

```python
sc = book.screen_sheet("02_Calculator", "Beam calculator", "purpose")   # banner in row 2
sc.section("Inputs", at="left")
sc.input("in_L", "Span L", 6.0, "m", lo=1, hi=12)                       # yellow, validated, ✔ / ✘
sc.input("in_sec", "Section", "IPE 240", "", choices="lst_IPE")
# … calc pad (P) reads in_L, in_sec — logic stays traceable there (inputs shown as links)
sc.fields([("h", "=calc_h", "mm", "0")], at="left", title="Section")
sc.chart(sketch_chart(sec, "x", "y", half_range=170, size_cm=5.5), at="left")
sc.figure(png, at="mid");  sc.chart(xy_chart(…, width=7.8, height=5.0), at="mid")
sc.panel("Utilisation η max", "=out_eta", "", "0.00", at="right", tiles=[…])
sc.checks(at="right")                                                   # η with data bar + ✔/▲/✘
sc.close()
```

Rules: inputs **only** on the S sheet (the calc pad shows them as green link rows); short
labels with the symbol (`Span L`, ≤ 20 characters); every number on S is a reference; keep it
to ~40 rows so it fits one screen at 100 % zoom on a laptop. Reference:
`example_ipe_beam.py --screen`.

By hand (path A): 18 columns of width 7, three zones of 6 columns; input row = label (3
columns) | yellow value | unit | ✔ / ✘; charts sized to 6 columns (≈ 7.8 cm); banner in row 2
across B–S; freeze panes below row 2; Page Layout landscape, Fit to 1 × 1 page.

## M — mosaic of pages (TCC style, path A)

One wide sheet with several A4-sized calculation blocks side by side, each block its own
print page, plus plan views on the right. Zoom 50–70 % shows the whole element; zoom 100 % on
a block to edit.

- Grid: each block 10–12 columns (~ 90 characters) = A4 portrait at "Fit to 1 page wide" per block.
- Vertical page breaks between blocks (Page Break Preview → drag, or `ws.col_breaks.append(Break(id=col))`
  in openpyxl), Print Titles none; each block repeats its own small title strip.
- Style K inside each block (2 quantities per row, blue underlined inputs, red section
  headings); inputs only in block 1, the other blocks reference them.
- Plan views / sketches as live XY charts ([part-drawing.md](part-drawing.md)), one chart
  per view, aligned in a grid.
- Banner + `80_Checks` as everywhere; each block has its own small DESIGN STATUS.

## V — variants in columns (pattern P18)

Rows = quantities, columns = variants (E, F, G…), the **same formula across the row**,
a check and a status per column, the best variant highlighted with conditional formatting
(`=E$40=MIN($E$40:$J$40)`). Inputs that differ between variants are yellow per column; common
inputs once on top. Names: `in_L` for the common value, `var_L` for the row of variants.
Good as an extra sheet `15_Variants` next to the main calc.

## Choosing quickly

| The user says | Layout |
|---|---|
| "I want to see everything at once", "try values", "calculator", "nástroj na návrh" | S |
| "like the TCC sheets", "everything about the pile cap / foundation on one sheet" | M (or K for one member) |
| "one page for the checker", "standard check" | K |
| "compare", "which size", "variants", "sensitivity" | V |
| "derivation", "design method", "every step" | P |
| "print", "PDF", "report", "výpočtová zpráva" | R (+ the working layout) |
