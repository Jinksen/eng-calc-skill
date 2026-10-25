# Dashboard widgety a tvary

Interaktivní panely na `01_Prehled` nebo vedle vstupů: uživatel posouvá vstup a hned vidí
ukazatel, graf a stav. Platí pravidla skillu: widget jen **čte nebo zapisuje pojmenovanou
buňku**, výpočet zůstává ve vzorcích, stav ✔/▲/✘ a banner se nemění.

## 1. Panel „Parametry / Výstup“

Malé dvoubarevné bloky: záhlaví `Parametry | Jednotky` (NAVY / akcent oboru, bílé písmo),
řádky `veličina | hodnota | jednotka`, pod tím záhlaví `Výstup` a řádek s výsledkem a jeho
vzorcem (`FORMULATEXT`) vedle. Vstupní buňka má **rámeček v barvě své pojmenované oblasti**
(barevně sladěné s tím, jak Excel obarví odkazy při úpravě vzorce) — čtenář spáruje vstup se
vzorcem. Jména drží konvenci skillu: `in_h1`, `in_h2`, `out_v` (ne `dash_h1_in`).

## 2. Ovládací prvky formuláře (desktop Excel)

| Prvek | Použití | Propojení |
|---|---|---|
| **posuvník** (Vývojář → Vložit → Posuvník) | citlivost na vstup, plynulé ladění | propojená buňka `ui_h1_raw` (celé číslo 0–1000), vstup `=c_h1_min+ui_h1_raw*krok` |
| **číselník** | krokování normalizovanou řadou | index do `lst_*` → `INDEX(lst_E12;ui_idx)` |
| **přepínač** (option button) | volba soustavy jednotek, režimu, varianty | `ui_units` = 1/2 → `cfg_units = CHOOSE(ui_units;"SI";"US")` |
| **zaškrtávátko** / zaškrtávací políčko v buňce (365) | zapnout/vypnout vliv, předpoklad ANO/NE | `condition` čte PRAVDA/NEPRAVDA |
| **rozevírací seznam** | výběr z katalogu | raději ověření dat seznamem (funguje všude) |

Pravidla: prvek zapisuje do `ui_*` buňky; skutečný vstup `in_*` z ní počítá a **má ověření
mezí** jako ostatní vstupy. Ovládací prvky formuláře neumí Claude in Excel, Excel pro web
ani openpyxl → vždy existuje i obyčejná vstupní buňka a README to uvádí. ActiveX nepoužívat.

**Přepínač jednotek**: výpočet vždy v SI; zobrazení `=IF(cfg_units="SI";x;CONVERT(x;"m/s";"ft/s"))`
a jednotka `=IF(cfg_units="SI";"m/s";"ft/s")` (vzor P20).

## 3. Ukazatele

| Widget | Stavba |
|---|---|
| **hladina v nádrži / sloupec naplnění** | sloupcový graf 1 bod, osa pevně 0–max, výplň přechodem (*Výplň → Přechod*, světlá→`BLUE`), popisek „h₁ 41 m“ z buňky; druhá hladina (h₂, výtok) jako řada XY s vodorovnou čárou |
| **digitální displej** | jedna buňka 24–28 pt tučně, tlustý černý rámeček, formát `0.0`; nad ní popisek s jednotkou `V (m/s)`; podmíněné formátování barvy textu podle stavu |
| **tachometr / půlkruhová stupnice** | prstencový graf: 3 pásma (✔ ▲ ✘ barvy, poslední polovina průhledná) + koláč s úzkou výsečí jako ručička z `chk_eta` |
| **teploměr / lineární stupnice** | skládaný pruhový graf: hodnota + zbytek do max, čára meze jako XY řada |
| **semafor** | 3 kruhy (tvary) nebo buňky se symboly ●, barva podmíněným formátováním podle stavu |
| **KPI dlaždice** | viz visual-language.md → Dashboard |

Hodnoty ukazatelů jsou vždy pojmenované buňky; osa a meze z `cfg_*`, ne pevně v grafu.

## 4. Grafy s výrazným vzhledem

- **Plošný graf s přechodem** (např. dva roky měření přes sebe): *Výplň → Přechod*, lineární
  svisle, průhlednost 20–40 %, starší řada vzadu. Pro technická x–y data ale vždy XY graf;
  plošný jen pro kategorie (měsíce, zatěžovací stavy).
- Barvy přechodů odvozuj od palety skillu (`2E75B6`, `7030A0`…), ne od výchozího motivu.
- Pozadí plochy jemně (`DEEBF7`), bez 3D, osy s jednotkou.

## 5. Tvary a vývojové diagramy (Vložit → Tvary)

| Účel | Jak |
|---|---|
| **vývojový diagram postupu výpočtu** na README | ovál = start/konec, obdélník = krok (odkaz na list), kosočtverec = rozhodnutí (`condition`), šipky = spojnice (*Čáry → Spojnice*, přichytí se k bodům tvaru) |
| idealizované schéma (nosník, podpory, síly) | tvary + šipky, seskupit; text šipky `=calc_F` |
| text propojený s buňkou | vyber tvar → řádek vzorců `=out_v` (jen jedna buňka, ne vzorec) |
| přepínání viditelnosti | nejde vzorcem → dva tvary + podmíněně formátovaná buňka pod nimi, nebo makro (vba.md) |
| zarovnání | *Formát tvaru → Zarovnat / Rozmístit*, mřížka přichycení, skupiny zamknout ochranou listu |

Cesta B: openpyxl tvary ani ovládací prvky **nevytváří a při uložení existující zahodí** —
neotvírej přes openpyxl sešit, který tvary má. Schéma pak jako PNG (matplotlib), diagram
postupu jako tabulka kroků s hypertextovými odkazy; tvary doplň cestou A nebo makrem.

## 6. Copyright a značky

Převzatý vzhled z cizí šablony (logo, © text, vodoznak) do sešitu nepatří; použij `meta_org`.
