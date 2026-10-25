# Changelog

## 0.2.0 — 2026-10-25

- `SKILL.md`: úvod „Pro agenta — o co jde“ a tabulka souvisejících skillů, které agent načte automaticky (`xlsx`, `electrical-machine-calc`, `dataviz`, `freecad-qelectrotech`, `ilogic-inventor`, `pdf`); popis skillu rozšířen o vizualizaci dílů a dashboardy.
- `reference/part-drawing.md`: parametrický výkres / řez dílu v Excelu — obrys z kót, šrafy, osa, kóty s tolerancemi (ISO 286, ISO 2768), rozměrový řetězec, GD&T (ISO 1101), rohové razítko (ISO 7200).
- `reference/dashboard-widgets.md`: panely Parametry/Výstup, posuvníky, číselníky, přepínače, ukazatel hladiny, digitální displej, stupnice, gradientní grafy, vývojové diagramy z tvarů; omezení openpyxl na tvary.
- `excel-toolbox.md` §0: základní sada inženýra (dohledání, logika, statistika, kusovník přes `SUMIFS`, `RANK.EQ`/`PERCENTILE`, `CONVERT`, Bessel, komplexní čísla, bity, `ERF`, Řešitel).
- `patterns.md` P21–P26, `domains.md`: tolerance a uložení, díl z výkresu.
- Repozitář: jediná kopie skillu v `skills/eng-calc-workbook/`.

## 0.1.0 — 2026-10-25

- Sloučeny dřívější skilly `excel-design`, `python-openpyxl-engineering`, `vba-excel-engineering`.
- Vizuální jazyk z referenčních inženýrských sešitů (hlavička, banner, calc pad, akcent oboru).
- Tři vrstvy podmínek: vstupy, posudky η ✔/▲/✘ + podmínky platnosti, banner; registr `80_Kontroly`.
- Cesta A pro Claude in Excel (jen nativní Excel), cesta B `engcalc.py`, revize, ticket režim.
- Referenční build: posudek nosníku IPE (ČSN EN 1993-1-1), živá skica průřezu, M(x), w(x), graf využití.
- `reference/excel-toolbox.md`: katalog funkcí Excelu podle úkolu a verze (vyhledávání, interpolace, komplexní čísla, matice, statistika, inženýrské funkce, numerika, Power Query).
- `reference/sheet-styles.md`: kompaktní posudkový list ve stylu TCC jako preferovaný hlavní list; excel-toolbox §10–13 vizuál buněk, obrázky v buňce, tvary propojené na buňky, grafy, vstupy.
- `fx()`: `_xlfn.` prefixy i pro statistické funkce Excel 2010+ a funkce Excel 2013+.
- `verify.py`: přepočet LibreOffice, lint (magická čísla, volatilní funkce, vstupy bez ověření, adresy mezi listy), render.
