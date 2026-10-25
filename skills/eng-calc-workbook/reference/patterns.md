# Katalog vzorů

Vzory převzaté z referenčních výpočtových sešitů (obrázky v zadání skillu). Každý vzor:
kdy ho použít a jak ho postavit v jazyce tohoto skillu.

| # | Vzor | Kdy | Stavba |
|---|---|---|---|
| P1 | **Hlavička listu** (projekt, výpočet, list x/y, datum, zpracoval, kontroloval) | vždy | visual-language.md, ř. 1–4 z `meta_*` |
| P2 | **Instrukce barev** v řádku pod hlavičkou | vždy | ř. 6 |
| P3 | **Popisek se symbolem**: „Průměr potrubí, D =“ | vždy | sl. C popis + sl. D `D =` |
| P4 | **Dynamická poznámka**: „Re > 4000 → turbulentní“ | režim/větev výpočtu | `remark` + `condition` |
| P5 | **Skica zadání** (deska, nosník, cihla s vyznačenými rozměry) | geometrie vstupů | statický obrázek v sekci vstupů |
| P6 | **Živá skica z grafu** (příhradovina, průřez, šrouby) | geometrie závislá na vstupech | souřadnice ve `91_Grafdata` → XY graf, skryté osy, rovný rozsah |
| P7 | **Kód normy u vztahu** („ASCE 7-02 Eq. 4-1“) | každý vztah z normy | sl. H |
| P8 | **Podmínka ANO/NE** („A_T·K_LL > 400 ft² → YES“) | přepínač platnosti | `condition` |
| P9 | **Sekce Vstupy / Mezivýpočty / Výsledek** s pruhy (tmavé záhlaví) | vždy | `section()` |
| P10 | **Vzorec jako obrázek** vedle výpočtu | klíčové vztahy | `equation()` (B), sl. G Unicode (A) |
| P11 | **FDM / časová mřížka s barevnou škálou** (teplota v uzlech × čas) | explicitní/implicitní schéma, přechodové děje | blok uzly × kroky ve `91_Grafdata`, barevná škála 3 barvy (min modrá – max červená), graf profilů; podmínka stability (např. Fo ≤ 0,5) jako `condition` |
| P12 | **Tabulka Popis \| Vzorec \| Hodnota \| Jednotka \| Poznámka (OK, ≥ TDH)** | návrh zařízení (čerpadlo, nádrž) | calc pad; poznámka = `check`/`condition` |
| P13 | **Více panelů na jedné stránce** (kalkulátor průřezu, posudek spoje, interakční diagram) | přehled | `01_Prehled`: KPI + skica + kapacitní graf + využití |
| P14 | **Výběr ze standardní databáze** (W-profily, IPE, kabely) | katalogové prvky | `table()` + `select` + `index_match` |
| P15 | **Kapacitní obálka + bod účinku** (interakční diagram N–M, bezpečná oblast) | interakce dvou účinků | obálka = blok bodů, účinek = 1bodová série, `condition` „bod uvnitř“ |
| P16 | **Iterace rozepsaná v řádcích** (Colebrook v C91:C100) | implicitní rovnice | sloupec iterací x_{k+1}=g(x_k), 8–20 řádků, `condition` \|x_n−x_{n−1}\| < tol; žádné cyklické odkazy, žádné Hledání řešení jako krok výpočtu |
| P17 | **Ruční Goal Seek** jako instrukce | inverzní úloha | nahradit P16 nebo uzavřeným tvarem; když nejde, postup do README + `condition` reziduum ≈ 0 |
| P18 | **Varianty ve sloupcích** | citlivost, porovnání návrhů | vstupy jako řádky × varianty ve sloupcích E, F, G…, identický vzorec napříč řádkem, posudek pro každý sloupec |
| P19 | **Revizní tabulka a provozní instrukce** (TCC) | předávka | README |
| P20 | **Přepínač jednotek US/SI** | mezinárodní použití | výběr `cfg_units` + převodní faktory v `02_` konstantách; výpočet vždy v SI |
| P21 | **Parametrický výkres dílu** (řez příruby s kótami, tolerancemi, GD&T, razítkem) | díl, jehož rozměry jsou vstupy výpočtu | [part-drawing.md](part-drawing.md): polygon v `92_Vykres` → XY graf, popisky kót z buněk |
| P22 | **Panel Parametry / Výstup** se vzorcem vedle výsledku | malé kalkulátory na přehledu | [dashboard-widgets.md](dashboard-widgets.md) §1, `FORMULATEXT` |
| P23 | **Posuvník / číselník na vstupu** | citlivost, ladění návrhu | `ui_*` buňka → `in_*` s ověřením mezí (desktop) |
| P24 | **Ukazatel hladiny + digitální displej** | názorný výstup (hladina, rychlost, tlak) | 1bodový sloupcový graf s přechodem + velká buňka v rámečku |
| P25 | **Vývojový diagram z tvarů** | postup výpočtu na README | tvary + spojnice, kroky s odkazy na listy |
| P26 | **LAMBDA jako pojmenovaná funkce** (`=ms(M15)`) | opakovaný převod / vztah | Správce názvů, popis v README (365) |
