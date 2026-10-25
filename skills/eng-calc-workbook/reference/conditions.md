# Podmínky, posudky, stavy

Vzorce jsou v anglické syntaxi (tak se ukládají v souboru a tak je zapisuje Claude in Excel
přes API). V české lokalizaci Excelu je uživatel uvidí se středníky — chování je stejné.

## Konvence stavu

První znak stavového textu nese význam; podmíněné formátování i počítání se řídí jím.

| Znak | Text | Kdy |
|---|---|---|
| ✔ | `✔ VYHOVUJE`, `✔ v mezích`, `✔ <text předpokladu>` | η ≤ `cfg_eta_warn`, podmínka splněna |
| ▲ | `▲ VYHOVUJE – malá rezerva` | `cfg_eta_warn` < η ≤ 1 |
| ✘ | `✘ NEVYHOVUJE`, `✘ mimo rozsah`, `✘ NELZE VYHODNOTIT` | η > 1, chyba, nesplněný předpoklad |
| – | `–` | nehodnoceno (η u bool podmínek) |

`cfg_eta_warn` = 0,90 (vstup na `80_Kontroly`, rozsah 0,5–1,0). Uživatel ho může zpřísnit.

## 1. Vstup

Ověření dat: *desetinné číslo mezi* lo a hi, chybové hlášení typu **Stop**, vstupní zpráva
`lo … hi jednotka`. Výběr: *seznam* se zdrojem `=lst_<tabulka>`.

Sloupec G: `⟨lo ; hi⟩ jednotka`. Sloupec I (chytí i vložení přes schránku, které ověření obejde):

```
=IF(AND(ISNUMBER($E12),$E12>=1,$E12<=12),"✔ v mezích","✘ mimo rozsah")
=IF(ISNUMBER(MATCH($E15,lst_IPE,0)),"✔ ze seznamu","✘ není v seznamu")
```

Meze vstupu jsou jediné místo, kde smí být číslo přímo ve vzorci (jsou zdokumentované ve sl. G).

## 2. Posudek (check)

`le`: účinek ≤ odolnost → η = účinek / odolnost. `ge`: hodnota ≥ minimum → η = minimum / hodnota.

| Sl. | Obsah |
|---|---|
| D | `η_M =` |
| E | `=(out_MEd)/(out_McRd)` formát `0.00`, tučně, pojmenovat `chk_M` |
| F | `–` |
| G | `=FIXED(out_MEd,1)&" ≤ "&FIXED(out_McRd,1)&" kNm"` |
| H | článek normy |
| I | stav (níže) |

```
=IF(NOT(ISNUMBER($E40)),"✘ NELZE VYHODNOTIT",
 IF($E40>1,"✘ NEVYHOVUJE",
 IF($E40>cfg_eta_warn,"▲ VYHOVUJE – malá rezerva","✔ VYHOVUJE")))
```

`FIXED`, ne `TEXT`: formátovací řetězec `TEXT` závisí na národním nastavení (v české
lokalizaci `"0.0"` nefunguje), `FIXED` ne.

Rozsahový posudek (lo ≤ x ≤ hi) rozepiš na dva řádky `ge` a `le` — každý má vlastní η.

## 3. Podmínka platnosti (condition)

Předpoklad metody, režim, třída — boolean. E: `=IF(podm,"ANO","NE")`, I:

```
=IF(out_VEd<=0.5*out_VplRd,"✔ bez redukce","✘ nutná redukce 6.2.8")
```

Použij pro: rozsah platnosti metody (Re pro vzorec, štíhlost, třída průřezu, frekvence),
předpoklady (klopení zajištěno, ustálený stav, lineární materiál), výběr větve výpočtu.

## 4. Dynamická poznámka (remark)

Interpretace pro čtenáře, tučná kurzíva NOTE_FONT ve sl. E (přetéká doprava):

```
=IF(calc_Re>4000,"Re > 4000 → turbulentní proudění, f z Colebrooka",
 IF(calc_Re<2300,"Re < 2300 → laminární, f = 64/Re","přechodová oblast – výsledek nejistý"))
```

Když remark říká „mimo rozsah“, patří k němu i `condition`, aby to zachytil banner.

## 5. Registr `80_Kontroly`

Tabulka od ř. 11: `# | Posudek | Symbol | η | Stav | List | Odkaz | fail | warn`.
Číselné posudky první (graf využití čte souvislý blok η), pak podmínky, pak řádek
„Vstupy listu X v povolených mezích“ za každý výpočtový list:

```
η:     =IF(ISNUMBER('10_Posudek'!$E$40),'10_Posudek'!$E$40,"–")
Stav:  ='10_Posudek'!$I$40
Odkaz: =HYPERLINK("#'10_Posudek'!C40","→ ř. 40")
fail:  =IF(LEFT(F11,1)="✘",1,0)
warn:  =IF(LEFT(F11,1)="▲",1,0)
vstupy:=IF(COUNTIF('10_Posudek'!$I$12:$I$18,"✘*")=0,"✔ všechny vstupy v mezích",
        "✘ vstupy mimo rozsah: "&COUNTIF('10_Posudek'!$I$12:$I$18,"✘*"))
```

Názvy: `chk_eta` (sl. E), `chk_fail` (sl. I), `chk_warn` (sl. J). Data bar na η: min 0, max 1,2, BLUE.
Registr je generovaný — jediný list, kde jsou odkazy adresou místo jménem.

## 6. Banner (ř. 5 každého listu)

```
=IF(SUM(chk_fail)>0,"✘ NEVYHOVUJE – počet nesplněných podmínek: "&SUM(chk_fail),
 IF(SUM(chk_warn)>0,"▲ VYHOVUJE S MALOU REZERVOU – posudků: "&SUM(chk_warn),
 "✔ VŠECHNY POSUDKY A PODMÍNKY VYHOVUJÍ"))
 &"     η max = "&IF(COUNT(chk_eta)>0,FIXED(MAX(chk_eta),2),"–")
```

## 7. Podmíněné formátování

Jedna sada pravidel na celý sloupec stavu listu (`I9:I<poslední>`), vzorec s relativním řádkem,
v tomto pořadí, *zastavit, pokud platí*:

| Pravidlo (vzorec) | Výplň | Písmo |
|---|---|---|
| `LEFT($I9,1)="✘"` | `FFC7CE` | `9C0006` tučně |
| `LEFT($I9,1)="▲"` | `FFEB9C` | `9C5700` tučně |
| `LEFT($I9,1)="✔"` | `C6EFCE` | `006100` tučně |
| `LEFT($I9,1)="–"` | `EDEDED` | `595959` |

Navíc na sloupec hodnot `E9:E<poslední>`: `LEFT($I9,1)="✘"` → FAIL výplň (vstup mimo rozsah
i nevyhovující η zčervená přímo v hodnotě). Stejná čtveřice na banner (`$B$5`).
Žádné ikony ani barevné škály na stavy — text + barva stačí a tiskne se.
