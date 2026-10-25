# Cesta C — revize existujícího sešitu

Výstup revize: tabulka nálezů seřazená podle závažnosti + návrh, zda opravit na místě
(cesta A), přestavět (B) nebo rozpadnout na tickety (D).

## Postup

1. Inventura: listy, skryté listy/řádky/sloupce, pojmenované oblasti, externí odkazy, makra.
2. Kde jsou vstupy? (rozházené po výpočtu = nález)
3. Projdi každý výpočetní vzorec (Ctrl+` / openpyxl), hledej vzory níže.
4. Nezávisle přepočítej aspoň jeden klíčový výsledek; uveď hodnotu a odchylku.
5. Vyzkoušej okraje: nula, záporná hodnota, vstup za rozumnou mez — co sešit udělá?
6. Cesta B dostupná → `verify.py` (lint najde magická čísla, volatilní funkce, vstupy bez ověření).

## Závažnost

| Úroveň | Příklady |
|---|---|
| **Kritická** — výsledek může být špatně | chybná jednotka/převod, odkaz na špatný řádek, nekonzistentní vzorec v oblasti, `IFERROR` schovávající chybu, chybějící posudek, který metodika vyžaduje, tiché pokračování mimo platnost metody |
| **Vysoká** — nelze ověřit | magická čísla bez zdroje, žádné kontroly, žádný referenční případ, skryté výpočty |
| **Střední** — křehké | vstupy bez ověření dat, sloučené buňky ve výpočtu, volatilní funkce, odkazy na jiné soubory |
| **Nízká** — čitelnost | chybějící jednotky/symboly, nejednotné formáty, falešná přesnost, bez README/verze |

Ke každému nálezu: místo (list!buňka nebo jméno), proč to vadí, oprava jednou větou.
