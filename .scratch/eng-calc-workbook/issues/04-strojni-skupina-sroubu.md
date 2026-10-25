# 04 — Referenční build strojní: excentricky zatížená skupina šroubů

**Co dodá:** `example_bolt_group.py` — tabulka souřadnic šroubů (vstup), těžiště, polární moment, síla na nejvzdálenější šroub, posudky střih/otlačení, živá skica rozmístění šroubů s vektorem výslednice (vzor P6 + P13).

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** ČSN EN 1993-1-8 (únosnosti šroubů, rozteče a vzdálenosti od okraje jako `condition`); pružná metoda okamžitého středu otáčení — ruční příklad.

- [ ] Vstupní tabulka šroubů s ověřením dat (rozsah souřadnic), proměnný počet řádků do 16
- [ ] Skica: šrouby jako značky, výslednice jako dvoubodová série
- [ ] Posudky a geometrické podmínky v registru
- [ ] Referenční případ sedí ±1 %, verify exit 0
