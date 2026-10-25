# Path C — review of an existing workbook

Output of a review: a table of findings sorted by severity + a recommendation whether to fix
in place (path A), rebuild (B) or split into tickets (D).

## Procedure

1. Inventory: sheets, hidden sheets / rows / columns, named ranges, external links, macros.
2. Where are the inputs? (scattered through the calculation = finding)
3. Go through every calculation formula (Ctrl+` / openpyxl) and look for the patterns below.
4. Independently recompute at least one key result; state the value and the deviation.
5. Try the edges: zero, a negative value, an input beyond a sensible limit — what does the workbook do?
6. Path B available → `verify.py` (the lint finds magic numbers, volatile functions, inputs without validation).

## Severity

| Level | Examples |
|---|---|
| **Critical** — the result may be wrong | wrong unit / conversion, reference to the wrong row, inconsistent formula in a range, `IFERROR` hiding an error, a missing check the method requires, silently continuing outside the method's validity, two names differing only in case |
| **High** — cannot be verified | magic numbers without a source, no checks, no reference case, hidden calculations |
| **Medium** — fragile | inputs without data validation, merged cells in the calculation, volatile functions, links to other files |
| **Low** — readability | missing units / symbols, inconsistent formats, false precision, no README / version |

For every finding: location (sheet!cell or name), why it matters, the fix in one sentence.
