# Parametrický výkres dílu v Excelu

Cíl: řez / pohled dílu (příruba, hřídel, pouzdro, průřez nosníku, plech s otvory), který se
**překreslí při změně kót** a nese tolerance, GD&T a rohové razítko. Výkres doplňuje výpočet,
nenahrazuje CAD. Hodnoty na výkrese jsou vždy propojené s buňkami: kóta = `in_*`, tolerance =
`tol_*`, mezní rozměry = `calc_*`.

## 1. Data výkresu (`92_Vykres`)

| Blok | Obsah | Jak |
|---|---|---|
| `gd_contour` | obrys dílu jako uzavřený polygon (x, y) v mm | body počítané z kót: `=in_D/2`, `=in_L1+in_L2`…; poslední bod = první |
| `gd_hole_*` | díry, zahloubení, závity | samostatné polygony / kružnice `x=xc+r·COS(t)`, `t` po 10° (`SEQUENCE` nebo sloupec) |
| `gd_axis` | osa symetrie | 2 body přesahující obrys o 5 mm |
| `gd_dim_*` | kótovací čáry | 2 body na kótu + 2 vynášecí čáry; odsazení od obrysu `cfg_dim_gap` |
| `gd_hatch` | šrafy řezu | rovnoběžné úsečky pod 45° oříznuté na obrys (viz §3) |
| `gd_frame` | rámeček výkresu | obdélník formátu (A4 297×210) v měřítku |

Rotačně symetrický díl: kresli horní polovinu obrysu a zrcadli (`y → −y`) do druhé série —
jedna sada kót, dvě řady grafu. Měřítko `cfg_scale` (např. 2:1) se jen zapisuje do razítka;
graf kreslí ve skutečných mm.

## 2. Graf výkresu

- **XY bodový graf se spojnicemi bez značek**, jedna řada na prvek (obrys, díry, osa, kóty).
- **Stejné měřítko os**: min/max obou os z `calc_view_*` se stejným rozsahem, plocha grafu
  čtvercová (nebo poměr os = poměr plochy). Osy, mřížka a legenda skryté.
- Styly čar podle ČSN EN ISO 128: obrys plná tlustá (2,25 pt, NAVY nebo černá), osa
  čerchovaná tenká (*Typ přerušení → dlouhá čárka-tečka*), kóty plná tenká (0,75 pt) se
  šipkami na obou koncích (*Formát čáry → Typ začátku / konce šipky*), skryté hrany čárkovaně.
- **Popisky kót = Hodnota z buněk** (*Popisky dat → Hodnota z buněk*) na středovém bodě kóty;
  text sestav vzorcem: `="Ø"&FIXED(in_D;1)&" "&calc_tol_D_txt`.
- Výplň řezu: graf plochu polygonu nevyplní → buď šrafy (§3), nebo **tvar Volný tvar** pod
  grafem s výplní `BLUE` 40 % průhlednosti (cesta A), nebo obrázek z matplotlibu (cesta B).
- Živé zvýraznění: posudek ✘ obarví příslušnou kótu červeně — samostatná řada „kóty mimo
  toleranci“ s body `=IF(chk_x_status="✘";x;NA())`.

## 3. Šrafování

Úsečky `y = x + k·s` pro `k = −n…n`, rozteč `s = cfg_hatch` (3 mm v měřítku výkresu). Oříznutí
na obdélníkové části obrysu: pro každý obdélník řezu spočti průsečíky se 4 hranami a vezmi
dva vnitřní (`MAX`/`MIN` přes `x_min…x_max`). Pro složitý obrys rozděl řez na obdélníky —
díly z tabule, příruby a pouzdra se tak rozloží vždy. Šrafy oddělí body `#N/A` (`NA()`),
graf je kreslí jako přerušenou čáru — jedna řada pro všechny šrafy.

## 4. Kóty a tolerance

| Řádek | Obsah | Vzorec / zdroj |
|---|---|---|
| jmenovitý rozměr | vstup | `in_D` |
| tolerance | horní / dolní úchylka, nebo pole + stupeň (`H7`, `g6`) | `in_D_es`, `in_D_ei` nebo výběr z `db_iso286` |
| ISO 286 | dohledání úchylek podle rozměrového intervalu | `XLOOKUP(in_D;db_iso286[do];db_iso286[H7];;1)`; mimo tabulku → `condition` |
| ISO 2768 (všeobecné) | netolerované kóty podle třídy `f/m/c/v` | `db_iso2768` + výběr `cfg_gen_tol` (např. `mK`) |
| mezní rozměry | max / min | `=in_D+in_D_es`, `=in_D+in_D_ei` |
| text kóty | `40,5 ±0,1` / `9,2 +0,15/−0,1` | `IF(es=−ei; "±"&FIXED(es;2); "+"&FIXED(es;2)&"/"&FIXED(ei;2))` |
| uložení | vůle / přesah min–max | díra − hřídel, `check` „vůle min ≥ 0“ nebo „přesah v mezích“ |

**Rozměrový řetězec** (tolerance stack-up) jako posudek: uzavírací rozměr
`A0 = ΣA_zvětšující − ΣA_zmenšující`; tolerance **nejhorší případ** `T0 = ΣT_i`,
**statisticky** `T0 = √(ΣT_i²)` (RSS, předpoklad normálního rozdělení → `condition`).
Posudek `T0 ≤ T0_dov` → η, stav, registr `80_Kontroly`.

Na výkrese i v tabulce vždy obě úchylky; výrobní min/max patří do výsledku.

## 5. Geometrické tolerance (GD&T, ČSN EN ISO 1101)

Rámeček tolerance = blok 3 buněk s ohraničením (nebo textové pole propojené na buňku):
`symbol | hodnota | základna`. Symboly Unicode:

| Vlastnost | Znak | Vlastnost | Znak |
|---|---|---|---|
| přímost | ⏤ | rovnoběžnost | ∥ |
| rovinnost | ⏥ | kolmost | ⊥ |
| kruhovitost | ○ | sklon | ∠ |
| válcovitost | ⌭ | poloha | ⌖ |
| profil čáry / plochy | ⌒ / ⌓ | soustřednost | ◎ |
| házení / celkové | ↗ / ⌰ | souměrnost | ⌯ |

Základny `A`, `B` jako rámeček s písmenem a trojúhelníkem (tvar). Hodnota rámečku je buňka
`tol_geo_*` — měřený protokol pak porovná naměřenou úchylku a dá `check`.

## 6. Rohové razítko (ČSN EN ISO 7200)

Blok buněk vpravo dole, žádné slučování (zarovnat na střed výběru): název dílu, číslo výkresu,
materiál, měřítko, všeobecné tolerance (ISO 2768-mK), hrany (ISO 13715), promítání, zpracoval /
kontroloval / schválil s datem, list, revizní tabulka (č., změna, datum, jméno). Všechny hodnoty
z `meta_*` a `in_*` — razítko se nevyplňuje ručně. Barvy jen jako akcent oboru, tisk ČB čitelný.

## 7. Posudky typické pro díl

`check`: minimální tloušťka stěny ≥ t_min; vůle uložení ≥ 0; rozměrový řetězec T0 ≤ T0_dov;
hmotnost ≤ m_max (`ρ·V`, objem rotačního dílu z polygonu Pappovou větou
`V = 2π·x̄·A`); otlačení / smyk závitu ze `domains.md`.
`condition`: kóta v intervalu tabulky ISO 286; poměr L/D v rozsahu metody; materiál v katalogu.

## 8. Cesty

| | Cesta A (Claude in Excel / ruční) | Cesta B (`engcalc.py`) |
|---|---|---|
| obrys, kóty, osa, šrafy | XY graf (vše) | `sketch_chart()` / `xy_chart()` z bloku `92_Vykres` |
| výplň řezu, rámečky GD&T, šipky základen | tvary (Vložit → Tvary), text propojený na buňku | openpyxl **tvary nevytváří** → buněčné rámečky + PNG z matplotlibu (`png_from_figure`) |
| razítko | buňky | buňky |

Hotovo, když změna libovolné kóty překreslí obrys, šrafy i popisky, text kóty ukazuje
úchylky a posudek mimo toleranci obarví kótu i banner.
