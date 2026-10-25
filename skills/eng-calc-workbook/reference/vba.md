# VBA — jen desktop Excel

Claude in Excel ani Excel na webu makra nespouští. VBA použij jen tam, kde vzorec nestačí
(UDF pro složitý algoritmus, export, tlačítka v desktopovém nástroji), a sešit musí fungovat
i bez maker (vstupy, posudky a banner zůstávají vzorce).

- Dodávej čistý `.xlsx` + samostatný `.bas`; programově generovaný `.xlsm` se rozbíjí.
- `Option Explicit` v každém modulu, explicitní typy (`As Double`), `ByVal` u vstupů.
- Moduly: `modConstants` (Const s jednotkou v komentáři), `modCalc_<oblast>` (čisté UDF bez
  `Range`/`ActiveSheet`), `modIO` (jediné čtení/zápis listu, validace vstupů), `modUI` (tlačítka).
- Hlavička UDF: popis, každý parametr s jednotkou, návratová jednotka.
- Chyby: `Err.Raise vbObjectError + N, "Funkce", "srozumitelný text"`; makra s vedlejšími
  efekty `On Error GoTo ErrHandler`, v handleru obnovit `ScreenUpdating/Calculation/EnableEvents`.
  Plošné `On Error Resume Next` jen s okamžitou kontrolou `Err.Number` a `On Error GoTo 0`.
- Výkon: rozsah načíst do pole `Variant`, počítat v paměti, zapsat najednou.
- Test: `Sub Test_<UDF>()` s pevnými vstupy a `Debug.Assert Abs(x - ocek) < tol`, nebo list
  `TestCases` (vstupy | očekávané | tolerance) s makrem, které hlásí neshody.
- UDF výsledek vstupuje do calc padu jako normální `calc` řádek se zdrojem „UDF modCalc_X.Funkce“.
