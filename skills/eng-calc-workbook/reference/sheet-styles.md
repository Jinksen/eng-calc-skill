# Calculation sheet styles

Two styles, same data, same conditions ([conditions.md](conditions.md)), same names.
They differ in layout and density. A third, **R — printable report**, only reads from them:
[report-sheet.md](report-sheet.md).

| | **K — compact check sheet** (preferred) | **P — calc pad** |
|---|---|---|
| Model | TCC / The Concrete Centre sheets, hand-written structural calculation | step-by-step report |
| When | main check sheet, 1 A4 page per member | long derivations, design methods (machine, winding), review |
| Density | 2 quantities per row, load case tables | 1 quantity per row |
| `engcalc.py` | not yet (ticket 12) — path A | `CalcSheet` |

Combination: sheet K as the summary check, sheet P as the record of intermediate steps on another sheet.

## Style K — anatomy (top to bottom, A4 portrait)

1. **Identification strip** (9 pt grey, thin grid): source / template · © · rev. (input) · sheet x/y · date.
2. **Title** 16 pt bold CAPITALS on the left; top right an **idealised sketch with loads**
   (picture or group of shapes; forces red, reactions blue, dimensions black italic).
3. **Section** = red bold heading in CAPITALS 13 pt `C00000`, no fill, with units in
   brackets in normal font: `DIMENSIONS (mm)`.
4. **Quantity row**: `description symbol =` right aligned | value centred | unit.
   Symbol in italics, index as subscript (Format Cells → Subscript on part of the text, or
   Unicode ₀ ₁ ᵣ ₐ). **Input = blue underlined font `0000FF`**, no fill; calculation and
   catalogue values black. Two quantities side by side (left and right block of columns).
5. **Load case / combination table**: italic bold header in a frame, columns LC 1, LC 2
   (or unfavourable / favourable), inputs blue underlined.
6. **DESIGN STATUS** to the right of the loads: red label + `OK` green `00B050` /
   `FAILS` red, + η max. Below it a **utilisation chart**: horizontal bars, each check its own
   colour, axis 0–125 %, vertical red line at 100 %, light blue plot background `DEEBF7` with
   rounded corners.
7. **CALCULATION AND CHECKS**: table LC 1 | LC 2 | √ | relation. Check rows bold, the √ column
   green (✘ red), **relation in italics on the right** (`L_req / L₁₀ₕ ≤ 1`, "see equation on
   sheet Refs"). Below the table a remark in brackets in italics (what governs, what is neglected).
8. **ASSUMPTIONS** in dark blue italics; items `a)` `b)` … with a red letter, in 2–3 columns.
9. Footer: colour legend, reference to the standard.

Banners and the register from style P apply here too: `DESIGN STATUS` is the banner, check rows
are in `80_Checks`. Page frame: vertical blue lines on the left and right (borders of columns A and L).

## Style K — technique in Excel

| Element | How |
|---|---|
| grid | hidden; a fine grid only in the identification strip |
| column widths | narrow grid (e.g. 12 columns of ~6–9 characters), sections aligned to it; nothing merged, labels overflow to the left via *Align right* |
| blue underlined input | cell style `ec_input_k` (blue, underlined, unlocked) + data validation |
| design status | formula + conditional formatting (green / red), style `ec_status_k` |
| utilisation chart | bar chart from `chk_eta`, *Format Data Point → vary colours by point*, axis max 1.25, 100 % line as a second series (XY) or an error bar |
| sketch | picture (Insert → Pictures → Place over Cells) or a group of shapes; dimension texts linked to cells (`=calc_h` in a text box) |
| relations | italic text; the key equation as an Equation object (Insert → Equation) |

## Style P

See [visual-language.md](visual-language.md) — column grid A–J, dark section bars, yellow
inputs. Implemented by `engcalc.py`.
