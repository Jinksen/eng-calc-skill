# Workbook templates — what a finished workbook looks like

A template is a **whole workbook** (sheets, layout, conventions), not one sheet. Pick one in
SKILL.md §1 together with the layout, then build from its reference script. All templates share
the same names, checks, banner and register, so they can be mixed (e.g. T1 main sheet + T4 report).

| | Template | Model | Sheets | Layout | Reference build |
|---|---|---|---|---|---|
| **T1** | **Design-office sheet** | TCC / RCC design spreadsheets (pile cap, ribbed slab) | `10_Main` · `11_Details` · `80_Checks` · `91_ChartData` · README | K (or M) | `example_pile_cap.py` (`FormSheet`) |
| **T2** | **Calculation notebook with side catalogue** | electrical "distribution transformer calculation" sheets | numbered sections left, catalogue tables / picture / second method right | K zones | `FormSheet` (`table(at="right")`) |
| **T3** | **Calculator + calc pad** | design by trial | `02_Calculator` · `10_*` pad · overview | S + P | `example_ipe_beam.py --screen` |
| **T4** | **Calc pad + printable report** | calculation appendix to a technical report | `10_*` pad · `70_Report` · overview | P + R | `example_ipe_beam.py` |
| **T5** | **Part with a drawing** | machine part, fit, tolerance chain | `10_*` pad · `20_Drawing` · `92_DrawingData` | P + drawing | `example_flange.py` |
| **T6** | **Variant comparison** | which size / which option | `15_Variants` next to the main calc | V | `CalcSheet` + pattern P18 |
| **T7** | **Catalogue / register** | sections, cables, materials, equipment list | `9x_*` tables, entry sheet with dropdowns | tables | `DataSheet` → [databases.md](databases.md) |

Default: **T1** for a member or element check handed to a checker on paper, **T3** when the
engineer will try many values, **T4** when the output goes into a report. When unsure, show
this table and ask.

## What every template has (the rules, whatever the look)

| Part | Where | Why |
|---|---|---|
| Job box: project, client, location, made by, checked, date, revision, job no., page | top of every printed sheet (`meta_*` names, typed once in README) | a printed page is identifiable on its own |
| One status per sheet: `STATUS ✔ OK η max = …` / `✘ FAILS` | top right (T1) or row 2 / 5 banner | the reader sees the answer first |
| One input convention: blue (underlined in T1, yellow fill elsewhere), unlocked, validated | every input | "type only here" without reading a manual |
| Input messages: out-of-range value → red value + `✘ … allowed ⟨a ; b⟩` | next to the input or right of the page (T1) | the RCC "red messages indicate entry errors" |
| Operating instructions (3–5 lines) | right of the print area (T1) or row 6 | the sheet explains itself, not printed |
| Checks with both sides in numbers, η, ✔ / ▲ / ✘ and the relation or clause | check table | traceable without opening formulas |
| Assumptions a) b) c), scope of validity, what is **not** checked | bottom of the main sheet + README | honest limits |
| Sources with editions, revision history (date · rev · change · by) | README (`Refs`, `Notes` of the TCC sheets) | audit trail |
| Live sketch / plan view / diagram from the inputs | next to the inputs | a wrong value shows as a wrong picture |
| One print page per block, print area set, no merged cells, sheets protected (inputs unlocked) | page setup | prints like the TCC sheets without fiddling |

## Use the whole page — visibility first

The TCC, RCC and transformer sheets fill the screen and the A4 page edge to edge: everything
about the element is visible at once, so a wrong input shows its consequence without
scrolling. That density is the point of these templates.

| Rule | How |
|---|---|
| **three blocks per row**, not one column of rows | `FormSheet` zones `left` · `mid` · `right` (5 narrow columns each); e.g. DIMENSIONS · LOADS · RESULTS |
| **no empty corner**: put the sketch or chart beside the shorter block | `at="half"` sketch + `at="right"` chart; check the render — a white quarter page is a layout bug |
| **dense rows**: 9 pt labels, row height 13.5, label and symbol right aligned against the value | built into `FormSheet` |
| **narrow columns, nothing merged** | 15 columns × 6.3; labels overflow to the left |
| **one A4 page, fitted**, margins 0.25 in | `close()` sets fit to 1 × 1 page |
| **screen = page**: zoom 90 %, frozen job box, instructions and messages just right of the page | visible while typing, not printed |
| short labels (≤ 18 characters with the symbol) | `Column load N_Ed`, not `Design axial load from the column at ULS` |
| tables run across the full width, positions or cases as columns | `fm.table(..., at="full")` |
| fill the page with content that answers something (schedule, load table, second view) — never with decoration | Restraint in [visual-language.md](visual-language.md) |

If the content of one element does not fit one page, use layout **M** (several A4 blocks side by
side on one wide sheet) instead of letting a single page grow long.

## T1 — design-office sheet (TCC / RCC style)

What the TCC pile cap and the RCC ribbed slab sheets do, and how it maps to the skill:

| In the original | Here |
|---|---|
| job box (Project / Client / Location · Made by / Date / Page · Checked / Revision / Job no) with the office name | `FormSheet` header rows 2–5, from `meta_*` |
| `STATUS VALID DESIGN` top right | `STATUS ✔ OK η max = …` from the register |
| `DIMENSIONS`, `LOADING`, `MATERIALS` in red capitals, 2–3 quantities per row | `fm.section("Dimensions", unit="mm", at="left")`, `fm.input(..., at="left" / "right")` |
| blue underlined inputs `5`, `7.200` | style `ec_input_k` |
| "ENTER DATA IN BLUE CELLS ONLY", "RED MESSAGES INDICATE ENTRY ERRORS", "SHORTEST SPAN NOT < 6.12 m" | `instructions=[…]` panel and the input messages in columns O–P |
| small geometry and bending moment diagrams | `fm.chart(drawing_chart(...) / xy_chart(...), at=…)` from `91_ChartData` |
| table across positions (END SUPPORTS · END SPANS · INTERIOR …) with the BS / EC clause on the right | `fm.table(cols, rows, at="full")` — one column per position, last column the clause |
| bending / deflection checks with `OK` | `fm.checks()` — η, √ and relation from the calc pad |
| tabs MAIN · DETAILS · Weight · Graf · Notes · Refs | `10_Main` · `11_Details` · `9x_` · `91_ChartData` · README (notes, sources, revisions) |
| tabs DOUBLE · 3CAP · 4CAP … (one sheet per configuration) | one `FormSheet` + pad per configuration, built in a loop with a prefix on the names (`in2_`, `in3_`) — or variant columns (T6) |
| "Print Sheet" / "Print ALL Output" buttons | print areas per sheet; buttons only with macros → [vba.md](vba.md) |
| revision table (date · version · action · page) and disclaimer | README revision log and scope / assumptions |

Build (path B):

```python
fm = book.form_sheet("10_Main", "Two-pile cap design", "…", instructions=["Piles in one line, column centred."])
fm.section("Dimensions", unit="mm", at="left");   fm.input("in_s", "Pile spacing", "s", 1800, "mm", lo=900, hi=3600, fmt="0")
fm.section("Loads and materials", at="mid");      fm.input("in_NEd", "Column load", "N_Ed", 1500, "kN", lo=0, hi=20000, at="mid")
s = book.calc_sheet("11_Details", …)               # every step with relation and source, reads in_*
fm.section("Results", at="right");  fm.value("Tie force", "T", "calc_T", "kN", fmt="0", at="right")
fm.section("Plan view", at="half");  fm.chart(plan_view, at="half");  fm.utilization_chart(at="right", width=6.4, height=5.4)
fm.checks();  fm.table(..., title="Reinforcement schedule");  fm.notes([...], title="Assumptions");  fm.close()
```

Rules: inputs **only** on `10_Main`; logic only on `11_Details`; `10_Main` fills one A4 portrait
page (three blocks per row, no empty corner); at most ~12 inputs per block; messages and
instructions stay outside the print area.

## T2 — calculation notebook with a side catalogue

Model: electrical sheets like "distribution transformer calculation" — numbered sections
(`1 – Transformer data`, `2 – Short-circuit protection`, `3 – Prospective short-circuit
current`), each with rows `quantity | symbol | = | value | unit` on the left and, on the right,
the **catalogue it draws from** (standard ratings of transformers, breakers, cables), a picture
of the equipment and an **alternative method** box that checks the main result.

| Element | How |
|---|---|
| numbered sections | `fm.section("1 – Transformer data", at="left")` (numbers in the title) |
| quantity rows | `fm.input` / `fm.value` at `left` |
| standard ratings table | `9x_` catalogue (`DataSheet.table`) shown with `fm.table(..., at="right")`; the selected row highlighted by conditional formatting |
| next standard size ("select 630 A breaker") | `next_higher()` on the catalogue, shown as a result |
| picture of the equipment | `fm.figure(png, at="right")` — a picture, not decoration: it shows the connection or nameplate |
| "another method" box | second calculation on the pad + `condition` "methods agree within 5 %" |
| remarks box (where the formula comes from, what the symbols mean) | `fm.notes([...], title="Remarks")` |

Do not copy the original's colour bands per section and filled tables — sections get the red
heading, catalogue tables the standard header (Restraint in [visual-language.md](visual-language.md)).

## Choosing quickly

| The user says | Template |
|---|---|
| "like the TCC / RCC / Concrete Centre spreadsheets", "design sheet", "one page for the checker" | T1 |
| "with the table of standard sizes next to it", "transformer / breaker / cable selection" | T2 |
| "calculator", "try values" | T3 |
| "report", "PDF", "appendix" | T4 |
| "part", "drawing", "tolerance" | T5 |
| "compare", "which is better" | T6 |
| "catalogue", "list of …", "register" | T7 |
