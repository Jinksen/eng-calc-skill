# Cesta A — živě v sešitu (Claude in Excel / ruční stavba)

Claude in Excel pracuje přímo nad otevřeným sešitem: zapisuje hodnoty a vzorce, formátuje,
přidává podmíněné formátování a ověření dat, pracuje napříč listy. **Nespouští Python ani VBA**
a nepodporuje tabulky dat (What-If Data Table). Celý standard proto stojí na nativních
prvcích Excelu — výsledek je stejný jako z cesty B.

## Pořadí stavby

Stav po každém kroku musí jít přepočítat bez chyb. Postupuj po listech, ne po vrstvách.

1. **Styly buňky** (Domů → Styly buňky → Nový styl), názvy přesně: `ec_input`, `ec_select`,
   `ec_const`, `ec_calc`, `ec_link`, `ec_aux`, `ec_result`, `ec_h1`, `ec_h2`, `ec_colhead`,
   `ec_status`, `ec_note` — vlastnosti v [visual-language.md](visual-language.md). Když API
   styly vytvářet neumí, formátuj přímo podle stejných tokenů; názvy stylů pak zmiň v README.
2. **`00_README`** — identifikace v C5:C13, každá buňka pojmenovaná `meta_project`,
   `meta_title`, `meta_subject`, `meta_org`, `meta_std`, `meta_author`, `meta_checker`,
   `meta_rev`, `meta_date`. Zbytek README až na konci.
3. **`80_Kontroly`** — hlavička, `cfg_eta_warn` v E8 = 0,90 s ověřením 0,5–1,0, záhlaví
   registru ř. 10. Řádky registru se doplňují s každým posudkem.
4. **Databáze `9x_`** — Excel tabulka (Vložit → Tabulka) s názvem `tbl_<x>`, hodnoty ve stylu
   const, nad tabulkou řádek „Zdroj: …“. Pojmenuj sloupce `db_<x>_<sloupec>`, klíčový sloupec
   `db_<x>_key` a stejný rozsah `lst_<x>` pro rozbalovací seznamy.
5. **Výpočtový list `1x_`** — šířky sloupců A–J, hlavička ř. 1–7, ukotvit příčky na A8,
   mřížka vypnutá. Pak sekce po sekcích (typy řádků v SKILL.md §3, vzorce v
   [conditions.md](conditions.md)). Každou hodnotu pojmenuj hned při zápisu.
6. **Posudky** — za každý `check`/`condition` přidej řádek do registru `80_Kontroly`
   (číselné nad podmínky) a rozšiř názvy `chk_eta`, `chk_fail`, `chk_warn`.
7. **Banner** na ř. 5 všech listů + podmíněné formátování (conditions.md §6–7).
8. **Grafy** — data do `91_Grafdata` (souřadnice skici, body průběhu), XY bodový graf
   s čarami bez značek; skica: osy skryté, stejný rozsah x a y, čtvercová plocha.
   Když v prostředí nejde graf vložit, připrav datový blok a napiš uživateli jednou větou,
   který rozsah vložit jako *XY bodový s rovnými čarami*.
9. **README** — účel, rozsah platnosti, předpoklady, postup, legenda (vzorek každého stylu),
   obsah s `HYPERLINK("#'list'!A1",…)`, zdroje, revizní log.
10. **Zámek a tisk** — odemknout jen vstupy, zamknout listy bez hesla; oblast tisku, tisk
    ř. 1–7 na každé stránce, A4 na šířku stránky, zápatí.

## Úprava existujícího sešitu

- Nejdřív přečti strukturu (listy, názvy, kde jsou vstupy) a navrhni mapování na standard;
  přestavbu dělej list po listu se zachovanými výsledky (před/po porovnej klíčová čísla).
- Hodnotu natvrdo ve vzorci vytáhni do `const`/`input` řádku se zdrojem.
- Před přepsáním obsazených buněk potvrď s uživatelem.

## Náhrady za funkce mimo dosah

| Chci | Nativní náhrada |
|---|---|
| přepínač / zaškrtávátko (Form Controls, VBA) | výběr ze seznamu `ANO;NE` nebo 0/1 s ověřením dat |
| iterace (Hledání řešení, cyklus) | rozepsaná iterace v řádcích + `condition` konvergence ([patterns.md](patterns.md)) |
| Data Table pro citlivost | sloupce variant se stejným vzorcem ([patterns.md](patterns.md)) |
| tlačítko „přepočítat“ | není potřeba — vše jsou vzorce |
| obrázek rovnice | vztah zápisem ve sl. G (Unicode: ², ³, √, ·, ≤, γ, η, σ, Δ) |

## Checklist před předáním

```
[ ] Žádná chybová hodnota v sešitu
[ ] Každý vstup: ověření dat + stav ve sl. I; mimo rozsah → banner ✘ (vyzkoušeno)
[ ] Každá konstanta a posudek: zdroj ve sl. H
[ ] Každý výpočet: jednotka (F) a vztah (G); žádné nevysvětlené číslo ve vzorci
[ ] Všechny posudky v 80_Kontroly, názvy chk_* pokrývají celý registr
[ ] Banner na každém listu, barvy stavů fungují
[ ] Referenční případ sedí; jeden posudek přepočítán ručně
[ ] README kompletní, revize zapsaná; listy zamčené, tisk nastavený
```
