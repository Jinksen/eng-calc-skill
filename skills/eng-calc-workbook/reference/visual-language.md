# Vizuální jazyk

Jediný zdroj pravdy pro vzhled. `scripts/engcalc.py` (třída `C`, `GRID`, `_style_defs`)
to implementuje 1:1 — při změně uprav oba.

## Barevné tokeny

| Token | Hex | Použití |
|---|---|---|
| NAVY | `1F3864` | nadpis sekce (výplň, bílé písmo), rámeček banneru, linky hlavičky |
| BLUE | `2E75B6` | série grafu 1, odkazy, karta výpočtového listu |
| BLUE_LT | `D9E1F2` | podsekce |
| BLUE_XLT | `F2F6FC` | záhlaví sloupců, KPI dlaždice |
| INPUT_FILL / INPUT_FONT | `FFF2CC` / `0000FF` | ruční vstup (tučně), rámeček `8EA9DB` |
| SELECT_FILL | `DDF4F7` | výběr ze seznamu (písmo `0000FF`) |
| CONST_FILL / CONST_FONT | `EDE4F5` / `5B2C83` | konstanta z normy / katalogu |
| LINK_FONT | `00703C` | vzorec čerpající z jiného listu |
| MUTED | `7F7F7F` | jednotky, pomocné výpočty (kurzíva), zdroje (8 pt kurzíva) |
| RESULT_FILL / RESULT_EDGE | `FCE4D6` / `C55A11` | klíčový výsledek, rámeček medium |
| NOTE_FONT | `1F4E79` | dynamická poznámka (tučná kurzíva) |
| OK | `C6EFCE` / `006100` | ✔ vyhovuje |
| WARN | `FFEB9C` / `9C5700` | ▲ malá rezerva |
| FAIL | `FFC7CE` / `9C0006` | ✘ nevyhovuje / mimo rozsah / nelze vyhodnotit |
| NA | `EDEDED` / `595959` | – nehodnoceno |
| Série grafů | `2E75B6 C55A11 548235 7030A0 BF8F00 1F3864` | v tomto pořadí |

**Akcent oboru** (levý blok hlavičky): elektro `BF8F00`, strojní `2F5597`,
stavební `548235`, obecné `1F3864`.

**Karty listů**: README `7F7F7F`, přehled `1F3864`, výpočet `2E75B6`, kontroly `548235`,
data `7030A0`.

Barva nikdy nenese informaci sama: stav má vždy i symbol a text (✔ ▲ ✘ –), tisk ČB.

## Písmo a čísla

- Calibri 10 pt; nadpis sekce 11 pt tučně VERZÁLKAMI; výsledek 11 pt tučně; KPI 18 pt.
- Sloupec „Vztah“ Cambria Math 10 pt.
- Formát podle veličiny, žádná falešná přesnost: síly/momenty `0.0`, napětí v MPa `0`,
  součinitele `0.00`, využití η `0.00`, ε a malé poměry `0.000`, rozměry v mm `0` nebo `0.0`.
- Jednotka **vždy v sousedním sloupci**, nikdy jako text v buňce s číslem.
- Datum `yyyy-mm-dd`.

## Mřížka calc padu (sloupce A–J)

| Sl. | Šířka | Role | Styl |
|---|---|---|---|
| A | 1,5 | okraj | — |
| B | 5 | číslo kroku `3.12` | jednotka |
| C | 30 | veličina (popis) | label |
| D | 9 | symbol + ` =` | tučná kurzíva, vpravo |
| E | 12 | **hodnota** | podle typu řádku |
| F | 8 | jednotka | šedá |
| G | 26 | vztah zápisem / text nerovnosti | Cambria Math |
| H | 18 | zdroj / norma (článek) | 8 pt kurzíva šedá |
| I | 22 | mez / stav | tučně na střed, barva podle stavu |
| J | 1,5 | okraj | — |

Řádky obsahu mají jen spodní tenkou linku `D9D9D9`; mřížka listu vypnutá.

## Hlavička listu (řádky 1–7, opakují se při tisku)

| Ř. | B–C (akcent oboru, bílé písmo) | D | E–G | H | I |
|---|---|---|---|---|---|
| 1 | `=meta_org` 11 pt tučně | Projekt | `=meta_project` | List č. | `=SHEET()&" / "&SHEETS()` |
| 2 | „Inženýrský výpočet“ | Výpočet | `=meta_title` 12 pt NAVY | Datum | `=meta_date` |
| 3 | `=meta_std` | List | název listu | Zpracoval | `=meta_author` |
| 4 | `="Revize "&meta_rev` | Předmět | `=meta_subject` | Kontroloval | `=meta_checker` |
| 5 | **banner** přes B–I, výška 26, 12 pt tučně, rámeček NAVY medium, *zarovnat na střed výběru* |
| 6 | instrukce 9 pt kurzíva: co se zadává kam + legenda ✔ ▲ ✘ |
| 7 | záhlaví sloupců 8 pt tučně NAVY na BLUE_XLT, spodní linka medium; ukotvit příčky pod ř. 7 |

Popisky hlavičky (Projekt, Datum…) 7 pt šedě; hodnoty tučně. Textová `meta_*` se
odkazují s `&""`, aby prázdná buňka neukázala 0. Identifikace žije jen na `00_README`.

## Sekce a nadpisy

- Sekce: celý řádek B–I výplň NAVY, číslo v B, název v C VERZÁLKAMI, výška 18, nad ní prázdný řádek.
- Podsekce: výplň BLUE_LT, písmo NAVY tučně, spodní linka NAVY.
- Komentář: 9 pt kurzíva šedá ve sl. C.

## Dashboard

KPI dlaždice 4 vedle sebe (B–C, D–E, F–G, H–I): popisek 9 pt šedě, hodnota 18 pt NAVY,
jednotka; výplň BLUE_XLT, horní linka NAVY medium. Pod tím mřížka grafů: skica vlevo
(čtverec ~6 cm), průběhy vpravo (~11,5 × 6 cm), využití přes celou šířku dole.

## Tisk

A4 na výšku (datové listy na šířku), přizpůsobit na šířku 1 stránky, okraje 1 cm,
tisknout řádky 1–7 na každé stránce, zápatí `soubor | list | Strana P / N`, vodorovně na střed.

## Zámek

Odemčené jsou jen `input`, `select` a pole revizního logu / identifikace na README.
List chráněn bez hesla (ochrana proti nechtěnému přepsání, ne utajení). Vzorce se nikdy neskrývají.
