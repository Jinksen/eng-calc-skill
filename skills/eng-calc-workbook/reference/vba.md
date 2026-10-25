# VBA — desktop Excel only

Neither Claude in Excel nor Excel for the web runs macros. Use VBA only where a formula is not
enough (a UDF for a complex algorithm, export, buttons in a desktop tool, placing shapes from
coordinates), and the workbook must work without macros too (inputs, checks and the banner
stay formulas).

- Deliver a clean `.xlsx` + a separate `.bas`; a programmatically generated `.xlsm` breaks easily.
- `Option Explicit` in every module, explicit types (`As Double`), `ByVal` for inputs.
- Modules: `modConstants` (Const with the unit in a comment), `modCalc_<area>` (pure UDFs
  without `Range`/`ActiveSheet`), `modIO` (the only reading / writing of sheets, input
  validation), `modUI` (buttons).
- UDF header: description, every parameter with its unit, the return unit.
- Errors: `Err.Raise vbObjectError + N, "Function", "clear text"`; macros with side effects use
  `On Error GoTo ErrHandler` and restore `ScreenUpdating/Calculation/EnableEvents` in the
  handler. Blanket `On Error Resume Next` only with an immediate `Err.Number` check and
  `On Error GoTo 0`.
- Performance: read a range into a `Variant` array, compute in memory, write back at once.
- Tests: `Sub Test_<UDF>()` with fixed inputs and `Debug.Assert Abs(x - expected) < tol`, or a
  `TestCases` sheet (inputs | expected | tolerance) with a macro that reports mismatches.
- A UDF result enters the calc pad as a normal `calc` row with the source "UDF modCalc_X.Function".
- Shapes from macros (desktop): `ws.Shapes.AddShape` / `AddLine` / `AddConnector` with
  positions computed from cells — the only way to generate real shapes (openpyxl cannot).
