# Styly výpočtového listu

Dva styly, stejná data, stejné podmínky ([conditions.md](conditions.md)), stejná jména.
Liší se rozvržením a hustotou.

| | **K — kompaktní posudkový list** (preferovaný) | **P — calc pad** |
|---|---|---|
| Vzor | listy TCC / The Concrete Centre, ruční statický výpočet | protokol krok za krokem |
| Kdy | hlavní list posudku, 1 strana A4 na jeden prvek | dlouhé odvození, návrhové metodiky (stroj, vinutí), revize |
| Hustota | 2 veličiny na řádek, tabulky zatěžovacích stavů | 1 veličina na řádek |
| `engcalc.py` | zatím ne (ticket 12) — cesta A | `CalcSheet` |

Kombinace: list K jako souhrnný posudek, list P jako doložení mezivýpočtů na dalším listu.

## Styl K — anatomie (shora dolů, A4 na výšku)

1. **Proužek identifikace** (9 pt šedě, tenké mřížky): zdroj/šablona · © · rev. (vstup) · list x/y · datum.
2. **Název** 16 pt tučně VERZÁLKAMI vlevo; vpravo nahoře **idealizovaná skica se zatížením**
   (obrázek nebo skupina tvarů; síly červeně, reakce modře, kóty černě kurzívou).
3. **Sekce** = červený tučný nadpis VERZÁLKAMI 13 pt `C00000`, bez výplně, s jednotkami v
   závorce běžným písmem: `ROZMĚRY (mm)`.
4. **Řádek veličiny**: `popis symbol =` zarovnané vpravo | hodnota na střed | jednotka.
   Symbol kurzívou, index jako dolní index (Formát buněk → Dolní index na části textu, nebo
   Unicode ₀ ₁ ᵣ ₐ). **Vstup = modré podtržené písmo `0000FF`**, bez výplně; výpočet a katalog černě.
   Dvě veličiny vedle sebe (levý a pravý blok sloupců).
5. **Tabulka zatěžovacích stavů / kombinací**: záhlaví kurzívou tučně v rámečku, sloupce
   ZS 1, ZS 2 (příp. nepříznivý / příznivý), vstupy modře podtržené.
6. **STAV NÁVRHU** vpravo vedle zatížení: červený popisek + `VYHOVUJE` zeleně `00B050` /
   `NEVYHOVUJE` červeně, + η max. Pod tím **graf využití**: vodorovné pruhy, každý posudek
   vlastní barvou, osa 0–125 %, svislá červená čára 100 %, světle modré pozadí plochy
   `DEEBF7` se zaoblením.
7. **VÝPOČET A POSUDKY**: tabulka ZS 1 | ZS 2 | √ | vztah. Posudkové řádky tučně, sloupec
   √ zeleně (✘ červeně), **vztah kurzívou vpravo** (`L_req / L₁₀ₕ ≤ 1`, „viz rovnice na listu Refs“).
   Pod tabulkou poznámka v závorce kurzívou (co rozhoduje, co je zanedbáno).
8. **PŘEDPOKLADY** tmavě modrou kurzívou; položky `a)` `b)` … s červeným písmenem, ve 2–3 sloupcích.
9. Patička: legenda barev, odkaz na normu.

Bannery a registr ze stylu P platí i tady: `STAV NÁVRHU` je banner, posudkové řádky jsou
v `80_Kontroly`. Rámec stránky: svislé modré čáry vlevo a vpravo (ohraničení sloupců A a L).

## Styl K — technika v Excelu

| Prvek | Jak |
|---|---|
| mřížka | skrytá; jemná mřížka jen v proužku identifikace |
| šířky sloupců | úzká mřížka (např. 12 sloupců po ~6–9 znacích), sekce zarovnané na ni; nic se neslučuje, popisky přetékají doleva přes *Zarovnat vpravo* |
| modrý podtržený vstup | buňkový styl `ec_input_k` (modré, podtržené, odemčené) + ověření dat |
| stav návrhu | vzorec + podmíněné formátování (zelená / červená), styl `ec_status_k` |
| graf využití | pruhový graf ze `chk_eta`, *Formát datového bodu → různé barvy podle bodu*, osa max 1,25, čára 100 % jako druhá řada (XY) nebo chybová úsečka |
| skica | obrázek (Vložit → Obrázky → Umístit na buňky) nebo skupina tvarů; texty kót propojené na buňky (`=calc_h` v textovém poli) |
| vztahy | text kurzívou; klíčová rovnice jako objekt Rovnice (Vložit → Rovnice) |

## Styl P

Viz [visual-language.md](visual-language.md) — mřížka sloupců A–J, tmavé pruhy sekcí,
žluté vstupy. Implementuje `engcalc.py`.
