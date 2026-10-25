# Nástroje Excelu — co použít na jaký úkol

Zásada: použij **nejsilnější funkci, kterou cílová verze umí**, a minimální verzi napiš do
README (`Vyžaduje: Excel 365 / 2021 / 2016 / LibreOffice ≥ 24.8`). Cílovou verzi zjisti ve
specifikaci; když ji nikdo neřekne, platí Excel 365 a ke každé funkci jen pro 365 dej do
sl. H náhradu pro starší verze.

Verze: **365** = Microsoft 365, **21** = Excel 2021/2024, **16** = Excel 2016/2019,
**LO** = LibreOffice Calc (24.2 / 24.8). ✔ = umí, ✘ = neumí.

## 0. Základní sada inženýra (rychlý přehled)

Minimum, které má agent v hlavě; detaily a verze v sekcích níže.

| Skupina | Funkce | Typické použití | § |
|---|---|---|---|
| dohledání | `XLOOKUP`, `INDEX`+`MATCH` | materiály, čísla dílů, dodavatelé, průřezy z katalogu | 1 |
| logika a chyby | `IF`, `IFS`, `AND`, `OR`, `IFNA`, `IFERROR` (jen s důvodem) | větve modelu, zachycení `#DIV/0!` jako stav „nelze vyhodnotit“ | 3 |
| souhrny | `SUM`, `AVERAGE`, `MIN`, `MAX`, `STDEV.S` (výběr) / `STDEV.P` (celý soubor) | statistika měření, souhrn sady | 6 |
| podmíněné součty | `SUMIFS`, `COUNTIFS`, `AVERAGEIFS`, `MAXIFS` | **kusovník** (počty a ceny dílů podle typu), počty poruch podle příčiny | 6 |
| pořadí a rozložení | `RANK.EQ`, `PERCENTRANK.INC`, `PERCENTILE.INC`, `QUARTILE.INC` | rozhodující zatěžovací stav, kvantil pevnosti, výběr nejhorší varianty | 6 |
| regrese | `LINEST`, `TREND`, `RSQ` | proložení zkoušky, charakteristika | 2, 6 |
| jednotky | `CONVERT` | °F→°C, psi→Pa, ft→m — jen na hranici, výpočet v SI | 7 |
| Besselovy funkce | `BESSELJ/Y/I/K` | vedení tepla (žebra), akustika, skin efekt | 7 |
| komplexní čísla | `COMPLEX`, `IMABS`, `IMCONJUGATE`, `IMSUM`, `IMPRODUCT` | obvody AC, fázory, vektory | 4 |
| bity a soustavy | `BIN2DEC`, `HEX2DEC`, `BITAND`, `BITOR` | registry MCU, protokoly, stavová slova | 7 |
| chybová funkce | `ERF`, `ERFC` | vedení tepla v poloprostoru, pravděpodobnost | 7 |
| co-když | Hledání řešení, Řešitel | inverzní úloha, optimalizace (min. hmotnost při únosnosti) — **jen návrh**, výsledek se zapíše jako vstup | 8, P17 |

## 1. Dohledávání, katalogy, databáze

| Úkol | Funkce | 365 | 21 | 16 | LO |
|---|---|---|---|---|---|
| hodnota z katalogu podle klíče | `XLOOKUP(klíč;db_x_key;db_x_C)` | ✔ | ✔ | ✘ | ≥24.8 |
| totéž kompatibilně | `INDEX(db_x_C;MATCH(klíč;db_x_key;0))` | ✔ | ✔ | ✔ | ✔ |
| nejbližší vyšší normalizovaná hodnota (řada průřezů, E12, jističe) | `XLOOKUP(x;řada;řada;;1)` / `INDEX(řada;MATCH(TRUE;řada>=x;0))` | ✔ | ✔ | ✔* | ✔ |
| výběr všech vyhovujících položek | `FILTER(tbl[Označení];(podm1)*(podm2);"nic nevyhovuje")` | ✔ | ✔ | ✘ | ≥24.8 |
| seřadit katalog podle využití | `SORTBY(tbl[Označení];η_sloupec;1)` | ✔ | ✔ | ✘ | ≥24.8 |
| závislý rozbalovací seznam | ověření dat se zdrojem `=FILTER(...)` přes pojmenovanou oblast | ✔ | ✔ | ✘ | — |
| sloupce/řádky tabulky | `CHOOSECOLS`, `TAKE`, `DROP`, `VSTACK`, `HSTACK` | ✔ | 24 | ✘ | ✘ |

`*` v 16 jako maticový vzorec. Katalog vždy jako Excel tabulka; strukturované odkazy
`tbl_brg[C]` ve vzorcích tabulek, jména `db_*` mimo ně.

## 2. Interpolace a aproximace (tabulky z norem, charakteristiky)

| Úkol | Funkce |
|---|---|
| lineární interpolace v tabulce | `LET(k;XMATCH(x;X;-1);FORECAST.LINEAR(x;INDEX(Y;k):INDEX(Y;k+1);INDEX(X;k):INDEX(X;k+1)))`; kompatibilně `MATCH(x;X;1)` a vzorec přímky |
| bilineární interpolace (2D tabulka) | dvakrát lineární přes `INDEX` řádku a sloupce, nebo `LAMBDA` `INTERP2` |
| proložení přímky / polynomu | `LINEST(y;x^{1,2,3};TRUE;TRUE)` (koeficienty + R², směrodatné chyby), `TREND`, `SLOPE`, `INTERCEPT`, `RSQ`, `STEYX` |
| exponenciála / mocnina | `LOGEST`, `GROWTH`; mocninu linearizuj `LINEST(LN(y);LN(x))` |
| hodnota mimo rozsah tabulky | **nikdy neextrapoluj tiše** → `condition` „x v rozsahu tabulky“ |

## 3. Logika, větve, čitelnost

| Úkol | Funkce |
|---|---|
| větve výpočtu | `IFS`, `SWITCH` (typ ložiska → exponent, soustava TN/TT/IT → podmínka) |
| pojmenované mezivýsledky v jednom vzorci | `LET` (365/21, LO ≥ 24.8) |
| vlastní funkce bez VBA | `LAMBDA` uložená ve Správci názvů: `L10H = LAMBDA(C;P;p;n; 10^6*(C/P)^p/(60*n))` (365) |
| výpočet po prvcích pole | `MAP`, `BYROW`, `BYCOL`, `MAKEARRAY`, `SCAN` (kumulace), `REDUCE` (365) |
| cílené ošetření chyb | `IFNA` u dohledání; `IFERROR` jen s textem důvodu, nikdy plošně |

## 4. Komplexní čísla (elektro: fázory, impedance, obvody AC)

Komplexní číslo je v Excelu **text** `"3+4j"`; vytváří se a čte funkcemi `IM*`
(všechny verze i LibreOffice).

| Úkol | Funkce |
|---|---|
| vytvoření | `COMPLEX(R;X;"j")`; z polárního tvaru `IMPRODUCT(abs;IMEXP(COMPLEX(0;RADIANS(φ);"j")))` |
| aritmetika | `IMSUM`, `IMSUB`, `IMPRODUCT`, `IMDIV`, `IMPOWER`, `IMSQRT`, `IMCONJUGATE` |
| modul a fáze | `IMABS`, `DEGREES(IMARGUMENT(z))`, `IMREAL`, `IMAGINARY` |
| funkce | `IMEXP`, `IMLN`, `IMSIN`, `IMCOS`, `IMSINH`, `IMCOSH`, `IMTAN` (od 2013; v souboru `_xlfn.` — LibreOffice 24.2 takový soubor nepřečte, `verify.py` pak hlásí `#NAME?`, Excel je v pořádku; pro LO použij `IMEXP`: sinh z = (e^z − e^−z)/2) |
| paralelní impedance | `IMDIV(IMPRODUCT(Z1;Z2);IMSUM(Z1;Z2))` nebo LAMBDA `ZPAR` |
| výkon | `S = IMPRODUCT(U;IMCONJUGATE(I))` → P = `IMREAL(S)`, Q = `IMAGINARY(S)`, cos φ = `P/IMABS(S)` |

Pravidla: zobrazovat **modul a úhel jako čísla** (`IMABS`, `DEGREES(IMARGUMENT())`) se
standardním formátem a jednotkou — text komplexního čísla se nedá zaokrouhlit formátem.
Vstupy zadávej jako R a X (dvě číselné buňky s ověřením dat), komplexní buňku z nich skládej.
Fázorový diagram = živá skica (XY graf z `IMREAL`/`IMAGINARY`).

## 5. Matice a soustavy rovnic

| Úkol | Funkce |
|---|---|
| soustava A·x = b (uzlové napětí, příhradovina, statika) | `MMULT(MINVERSE(A);b)` |
| determinant (singularita → `condition`) | `MDETERM(A)`; podmínka `ABS(MDETERM(A))>tol` |
| transformace (abc → dq0, souřadnice) | `MMULT`, `TRANSPOSE`, `MUNIT` |
| komplexní soustava | `MMULT` komplexní neumí → rozepsat na reálnou soustavu 2n×2n `[[R;−X];[X;R]]` |

Matice vždy jako pojmenovaná oblast (`calc_A`), rozměr kontroluj `ROWS`/`COLUMNS` v `condition`.

## 6. Statistika a datová analýza (měření, zkoušky, spolehlivost)

| Úkol | Funkce / nástroj |
|---|---|
| popis souboru | `AVERAGE`, `MEDIAN`, `STDEV.S`, `VAR.S`, `MIN`, `MAX`, `PERCENTILE.INC`, `QUARTILE.INC`, `COUNT` |
| interval spolehlivosti | `CONFIDENCE.T(α;s;n)`, `T.INV.2T(α;n−1)` |
| rozdělení | `NORM.DIST`, `NORM.INV`, `LOGNORM.DIST`, `WEIBULL.DIST` (spolehlivost ložisek, únava), `EXPON.DIST` (poruchovost), `BINOM.DIST`, `POISSON.DIST` |
| testy | `T.TEST`, `F.TEST`, `CHISQ.TEST` |
| korelace a regrese | `CORREL`, `LINEST` s úplnou statistikou, `FORECAST.LINEAR`, `TREND` |
| podmíněné agregace | `SUMIFS`, `AVERAGEIFS`, `COUNTIFS`, `MAXIFS`, `MINIFS`, `AGGREGATE` (ignoruje chyby a skryté) |
| histogram | `FREQUENCY` nebo `COUNTIFS` po třídách + sloupcový graf; v 365 graf Histogram |
| odlehlé hodnoty | `condition` `ABS(x−průměr) ≤ k·s` nebo kvartilové meze |
| import a čištění měření | **Power Query** (CSV z osciloskopu/měřicí karty → tabulka, typy, jednotky), výsledek jako Excel tabulka |
| přehledy | kontingenční tabulka + průřezy (slicery), kontingenční graf |
| spektrum, FFT | doplněk Analýza dat → Fourierova analýza (desktop), nebo `=PY()` |
| regrese s diagnostikou | Analýza dat → Regrese (desktop); výsledek převeď do vzorců `LINEST`, ať se přepočítává |
| Python v buňce | `=PY()` (Microsoft 365, kde je dostupné): numpy/scipy pro to, co vzorce neumí; výsledek vždy zpět do pojmenované buňky se zdrojem |

## 7. Inženýrské a matematické funkce

| Úkol | Funkce |
|---|---|
| převody jednotek | `CONVERT(x;"hr";"yr")`, `CONVERT(t;"C";"K")`, `CONVERT(p;"bar";"Pa")`, `CONVERT(P;"HP";"W")` — výpočet vždy v SI, převádí se na hranici |
| chybová funkce (vedení tepla, difuze, šum) | `ERF`, `ERFC`, `ERF.PRECISE` |
| Besselovy funkce (skin efekt, žebra, kmitání membrán) | `BESSELJ`, `BESSELY`, `BESSELI`, `BESSELK` |
| gama a faktoriál | `GAMMA`, `GAMMALN.PRECISE`, `FACT`, `COMBIN` |
| úhly | `RADIANS`, `DEGREES`, `PI()`, `ATAN2(x;y)` (pozor: pořadí x, y) |
| skokové funkce, tolerance | `DELTA`, `GESTEP`, `SIGN`, `ABS` |
| zaokrouhlení na řadu / výrobní krok | `MROUND`, `CEILING.MATH`, `FLOOR.MATH`, `ROUNDUP` (vždy na bezpečnou stranu) |
| registry, protokoly | `BIN2DEC`, `HEX2DEC`, `DEC2HEX`, `BITAND`, `BITOR`, `BITXOR`, `BITLSHIFT` |

## 8. Numerika bez maker

| Úkol | Postup |
|---|---|
| vážený součet, ekvivalentní zatížení | `SUMPRODUCT`: `P_eq = (SUMPRODUCT(P^3;q)/SUM(q))^(1/3)` |
| integrál z tabulky (lichoběžník) | `SUMPRODUCT((x2−x1)*(y1+y2)/2)` s posunutými oblastmi; v 365 `DROP` |
| derivace z tabulky | centrální diference v pomocném sloupci |
| implicitní rovnice (Colebrook, rovnováha) | iterace rozepsaná v řádcích + `condition` konvergence ([patterns.md](patterns.md) P16) |
| řada bodů pro graf | `SEQUENCE(n;1;start;krok)` (365) nebo sloupec `=start+(ROW()-r0)*krok` |
| ODE / přechodový děj | explicitní schéma v mřížce + `condition` stability (P11) |
| optimalizace | Řešitel (Solver) jen jako nástroj **návrhu**, výsledek se zapíše jako vstup; výpočet nesmí na Řešiteli záviset |

## 9. Dokumentace a sebekontrola

| Úkol | Funkce |
|---|---|
| zobrazit skutečný vzorec vedle hodnoty | `FORMULATEXT(E41)` (revize, ladění, příloha zprávy) |
| čísla do textu stavů | `FIXED(x;n)` (ne `TEXT` — závisí na lokalizaci) |
| spojení textů | `TEXTJOIN(", ";TRUE;oblast)`, `CONCAT` |
| symboly | `UNICHAR(8804)` ≤, `UNICHAR(951)` η, `UNICHAR(8730)` √ |
| odkazy v README | `HYPERLINK("#'10_List'!A1";"10_List")` |
| číslo listu v hlavičce | `SHEET()`, `SHEETS()` |
| kontrola typu | `ISNUMBER`, `ISTEXT`, `ISBLANK`, `ISFORMULA` (žádný vstup nesmí být vzorec a naopak) |

## 10. Vizuál buněk — využij všechno, co Excel umí

Vzhled je součást výpočtu: čtenář musí na první pohled vidět, co je vstup, co výsledek a co
nevyhovuje. Formátuje se **styly buňky a pravidly**, ne ručně buňku po buňce.

| Prvek | Použití |
|---|---|
| **buňkové styly** (Domů → Styly buňky) | `ec_*` podle [visual-language.md](visual-language.md) / [sheet-styles.md](sheet-styles.md); změna stylu překreslí sešit |
| **motiv sešitu** (Rozložení stránky → Motivy) | barvy a písma motivu = tokeny; grafy a tvary je přebírají |
| **vlastní formát čísla** | jednotka zobrazená, hodnota zůstává číslem: `0.0" kN"`, `# ##0" h"`, `0.00" ‰"`; tři sekce `kladné;záporné;nula`; podmínky `[<1]0.000;0.0`; barvy `[Zelená]0.00;[Červená]-0.00`; text `@" ✔"`; inženýrská notace `##0.0E+0`; zlomky `# ?/?` |
| symboly a indexy | v textu buňky *Formát buněk → Horní/Dolní index* na vybraných znacích, nebo Unicode (², ³, ⁻¹, ₀–₉, ᵣ, ₐ, η, σ, τ, γ, Δ, ≤, ≥, √, ·, ×, ⟨⟩) |
| zarovnání | *Zarovnat na střed výběru* místo sloučení; odsazení podúrovní; otočený text u úzkých záhlaví; *Zalomit text* jen v poznámkách |
| ohraničení | tenké pod řádkem obsahu, střední pod záhlavím, dvojité nad součtem/výsledkem, rámeček výsledku |
| **podmíněné formátování vzorcem** | stavy ✔ ▲ ✘ (conditions.md), zvýraznění rozhodujícího zatěžovacího stavu, šedé písmo u neaktivní větve výpočtu |
| **datové pruhy** | η v registru i přímo v calc listu (0–1,25, plný pruh, červená nad 1 přes druhé pravidlo) |
| **barevné škály** | FDM mřížky, mapy teplot, matice citlivosti, tabulky katalogu podle využití |
| **sady ikon** | jen s vlastními prahy (≥ 1 ✘, ≥ 0,9 ▲, jinak ✔) a vždy s textem vedle |
| **minigrafy** (sparklines) | průběh vedle čísla: L₁₀ₕ přes zatěžovací stavy, teplota v čase, η přes varianty |
| komentáře / poznámky | zdroj nebo odvození u konstanty (hover), ne místo sloupce Zdroj |
| vstupní zpráva ověření dat | jednotka a rozsah při kliknutí na vstup |
| hypertextové odkazy | z registru na řádek posudku, z README na listy, z konstanty na PDF normy |
| zobrazení | ukotvené příčky pod hlavičkou, skrytá mřížka, lupa 100 %, rozložení stránky pro tisk, pojmenovaná zobrazení listu |

## 11. Obrázky, tvary a skici

| Prvek | Použití |
|---|---|
| **obrázek v buňce** (`=IMAGE(url)` nebo Vložit → Obrázky → Umístit do buňky, 365) | ikona typu prvku v katalogu, schéma varianty vybrané v seznamu — obrázek se mění s výběrem: `=XLOOKUP(in_typ;tbl_typ[key];tbl_typ[obrazek])` |
| obrázek nad buňkami | skica zadání u sekce vstupů (PNG/SVG z CAD, matplotlib); *Formát → Vlastnosti → Přesouvat a neměnit velikost s buňkami* |
| **SVG ikony** (Vložit → Ikony) | symboly zatížení, podpor, stavů; barva z motivu |
| **tvary a skupiny** | idealizované schéma (nosník, podpory, šipky sil, kóty); seskupit, zamknout |
| **text tvaru propojený s buňkou** (vyber tvar, do řádku vzorců `=calc_h`) | kóty a hodnoty sil ve skice se mění se vstupy |
| **propojený obrázek** (Kopírovat → Vložit jinak → Propojený obrázek, *Fotoaparát*) | živý výřez výsledkové tabulky na přehledu nebo ve zprávě |
| **živá skica z grafu** | XY bodový graf ze souřadnic počítaných ze vstupů (průřez, příhradovina, šrouby, fázory) — skryté osy, stejné měřítko x/y |
| rovnice (Vložit → Rovnice) | klíčové vztahy v textovém poli u sekce; LaTeX-like zápis |
| SmartArt / vývojový diagram | postup výpočtu na README |
| vodoznak v záhlaví | „KONCEPT“ do schválení (obrázek v záhlaví stránky) |

Obrázky nikdy nenesou čísla, která se nepočítají: každá hodnota ve skice je propojená s buňkou.

## 12. Grafy

| Prvek | Použití |
|---|---|
| XY bodový graf | průběhy, charakteristiky, živé skici; nikdy spojnicový graf pro x–y data |
| pruhový graf využití | barvy podle bodu, osa 0–125 %, čára 100 % |
| kombinovaný graf, vedlejší osa | dvě veličiny s různou jednotkou (M a w) |
| chybové úsečky | tolerance měření, pásmo ±η_warn, čára meze |
| plošná řada pod křivkou | vyhovující oblast (n ≤ n_max), bezpečná oblast interakčního diagramu |
| popisky dat z buněk (*Hodnota z buněk*) | pracovní bod, název varianty |
| šablona grafu (.crtx) | jednotný vzhled všech grafů v sešitu |
| graf vodopád / histogram / krabicový (365) | bilance ztrát, rozložení měření |
| dynamický rozsah | data grafu z Excel tabulky nebo pojmenované oblasti, ne pevné adresy |

## 13. Vstupy a ochrana

| Prvek | Použití |
|---|---|
| ověření dat | desetinné min–max, seznam, vlastní vzorec (`=AND(ISNUMBER(E12);E12>0)`) + vstupní zpráva + chybové hlášení Stop |
| ovládací prvky formuláře (desktop) | zaškrtávátko, přepínač, číselník pro citlivost — propojené s buňkou; v Claude in Excel náhrada seznamem |
| zaškrtávací políčka v buňce (365) | ANO/NE předpoklady (Vložit → Zaškrtávací políčko) |
| ochrana listu | odemčené jen vstupy, bez hesla; povolit formát sloupců |
| správce scénářů | pojmenované sady vstupů (zatěžovací stavy) — desktop |
| Hledání řešení / tabulka dat | desktop, ne v Claude in Excel; náhrada: varianty ve sloupcích (P18) |

Při psaní souboru přes openpyxl řeší prefixy `_xlfn.`/`_xlpm.` funkce `fx()` a `let()` z
`engcalc.py`; dynamická pole (`FILTER`, `SORT`, `SEQUENCE`…) se do souboru zapisovat nedají —
napiš je v Excelu (cesta A) nebo nech v README instrukci.
