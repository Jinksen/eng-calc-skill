# Conditions, checks, statuses

Formulas are in English syntax (that is how they are stored in the file and how Claude in
Excel writes them through the API). In a localised Excel the user sees them with the local
separators (e.g. semicolons) — behaviour is the same.

## Status convention

The first character of the status text carries the meaning; conditional formatting and
counting rely on it.

| Char | Text | When |
|---|---|---|
| ✔ | `✔ OK`, `✔ within limits`, `✔ <assumption text>` | η ≤ `cfg_eta_warn`, condition met |
| ▲ | `▲ OK – low reserve` | `cfg_eta_warn` < η ≤ 1 |
| ✘ | `✘ FAILS`, `✘ out of range`, `✘ CANNOT EVALUATE` | η > 1, error, assumption not met |
| – | `–` | not evaluated (η of boolean conditions) |

`cfg_eta_warn` = 0.90 (input on `80_Checks`, range 0.5–1.0). The user may tighten it.

## 1. Input

Data validation: *decimal between* lo and hi, error alert of type **Stop**, input message
`lo … hi unit`. Selection: *list* with source `=lst_<table>`.

Column G: `⟨lo ; hi⟩ unit`. Column I (also catches values pasted in, which bypass validation):

```
=IF(AND(ISNUMBER($E12),$E12>=1,$E12<=12),"✔ within limits","✘ out of range")
=IF(ISNUMBER(MATCH($E15,lst_IPE,0)),"✔ from list","✘ not in list")
```

Input limits are the only place where a number may sit directly in a formula (they are
documented in col. G).

## 2. Check

`le`: effect ≤ resistance → η = effect / resistance. `ge`: value ≥ minimum → η = minimum / value.

| Col. | Content |
|---|---|
| D | `η_M =` |
| E | `=(out_MEd)/(out_McRd)` format `0.00`, bold, named `chk_M` |
| F | `–` |
| G | `=FIXED(out_MEd,1)&" ≤ "&FIXED(out_McRd,1)&" kNm"` |
| H | clause of the standard |
| I | status (below) |

```
=IF(NOT(ISNUMBER($E40)),"✘ CANNOT EVALUATE",
 IF($E40>1,"✘ FAILS",
 IF($E40>cfg_eta_warn,"▲ OK – low reserve","✔ OK")))
```

`FIXED`, not `TEXT`: the format string of `TEXT` depends on the locale (`"0.0"` does not work
in every language version), `FIXED` does not.

A range check (lo ≤ x ≤ hi) is split into two rows `ge` and `le` — each with its own η.

**`ge` check with a value that can reach zero or go negative** (gap, wall, edge distance):
write the value as `MAX(x,1e-6)` — otherwise η = minimum / value becomes negative and shows
✔. With the guard η jumps to a huge number and the status is ✘.

## 3. Validity condition

Assumption of the method, regime, class — boolean. E: `=IF(cond,"YES","NO")`, I:

```
=IF(out_VEd<=0.5*out_VplRd,"✔ no reduction","✘ reduction 6.2.8 required")
```

Use for: scope of the method (Re for a formula, slenderness, section class, frequency, size
range of a table), assumptions (LTB restrained, steady state, linear material), choice of a
calculation branch.

## 4. Dynamic remark

Interpretation for the reader, bold italic NOTE_FONT in col. E (overflows to the right):

```
=IF(calc_Re>4000,"Re > 4000 → turbulent flow, f from Colebrook",
 IF(calc_Re<2300,"Re < 2300 → laminar, f = 64/Re","transition region – result uncertain"))
```

When a remark says "out of scope", add a `condition` so that the banner catches it.

## 5. Register `80_Checks`

Table from row 11: `# | Check | Symbol | η | Status | Sheet | Link | fail | warn`.
Numeric checks first (the utilisation chart reads a contiguous η block), then conditions,
then one row "Inputs of sheet X within allowed limits" per calculation sheet:

```
η:      =IF(ISNUMBER('10_Beam'!$E$40),'10_Beam'!$E$40,"–")
Status: ='10_Beam'!$I$40
Link:   =HYPERLINK("#'10_Beam'!C40","→ row 40")
fail:   =IF(LEFT(F11,1)="✘",1,0)
warn:   =IF(LEFT(F11,1)="▲",1,0)
inputs: =IF(COUNTIF('10_Beam'!$I$12:$I$18,"✘*")=0,"✔ all inputs within limits",
         "✘ inputs out of range: "&COUNTIF('10_Beam'!$I$12:$I$18,"✘*"))
```

Names: `chk_eta` (col. E), `chk_fail` (col. I), `chk_warn` (col. J). Data bar on η: min 0,
max 1.2, BLUE. The register is generated — the only sheet where references are addresses
instead of names.

## 6. Banner (row 5 of every sheet)

```
=IF(SUM(chk_fail)>0,"✘ FAILS – conditions not met: "&SUM(chk_fail),
 IF(SUM(chk_warn)>0,"▲ OK WITH LOW RESERVE – checks: "&SUM(chk_warn),
 "✔ ALL CHECKS AND CONDITIONS SATISFIED"))
 &"     η max = "&IF(COUNT(chk_eta)>0,FIXED(MAX(chk_eta),2),"–")
```

## 7. Conditional formatting

One set of rules for the whole status column of a sheet (`I9:I<last>`), formula with a
relative row, in this order, *stop if true*:

| Rule (formula) | Fill | Font |
|---|---|---|
| `LEFT($I9,1)="✘"` | `FFC7CE` | `9C0006` bold |
| `LEFT($I9,1)="▲"` | `FFEB9C` | `9C5700` bold |
| `LEFT($I9,1)="✔"` | `C6EFCE` | `006100` bold |
| `LEFT($I9,1)="–"` | `EDEDED` | `595959` |

Plus on the value column `E9:E<last>`: `LEFT($I9,1)="✘"` → FAIL fill (an input out of range
and a failing η turn red right in the value). The same four rules on the banner (`$B$5`).
No icons or colour scales on statuses — text + colour is enough and prints.
