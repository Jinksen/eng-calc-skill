# VBA — desktop Excel only

Neither Claude in Excel nor Excel for the web runs macros. Use VBA only where a formula is not
enough (a UDF for a complex algorithm, export, buttons in a desktop tool, placing shapes from
coordinates), and the workbook must work without macros too (inputs, checks and the banner
stay formulas).

- Deliver a clean `.xlsx` + a separate `.bas`; a programmatically generated `.xlsm` breaks easily.
- `Option Explicit` in every module, explicit types (`As Double`), `ByVal` for inputs.
- First line of every `.bas`: `Attribute VB_Name = "modCalc_x"` (the VBA editor writes it on
  export; `vba_run.ps1` needs it). Line endings CRLF.
- Modules: `modConstants` (Const with the unit in a comment), `modCalc_<area>` (pure UDFs
  without `Range`/`ActiveSheet`), `modIO` (the only reading / writing of sheets, input
  validation), `modUI` (buttons).
- UDF header: description, every parameter with its unit, the return unit.
- Errors: `Err.Raise vbObjectError + N, "Function", "clear text"`; macros with side effects use
  `On Error GoTo ErrHandler` and restore `ScreenUpdating/Calculation/EnableEvents` in the
  handler. Blanket `On Error Resume Next` only with an immediate `Err.Number` check and
  `On Error GoTo 0`.
- Performance: read a range into a `Variant` array, compute in memory, write back at once.
- Tests: `Sub Test_<UDF>()` with fixed inputs that **raises** on a mismatch
  (`If Abs(x - expected) > tol Then Err.Raise …`), or a `TestCases` sheet (inputs | expected |
  tolerance) with a macro that raises listing the mismatches. Not `Debug.Assert`: it stops in
  the debugger, which a hidden Excel started by a script never shows. Pattern:
  [`scripts/example_udf.bas`](../scripts/example_udf.bas).
- A UDF result enters the calc pad as a normal `calc` row with the source "UDF modCalc_X.Function".
- Shapes from macros (desktop): `ws.Shapes.AddShape` / `AddLine` / `AddConnector` with
  positions computed from cells — the only way to generate real shapes (openpyxl cannot).

## Running the macros (Claude Code on Windows with desktop Excel)

Where the agent has a shell on Windows with desktop Excel installed, it does not stop at
writing the `.bas`: it imports it and runs the tests through COM.

```
powershell -NoProfile -File scripts/vba_run.ps1 book.xlsx -Modules modCalc_x.bas -Run Test_A,Test_B
```

Opens the workbook in a hidden Excel, imports the modules (a module of the same name is
replaced), saves `book.xlsm` next to it (`-Out` for another path), runs every `-Run` macro and
prints `PASS` / `FAIL` with the error text. Exit 0 all passed · 1 a test failed · 2 setup
error. The input `.xlsx` is never changed; an existing `.xlsm` is overwritten only with `-Force`.
Excel is always closed at the end, also after an error.

**One-time setup by the user — never by the agent.** Importing code needs *File → Options →
Trust Center → Trust Center Settings → Macro Settings → Trust access to the VBA project object
model*. It is a security setting: any program running as the user can then read and write VBA
in every workbook they open. When `vba_run.ps1` reports "no access to the VBA project", tell the
user what the setting does and let them decide; offer to remind them to switch it off again.

Risks and limits — say them to the user when you use this route:

- **Windows + desktop Excel only.** Not in claude.ai, Claude in Excel, Excel for the web, Mac
  (COM) or CI (the Ubuntu runner has no Excel). The formula workbook stays the deliverable;
  the `.xlsm` is an extra.
- **Macros run with the user's rights.** Run only code you wrote in this session or the user
  gave you and you read. `vba_run.ps1` opens the workbook with events off, so a foreign
  `Workbook_Open` does not fire, but an imported or existing macro called by `-Run` does
  anything it is written to do.
- **Open workbooks.** The script starts its own Excel instance, but a workbook already open
  in the user's Excel is locked: close it first or pass a copy.
- **Modal dialogs hang the script.** `MsgBox`, `InputBox` or a UserForm in a tested macro waits
  for a click nobody sees. Keep them in `modUI`, never in what `-Run` calls; run the script in
  the background with a timeout and kill `EXCEL.EXE` it started if it times out.
- **Signing and distribution.** The generated `.xlsm` is unsigned; on another PC macros are
  blocked (Mark of the Web, macro policy) until the user trusts the file or its location.
  Do not tell anyone to lower their macro security level.
- **Review shows macros.** A review (path C) lists every module and what it touches
  ([review.md](review.md) step 1).
