# Databases in the workbook — tables, dropdowns, lookups

Catalogues (sections, cables, materials, bearings, tolerances), registers (measurements, bill
of materials, test log) and the dropdowns that read them. A database that is badly written
breaks every input that depends on it, silently: a lookup returns the first duplicate, an
approximate match reads an unsorted column, a dropdown keeps an old value. The rules below
prevent that and make the failure visible when it happens anyway.

Sources: [Literature](#literature) at the end. Function versions are in
[excel-toolbox.md](excel-toolbox.md) §1.

## 1. Writing the table

One catalogue = **one Excel table** `tbl_<x>` on a `9x_` sheet (Insert → Table, path B
`DataSheet.table`). Rules after Broman & Woo (2018) and the "tidy data" lessons:

| Rule | Why |
|---|---|
| one record per row, one attribute per column, one value per cell | sorting, filtering and lookups work only on a clean rectangle |
| first column = **key**: unique, never blank, short (`IPE 200`, `Cu 4 C`, `6205`) | lookups return the first hit; a duplicate key hides the second row |
| unit in the header (`Iz [A]`), the cell is a bare number | `16 A` as text cannot be compared or summed |
| one spelling per category (`Cu`, never `cu` / `copper`) | a dropdown and `MATCH` see three different values |
| no blank rows or columns inside, no merged cells, no subtotal rows | the table stops at the first gap; subtotals get looked up as records |
| no colour or bold as data — a status column instead | formats are invisible to formulas |
| numbers as numbers, text keys as text, dates ISO `YYYY-MM-DD` | `"16"` ≠ `16` for `MATCH` |
| a "Source:" row above the table: standard, **edition**, table / clause | traceability (SKILL.md §1, Constants) |
| raw values only — derived columns are **calculated columns** (one formula for the whole column) | a typed-over formula in one row is invisible |
| more than ~6 columns → a **data dictionary** under the table: column, meaning, unit, source | the reader a year from now |

**Unique headers** in a table (Excel renames duplicates `Iz2`); headers may contain units and
brackets — `struct_ref()` escapes `[ ] # '` in structured references.

### Normalise: master tables and references

Do not repeat an attribute in every row. Put it in a **master table** and refer to it by key:

```
tbl_mat     Material | ρ [Ω·mm²/m] | α [1/K]         ← master: one row per material
tbl_cable   Cable | Material | S [mm²] | Method | Iz [A]   ← detail: Material is a key of tbl_mat
```

- The reference column (`tbl_cable[Material]`) gets data validation `=lst_mat` — only existing
  keys can be typed (**referential integrity**), and a condition `refs_ok()` catches pasted values.
- `ρ` of a cable is a lookup through the material, never a copied number.

### Wide or long

A table from a standard with two entry parameters (Iz by size × installation method):

| Form | Use |
|---|---|
| **wide** — copy of the printed table (rows = size, columns = method) | **traceability**: compared cell by cell with the standard; lookup `INDEX(tbl;MATCH(row);MATCH(column))` |
| **long** — one row per combination (`Size`, `Method`, `Iz`) | dependent dropdowns, `FILTER`, pivot tables, multi-key `lookup2` |

Transcribe the standard **wide** (one sheet per standard table, checked against the PDF), and
derive a long table only when a dropdown or filter needs it (Power Query *Unpivot*, or a
calculated block). Never type the same number twice.

## 2. Names

| Name | Refers to | Use |
|---|---|---|
| `tbl_<x>` | the Excel table | structured references inside the table |
| `db_<x>_<col>` | `=tbl_<x>[Header]` — data of one column | lookups outside the table |
| `db_<x>_key` | key column | `MATCH` / `XLOOKUP` |
| `lst_<x>` | key column (or a list formula, §3) | **source of a dropdown** |

Names defined as **structured references grow with the table**: a row added at the bottom of
`tbl_cable` appears in every lookup and dropdown at once (tested in Excel 365 and LibreOffice
24.x reading `.xlsx`). A name to a fixed address (`$B$5:$B$20`) does not grow — a finding in
review.

## 3. Dropdowns (data validation → List)

Source is **always a name** `=lst_<x>`: the data validation box does not accept a structured
reference directly (Microsoft Q&A), and `INDIRECT("tbl_x[Col]")` is volatile and breaks when the
table is renamed.

| Kind | Source | 365 | 21 | 16 | LO | Path |
|---|---|---|---|---|---|---|
| fixed 2–3 values (`YES,NO`) | typed list | ✔ | ✔ | ✔ | ✔ | A, B |
| catalogue key | `lst_x` = `tbl_x[Key]` | ✔ | ✔ | ✔ | ✔ | A, B (`table`) |
| **dependent** — compatible | `lst_child` = `INDEX(c;MATCH(p;P;0)):INDEX(c;MATCH(p;P;0)+COUNTIF(P;p)-1)` on a table **grouped by parent** | ✔ | ✔ | ✔ | ✔ | A, B (`dependent_list`) |
| **dependent** — dynamic array | helper cell `=SORT(UNIQUE(FILTER(tbl_x[Child];tbl_x[Parent]=in_p)))`, name `lst_child` = `'9x'!$H$5#` | ✔ | ✔ | ✘ | ✘ | A only |
| only items that comply | helper cell `=FILTER(tbl_IPE[Name];tbl_IPE[Wel]>=calc_Wreq;"none")`, name → `…#` | ✔ | ✔ | ✘ | ✘ | A only |
| dependent with `INDIRECT` and one named range per parent | — | **don't**: volatile, breaks on spaces and renames, unreliable in LibreOffice | | | | |

Rules:

1. **Parent first, child below it.** A changed parent leaves the old child value in the cell —
   data validation does not re-check it. The child's status cell (engcalc does it for every
   `choices=` input) and a condition `ISNUMBER(MATCH(in_child;lst_child;0))` turn ✘ until the
   user picks again.
2. **The compatible dependent list needs the table grouped by the parent** (equal parents in
   one block). `dependent_list` refuses ungrouped rows at build time; in the workbook add
   `condition(grouped("db_x_parent"))` — somebody will append a row at the bottom.
3. `INDEX:INDEX` typed directly into the validation box can be refused; inside a name it works
   (tested in Excel 365 and LibreOffice).
4. Dynamic-array helper cells live on the `9x_` sheet in a labelled block, never on the
   calculation sheet; the dropdown refers to the spill with `#`. openpyxl cannot write them
   (`fx()` raises) → path A, or the compatible form in path B.
5. **Long lists**: Microsoft 365 desktop autocompletes typed text in a dropdown; older Excel and
   LibreOffice do not. Over ~30 items split into levels (material → size) instead of one list.
6. **Key vs. label**: the dropdown shows the short key; the description (`IPE 200 · 22.4 kg/m`)
   appears next to the input as a lookup, not as a longer key.
7. **Numeric keys** (ratings, sizes): the input cell keeps a number format — a cell formatted
   as text stores the picked `16` as `"16"` and `MATCH` against numbers fails.
8. Stop alert + input message on every list (conditions.md); pasted values bypass validation,
   the status cell catches them.

## 4. Lookup functions — which one

| Question | 365 / 21 | Compatible (16, LO) | engcalc |
|---|---|---|---|
| value for a key | `XLOOKUP(k;db_x_key;db_x_C)` | `INDEX(db_x_C;MATCH(k;db_x_key;0))` | `index_match` |
| value by **several** keys (material + size) | `XLOOKUP(1;(db_x_a=a)*(db_x_b=b);db_x_C)` | `INDEX(db_x_C;MATCH(1;INDEX((db_x_a=a)*(db_x_b=b);0);0))` | `lookup2` |
| cell of a wide table (row × column) | `XLOOKUP(r;rows;XLOOKUP(c;heads;body))` | `INDEX(body;MATCH(r;rows;0);MATCH(c;heads;0))` | — |
| next standard value ≥ x (sections, E-series, breakers) | `XLOOKUP(x;s;s;;1)` | `INDEX(s;MATCH(TRUE;INDEX(s>=x;0);0))` | `next_higher` |
| size range "over … up to" (ISO 286) | — | `INDEX(v;COUNTIF(ub;"<"&x)+1)` | `interval_lookup` |
| interpolation in a table | `FORECAST.LINEAR` around `XMATCH(x;X;-1)` | `MATCH(x;X;1)` + line | toolbox §2 |
| is the value in the catalogue | `ISNUMBER(XMATCH(v;lst))` | `ISNUMBER(MATCH(v;lst;0))` | input status |
| all records that comply | `FILTER(tbl;cond;"none")`, `SORTBY` | helper column + `COUNTIFS` | — |
| totals by category (BOM, losses) | `SUMIFS`, `COUNTIFS`, `MAXIFS`, `MINIFS` | same (`MAXIFS` from 2019, else `AGGREGATE(14;6;…)`) | — |
| whole record (several columns) | `XLOOKUP(k;key;tbl_x[[A]:[D]])`, `CHOOSECOLS` | one `INDEX/MATCH` per column | — |

Rules:

- **Exact match is the default** (`MATCH(…;0)`, `XLOOKUP` default). Approximate match only on a
  column that is strictly ascending, guarded by `condition(ascending(...))`.
- **No `VLOOKUP` / `HLOOKUP` with a column number** — inserting a column moves the result
  silently (ICAEW, Forvis Mazars). Name the result column.
- **`#N/A` is information**: "not in the catalogue". Do not hide it with `IFERROR`; let the
  status say `✘ not in catalogue` (`IFNA` only to produce that text).
- `COUNTIF` / `MATCH` treat `* ? ~` in keys as wildcards — keep them out of keys.
- One lookup per quantity, each in its own `calc` row with the source in col. H; the row that
  picks the record (`MATCH`) can be a `calc` of its own (`calc_irow`) reused by the others.

## 5. Integrity conditions

Every catalogue that a calculation reads gets conditions, on the calculation sheet that uses it
(they feed the banner like any other condition):

| Condition | Formula (engcalc helper) |
|---|---|
| keys unique and not blank | `unique_keys("db_x_key")` |
| references exist in the master | `refs_ok("db_cable_mat", "db_mat_key")` |
| grouped by parent (dependent list) | `grouped("db_x_parent")` |
| ascending (approximate match, `next_higher`, intervals) | `ascending("db_x_key")` |
| numeric column has only numbers | `SUMPRODUCT(--NOT(ISNUMBER(db_x_C)))=0` |
| input within the table range (no extrapolation) | `in_x<=MAX(db_x_key)` |

## 6. Forms — entering records

When the database **is** the product (test log, measurement register, BOM, cable list):

| Tool | Use | Where |
|---|---|---|
| **the Excel table itself** | Tab in the last cell adds a row; data validation, formats and calculated columns copy down | everywhere |
| validation on every column | lists from master tables (`lst_*`), ranges, dates; status column in the table: `=IF(AND(…);"✔";"✘ "&reason)` | everywhere |
| **Data Form** (add *Form…* to the Quick Access Toolbar) | one record per screen, search by criteria; up to 32 columns | Excel desktop (Windows) |
| input sheet + *Save* button (VBA) | guided form, writes the record to the table, clears inputs | desktop Excel only → [vba.md](vba.md) |
| Microsoft Forms → Excel | many people fill in, answers land in a table | Microsoft 365 |
| **Power Query** | import CSV / logger / another workbook into a table, types and units in the query; *Append* new files instead of pasting | 365 / 21 / 16 |
| pivot table + slicers | summaries by category, filtered view of a register | everywhere (LO: pivot table) |
| **Data Model relationships** | several related tables without lookup columns (large registers, ~50 000+ rows) | 365 / 21 desktop |

Above what Excel handles comfortably (many users writing at once, hundreds of thousands of
rows, history of changes) the data belongs in a real database (Access, SQLite, SQL Server) read
into the workbook by Power Query; the workbook stays the calculation.

## 7. Path A and path B

**Path A (live, Claude in Excel)**: Insert → Table, name it `tbl_x`; Name Manager →
`db_x_<col>` = `=tbl_x[Header]`, `lst_x` the same for the key; data validation `=lst_x`.
Dependent list: in 365 the `FILTER` helper on the `9x_` sheet (§3), otherwise the
`INDEX:INDEX` name. Then add the conditions from §5.

**Path B (engcalc)**:

```python
db.table("mat", [Col("key", "Material"), Col("rho", "ρ [Ω·mm²/m]", "0.0000")], rows, source="IEC 60228")
db.table("cable", [Col("key", "Cable"), Col("mat", "Material"), Col("S", "S [mm²]", "0.0"),
                   Col("Iz", "Iz [A]", "0")], rows, source="IEC 60364-5-52 Tab. B.52.4")
db.dependent_list("cable_by_mat", "cable", "key", "mat", "in_mat")   # → lst_cable_by_mat

s.input("in_mat", "Conductor material", "", "Cu", "", choices="lst_mat")
s.input("in_cab", "Cable", "", "Cu 4 C", "", choices="lst_cable_by_mat")   # status ✘ after a material change
s.calc("calc_Iz", "Current-carrying capacity", "I_z", index_match("cable", "Iz", "in_cab"), "A")
s.calc("calc_In", "Breaker rating", "I_n", next_higher("db_breaker_key", "calc_IB"), "A")
s.condition("cond_db", "Cable catalogue consistent",
            f'AND({unique_keys("db_cable_key")},{refs_ok("db_cable_mat", "db_mat_key")},{grouped("db_cable_mat")})',
            ok="keys unique, materials exist, grouped", fail="repair the catalogue")
```

## 8. Review checklist

```
[ ] Every catalogue is an Excel table with a Source row (standard + edition + table)
[ ] Keys unique, no blanks, no wildcards; units in headers; no merged cells or subtotals
[ ] db_/lst_ names are structured references (grow with the table), not fixed addresses
[ ] Every dropdown reads a name lst_*; no INDIRECT, no OFFSET in validation sources
[ ] Dependent dropdown: child below parent, child status ✘ after a parent change (tried)
[ ] No VLOOKUP/HLOOKUP with a column number; approximate match only on ascending data + condition
[ ] #N/A from a lookup shown as a status, not hidden by IFERROR
[ ] Integrity conditions (§5) on every catalogue a calculation reads
[ ] Standard tables transcribed wide and checked against the source; no number typed twice
```

## Literature

- K. W. Broman, K. H. Woo: *Data Organization in Spreadsheets*. The American Statistician
  72 (1), 2018, 2–10, doi:10.1080/00031305.2017.1375989 — open preprint
  [peerj.com/preprints/3183](https://peerj.com/preprints/3183). Consistency, one value per
  cell, rectangle, data dictionary, data validation, no formatting as data.
- Data Carpentry: *Data Organization in Spreadsheets* (lesson, key points)
  [datacarpentry.org](https://datacarpentry.org/spreadsheet-ecology-lesson/key-points.html);
  University of Iowa Libraries: *Data structure best practices*
  [lib.uiowa.edu](https://www.lib.uiowa.edu/data/manage/data-structure/).
- Microsoft: *Using structured references with Excel tables*
  [support.microsoft.com](https://support.microsoft.com/office/using-structured-references-with-excel-tables-f5ed2452-2337-4f71-bed3-c8ae6d2b276e)
  — table and column specifiers, escaping, references that follow added rows.
- Microsoft Q&A: a table cannot be used directly as a list source
  [learn.microsoft.com](https://learn.microsoft.com/en-us/answers/questions/4991963/excel-2016-unable-to-use-named-table-for-list-data);
  workaround with a name: [get-digital-help.com](https://www.get-digital-help.com/how-to-use-a-table-name-in-data-validation-lists-and-conditional-formatting-formulas/),
  [trumpexcel.com](https://trumpexcel.com/data-validation-list-from-excel-table/).
- J. Gross, Excel University: *Dependent Drop Downs with FILTER* — `SORT(UNIQUE(FILTER()))`
  helper and the `#` spill reference
  [excel-university.com](https://www.excel-university.com/dependent-drop-downs-with-filter/);
  *AutoComplete for Data Validation Dropdown Lists*
  [excel-university.com](https://www.excel-university.com/autocomplete-for-data-validation-dropdown-lists/).
- Excel Campus: *Dependent (cascading) drop-down lists* — `MATCH` + `COUNTIF` on a sorted list
  [excelcampus.com](https://www.excelcampus.com/tables/dependent-drop-lists/).
- ICAEW Excel Community (L. Bastick): *INDEX and MATCH*
  [icaew.com](https://www.icaew.com/technical/technology/excel-community/excel-community-articles/2023/index-and-match);
  Forvis Mazars: *Use LOOKUP to replace VLOOKUP and HLOOKUP*
  [financialmodelling.forvismazars.com](https://financialmodelling.forvismazars.com/resources/use-lookup-to-replace-vlookup-and-hlookup-functions-in-excel/)
  — why a column number in a lookup is a modelling risk.
- Microsoft Learn: *Data model relationships*
  [learn.microsoft.com](https://learn.microsoft.com/en-us/training/modules/modern-analytics-data-modeling/2-data-model-relationships)
  — keys, cardinality, one active relationship.
- LibreOffice Bugzilla, reports on structured references and validity lists
  ([139499](https://www.libreoffice.org/bugzilla/show_bug.cgi?id=139499),
  [153221](https://www.libreoffice.org/bugzilla/show_bug.cgi?id=153221)): reported that a
  structured reference saved to `.ods` becomes a fixed range (ODF has no structured
  references). Read from `.xlsx` they work (tested here) — keep LibreOffice workbooks in `.xlsx`.
