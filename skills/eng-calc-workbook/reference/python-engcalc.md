# Cesta B — generovaný soubor (`scripts/engcalc.py`)

Python 3.10+, `openpyxl>=3.1`, `Pillow`; `matplotlib` pro rovnice a skici; LibreOffice +
`pdftoppm` pro `verify.py`. Knihovnu zkopíruj vedle build skriptu nebo přidej `scripts/` do `sys.path`.

## Postup

1. Specifikaci (SKILL.md §1) přepiš do build skriptu `build_<nazev>.py` podle
   `scripts/example_ipe_beam.py` — pořadí: databáze → výpočtové listy → data grafů → přehled → README.
2. `python build_<nazev>.py out/<nazev>_v1.0_RRRR-MM-DD.xlsx`
3. `python scripts/verify.py out/<soubor>.xlsx --render out/render` → exit 0
   (1 = lint varování, 2 = chybové hodnoty), prohlédni PNG stránky.
4. Uživateli předej `.xlsx` (a build skript, pokud bude sešit generovat znovu).

## API

```python
from engcalc import EngWorkbook, Meta, Col, index_match, xy_chart, sketch_chart, png_from_figure, fx, let

book = EngWorkbook(Meta(project=…, title=…, subject=…, author=…, date=dt.date(…),
                        organisation=…, standard=…, domain="electrical"))   # | mechanical | civil

db = book.data_sheet("90_Databaze", "Databáze", "účel pro README")
db.table("cable", [Col("key", "Průřez"), Col("Iz", "Iz [A]", "0")], rows, source="ČSN … Tab. …")
#  → tbl_cable, db_cable_Iz, db_cable_key, lst_cable
db.close()

s = book.calc_sheet("10_Vypocet", "Název listu", "účel pro README")
s.section("Vstupní údaje");  s.subsection("…");  s.comment("…")
s.input("in_L", "Délka", "L", 25, "m", lo=1, hi=500)                 # rozsah povinný
s.input("in_cs", "Průřez", "S", "16", "mm²", choices="lst_cable")
s.const("c_rho", "Rezistivita Cu", "ρ", 0.0175, "Ω·mm²/m", source="…", fmt="0.0000")
s.calc("calc_R", "Odpor vedení", "R", "c_rho*2*in_L/in_S", "Ω", text="R = ρ·2L/S", fmt="0.000")
s.result("out_dU", …)
s.check("chk_dU", "Úbytek napětí", "η_ΔU", value="out_dU", limit="in_dUmax", unit="%", kind="le", dec=2, source="…")
s.condition("chk_rng", "Platnost vzorce", "calc_Re>4000", ok="turbulentní", fail="mimo rozsah", source="…")
s.remark("Režim", 'IF(calc_Re>4000,"turbulentní","laminární")')
s.equation(r"R=\rho\,\frac{2L}{S}")      # matplotlib mathtext → obrázek
s.figure(png_bytes, width_px=430);  s.chart(chart, rows=16)
s.close()                                 # povinné: CF stavů, rozsah vstupů, tisk

gd = book.data_sheet("91_Grafdata", …)
blk = gd.block("diag", [Col("x", "x [m]"), Col("M", "M [kNm]")], [("=…", "=…"), …], note="vztahy")
d = book.dashboard("01_Prehled", "Přehled", "…")
d.kpis([("popisek", "=out_x", "jedn.", "0.0"), …]);  d.chart(xy_chart(…), "E13")
d.utilization_chart("B39");  d.figure(png, "B28", width_px=250);  d.close(52)

book.readme(purpose=…, scope=[…], assumptions=[…], workflow=[…], sources=[…], revisions=[(…)])
book.save(path)                           # řadí listy, staví registr, grafy využití, README, zámek
```

Každá veličina se zapisuje pod jménem; vzorce používají jména. Knihovna sama:
přiřadí styl `ec_link` vzorcům čerpajícím z jiného listu, očísluje kroky, vytvoří ověření dat,
stavové vzorce, registr, banner, graf využití, legendu a obsah README.

## Úskalí openpyxl (knihovna je řeší, při ručním psaní ne)

| Problém | Řešení |
|---|---|
| Funkce Excel 2010+ (`IFS`, `XLOOKUP`, `SHEET`, `TEXTJOIN`, `CONCAT`, `MAXIFS`…) → `#NAME?` | prefix `_xlfn.` — `fx()` doplní automaticky |
| `LET` / `LAMBDA` | parametry s `_xlpm.` — helper `let({"a": "…"}, "{a}*2")`; LibreOffice < 24.8 neumí |
| Dynamická pole (`FILTER`, `SORT`, `UNIQUE`, `SEQUENCE`) | openpyxl je zapíše jako starý maticový vzorec → `fx()` hází chybu; napsat ručně v Excelu |
| `XLOOKUP` v LibreOffice < 24.8 | `index_match()` funguje všude |
| `TEXT(x,"0.0")` závisí na lokalizaci | `FIXED(x,1)` |
| Prázdná textová buňka v odkazu ukáže 0 | `=meta_x&""` |
| Hodnoty vzorců openpyxl nepočítá | `verify.py` (LibreOffice headless) |
| Data bar / rozšíření CF po uložení LibreOffice | jen varování při čtení, výsledek v Excelu v pořádku |
| Obrázky z `BytesIO` | nechat buffer otevřený do `save()` (knihovna drží referenci) |

## Rozšíření knihovny

Nový typ řádku/grafu přidej jako metodu `CalcSheet`/funkci v `engcalc.py`, doplň ho do
`example_ipe_beam.py` (nebo nového referenčního buildu) a ověř `verify.py` — nový prvek
bez referenčního použití nemá v knihovně místo.
