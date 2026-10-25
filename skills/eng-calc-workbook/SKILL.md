---
name: eng-calc-workbook
description: >
  Inženýrský výpočtový sešit v Excelu (elektro, strojní, stavební): kalkulátor,
  posudek, návrh, protokol měření nebo dashboard s podmínkami „vyhovuje / nevyhovuje“,
  včetně vizualizace v sešitu — parametrický výkres / řez dílu s kótami a tolerancemi,
  živá skica, interaktivní dashboard (posuvníky, přepínače, ukazatele), tvary a schémata.
  Použij, když uživatel vytváří, přestavuje nebo kontroluje .xlsx s technickým výpočtem,
  chce v Excelu nakreslit nebo vizualizovat díl, průřez, sestavu či průběh, ptá se jak
  výpočet v Excelu uspořádat, pracuje přímo v sešitu přes Claude in Excel, nebo chce
  rozpadnout větší výpočtový sešit na tickety. Platí i pro LibreOffice Calc.
---

# Inženýrský výpočtový sešit

## Pro agenta — o co jde (přečti první)

- **Kdo a proč**: uživatel je český inženýr (elektro / strojní / stavební). Chce sešity,
  které obstojí jako příloha technické zprávy: dohledatelné vstupy, zdroje z norem,
  viditelné posudky, a **hodně vizuálu** — skici a výkresy dílů, grafy, ovládací prvky.
- **Co odevzdáváš**: buď změny přímo v otevřeném sešitu (Claude in Excel), nebo `.xlsx`
  vygenerovaný `scripts/engcalc.py`. Vždy ověřený (§6) a s ruční kontrolou v odpovědi.
- **Jazyk**: listy, popisky, README i odpovědi česky; desetinná čárka v textu, vzorce
  podle lokalizace prostředí. Normy ČSN EN, jednotky SI.
- **Vizualizace je výpočet**: každý obrázek, tvar, kóta či ukazatel je propojený s buňkou a
  mění se se vstupy. Kreslení dílu → [reference/part-drawing.md](reference/part-drawing.md),
  dashboard s ovládacími prvky → [reference/dashboard-widgets.md](reference/dashboard-widgets.md).
- **Neodhaduj**: hodnota z normy bez zdroje, extrapolace mimo tabulku nebo vymyšlený vstup
  je chyba. Ptej se, nebo zapiš předpoklad do README.

### Související skilly — načti je automaticky, když jsou k dispozici

Skill sám jiný skill spustit neumí; ty (agent) ano. Když máš nástroj na skills a úloha
odpovídá řádku, **načti ho hned po tomto skillu, bez ptaní**. Když není dostupný, pokračuj
jen s tímto.

| Když úloha obsahuje | Načti | Na co |
|---|---|---|
| čtení / zápis souborů `.xlsx`, přepočet vzorců | `xlsx` | práce se souborem, recalc |
| asynchronní motor, transformátor, generátor, JTP/MTP | `electrical-machine-calc` | metodika výpočtu stroje |
| grafy, barvy sérií, dashboard mimo Excel (HTML) | `dataviz` | pravidla grafů |
| schéma elektroinstalace, výkres v QElectroTech / FreeCAD | `freecad-qelectrotech` | výkres mimo Excel |
| díl z Inventoru (parametry, iLogic) | `ilogic-inventor` | převzetí rozměrů a parametrů |
| PDF normy nebo katalogu jako zdroj | `pdf` | vytažení tabulek |

Tento skill **nahrazuje** dřívější `excel-design`, `python-openpyxl-engineering` a
`vba-excel-engineering`. Jsou-li zapnuté současně, platí pravidla tohoto skillu.

Cíl: **calc pad** — sešit, který se čte jako ruční výpočet ve zprávě. Shora dolů:
hlavička → **banner stavu** → vstupy → kroky výpočtu → **posudky** → výsledek.
Každá podmínka má využití **η** a stav ✔ / ▲ / ✘; jeden banner nahoře říká, jestli se
výsledek smí použít. Kdokoli za rok musí umět odpovědět: odkud je to číslo, co smím
měnit, čím je to ověřené, kde končí platnost.

Vizuální jazyk (barvy, mřížka sloupců, styly, hlavička) je **jediný zdroj pravdy** v
[reference/visual-language.md](reference/visual-language.md). Vzorce stavů, banneru a
pravidla podmíněného formátování v [reference/conditions.md](reference/conditions.md).
Obě cesty sestavení (A i B) z nich vycházejí beze změny.

## 0. Urči cestu

| Prostředí | Cesta |
|---|---|
| Claude in Excel, nebo uživatel chce úpravy přímo v otevřeném sešitu | **A – živě v sešitu** → [reference/excel-in-place.md](reference/excel-in-place.md) |
| Máš shell + Python (claude.ai, Claude Code) a výstupem je soubor | **B – generovaný soubor** → [reference/python-engcalc.md](reference/python-engcalc.md) |
| Uživatel přinesl existující sešit ke kontrole | **C – revize**: krok 1, pak [reference/review.md](reference/review.md) |
| Víc než ~3 listy výpočtu nebo víc posudků, než se vejde do jedné session | **D – tickety** → [reference/tickets.md](reference/tickets.md), pak A/B po ticketech |

Hotovo, když je cesta zvolená a příslušný reference soubor načtený.

## 1. Specifikace výpočtu (před první buňkou)

Sepiš a nech uživatele potvrdit tabulku — bez ní se nestaví:

| Položka | Obsah |
|---|---|
| Účel a obor | co se posuzuje, elektro / strojní / stavební (určuje akcent barvy) |
| Vstupy | symbol, popis, jednotka SI, **min–max** nebo **seznam**, zdroj |
| Konstanty | hodnota, jednotka, **norma + článek / tabulka** |
| Databáze | katalogy (průřezy, kabely, materiály) → listy `9x_` |
| Kroky | vztah zápisem + zdroj, v pořadí výpočtu |
| Posudky | „účinek ≤ odolnost“ nebo „hodnota ≥ minimum“ → η, zdroj podmínky |
| Podmínky platnosti | předpoklady metody (režim, rozsah, třída) → `condition` řádky |
| Referenční případ | známý výsledek (příklad z normy/literatury, ruční výpočet) pro ověření |
| Cílová platforma | Excel 365 / 2021 / 2016 / LibreOffice — rozhoduje, které funkce smíš použít |

Chybějící parametr nedomýšlej — zeptej se, nebo ho označ jako předpoklad do README.
Hotovo, když má každý posudek obě strany nerovnosti a zdroj, každý vstup rozsah.

Pro obor sáhni do [reference/domains.md](reference/domains.md) (typické posudky a meze
pro elektro / strojní / stavební).

## 2. Kostra sešitu

| List | Obsah |
|---|---|
| `00_README` | identifikace (pojmenované `meta_*`), účel, rozsah platnosti, předpoklady, postup, legenda, obsah s odkazy, zdroje, revizní log |
| `01_Prehled` | dashboard: banner, KPI dlaždice, živá skica, průběhy, graf využití — **jen odkazy** |
| `1x_*` | výpočtové listy (calc pad), jeden na logický celek |
| `80_Kontroly` | registr všech posudků a podmínek, `cfg_eta_warn`, souhrnné `chk_eta/chk_fail/chk_warn` |
| `9x_*` | databáze (Excel tabulky) a data grafů |

Tok dat jedním směrem: vstupy → výpočet → posudky → přehled. Názvy listů `NN_Ascii`.
Žádné skryté listy/řádky. Hotovo, když všechny listy existují s hlavičkou a bannerem.

## 3. Výpočtový list

**Styl** podle [reference/sheet-styles.md](reference/sheet-styles.md): hlavní posudek jako
**kompaktní posudkový list K** (styl TCC: červené sekce, modré podtržené vstupy, skica se
zatížením vpravo nahoře, stav návrhu s grafem využití, tabulka zatěžovacích stavů se vztahy,
předpoklady a)–f)); dlouhá odvození jako **calc pad P**. Obsah a pravidla níže platí pro oba.

**Vizuál naplno**: buňkové styly a motiv, vlastní formáty čísel, podmíněné formátování,
datové pruhy, minigrafy, obrázky v buňce měněné výběrem, tvary s textem propojeným na buňky,
živé skici z grafů, propojené obrázky — katalog v [reference/excel-toolbox.md](reference/excel-toolbox.md) §10–13.

### Řádek po řádku

Jeden řádek = jedna veličina. Sloupce B–I: `# | Veličina | Symbol = | Hodnota | Jedn. |
Vztah / podmínka | Zdroj / norma | Mez / stav`. Typy řádků:

| Typ | Buňka hodnoty | Stav (sl. I) | Povinné |
|---|---|---|---|
| **input** | žlutá, modré písmo, odemčená, ověření dat | ✔ v mezích / ✘ mimo rozsah | min–max nebo seznam |
| **select** | modrozelená, seznam z `lst_*` | ✔ ze seznamu | číselník v `9x_` |
| **const** | fialová | — | zdroj (norma, článek) |
| **calc** | vzorec, černě (zeleně = z jiného listu) | — | vztah zápisem ve sl. G |
| **check** | η = účinek/odolnost | ✔ / ▲ / ✘ | obě strany + zdroj |
| **condition** | ANO/NE | ✔ text / ✘ text | text předpokladu |
| **remark** | dynamický text (`IF` režimu) | — | — |
| **result** | oranžová, tučný rámeček | — | — |

Každá veličina dostane **pojmenovanou oblast** (`in_`, `c_`, `calc_`, `out_`, `chk_`,
`db_`, `lst_`, `gd_`, `cfg_`, `meta_`) a vzorce pracují se jmény: `=calc_qEd*in_L^2/8`.
Číslo ve vzorci jen jako součást zapsaného vztahu (ve sl. G) nebo převod jednotek.
Hotovo, když nemá žádný řádek prázdný symbol, jednotku nebo (u const/check) zdroj.

**Plný arzenál Excelu.** Ke každému kroku vyber nejsilnější funkci, kterou cílová platforma
umí — dohledání v katalogu, interpolace v tabulce normy, komplexní čísla pro fázory,
matice pro soustavy, statistika a regrese pro měření, `CONVERT` pro jednotky, `LET`/`LAMBDA`
pro čitelnost, Power Query a kontingenční tabulky pro data. Ruční náhražka existující funkce
je nález. Katalog „úkol → funkce → verze“: [reference/excel-toolbox.md](reference/excel-toolbox.md).
Minimální verze Excelu patří do README.

## 4. Podmínky — aby bylo vidět, že je to v mezích

Tři vrstvy, všechny povinné ([reference/conditions.md](reference/conditions.md)):

1. **Vstupy**: ověření dat (stop) + stavová buňka, která chytí i vložení přes schránku.
2. **Posudky a podmínky platnosti**: η, text nerovnosti s čísly (`FIXED`), stav ✔/▲/✘,
   barva podle stavu, data bar na η v registru.
3. **Banner** na každém listu: `✔ VŠECHNY POSUDKY VYHOVUJÍ` / `▲ … malá rezerva` /
   `✘ NEVYHOVUJE – n` + `η max`. Vstup mimo rozsah také přepne banner na ✘.

Hotovo, když změna libovolného vstupu za mez přepne banner na ✘ (vyzkoušej).

## 5. Grafika

- **Živá skica**: XY graf z buněk se souřadnicemi počítanými ze vstupů (průřez, příhradovina,
  rozmístění šroubů, fázorový diagram). Mění se s výběrem — preferuj před obrázkem.
- **Statická skica / schéma**: obrázek (matplotlib, CAD export) u sekce vstupů.
- **Průběhy**: XY graf z tabulky bodů v `91_Grafdata` (M(x), charakteristika, ohřev).
- **Kapacitní obálka**: odolnost jako křivka + účinek jako bod (interakční diagram).
- **Využití**: pruhový graf η z registru, osa 0–1,2.
- Rovnice klíčových vztahů jako vykreslený obrázek u sekce (cesta B: `equation()`).
- **Výkres / řez dílu**: obrys z kót (XY graf), šrafování, osa, kóty s tolerancemi z buněk,
  rámečky GD&T, rohové razítko — [reference/part-drawing.md](reference/part-drawing.md).
- **Dashboard widgety**: posuvník a číselník na vstupu, přepínač jednotek, ukazatel hladiny /
  stupnice, digitální displej, gradientní plošné grafy, vývojový diagram z tvarů —
  [reference/dashboard-widgets.md](reference/dashboard-widgets.md).

Osy vždy s jednotkou, žádné 3D, barvy série z palety.

## 6. Ověření (nikdy nepředávej bez něj)

1. Nula chybových hodnot (`#DIV/0!`, `#NAME?`, `#REF!`, `#VALUE!`).
2. Referenční případ ze specifikace sedí (odchylka uvedená v README nebo jako `check`).
3. Ruční kontrola aspoň jednoho posudku (spočítej nezávisle, uveď uživateli).
4. Test podmínek: jeden vstup za mez → banner ✘; vrátit.
5. Cesta B: `python scripts/verify.py soubor.xlsx --render out/` → exit 0, prohlédni PNG.
   Cesta A: projdi checklist v [reference/excel-in-place.md](reference/excel-in-place.md).

Hotovo, když všech 5 bodů prošlo; výsledek ruční kontroly patří do odpovědi.

## Doprovodné soubory

- `scripts/engcalc.py` — knihovna (cesta B), `scripts/example_ipe_beam.py` — referenční build
- `scripts/verify.py` — přepočet LibreOffice, lint, render
- `reference/vba.md` — makra jen pro desktop Excel (Claude in Excel VBA nespouští)
- `reference/patterns.md` — katalog vzorů z referenčních sešitů (iterace, FDM mřížka, varianty)
- `reference/part-drawing.md` — parametrický výkres dílu v Excelu (obrys, kóty, tolerance, GD&T, razítko)
- `reference/dashboard-widgets.md` — ovládací prvky, ukazatele, tvary, vývojové diagramy
