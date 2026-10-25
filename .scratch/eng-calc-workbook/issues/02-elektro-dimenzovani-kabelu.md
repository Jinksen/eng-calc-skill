# 02 — Referenční build elektro: dimenzování kabelu

**Co dodá:** `example_cable_sizing.py` — sešit pro dimenzování kabelového vedení NN s výběrem průřezu a způsobu uložení z databáze, posudky I_B ≤ I_n ≤ I_z·k, I_2 ≤ 1,45 I_z, ΔU ≤ ΔU_dov, k²S² ≥ I²t a podmínkou automatického odpojení; přehled s KPI a grafem využití.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** ČSN 33 2000-5-52 (tabulky dovolených proudů a přepočítacích součinitelů — **hodnoty přepsat z normy, neodhadovat**), ČSN 33 2000-4-43, -4-41; ověřovací příklad z učebnice / ČSN s ručním výpočtem.

- [ ] Databáze I_z pro zvolený způsob uložení a izolaci se zdrojem (číslo tabulky)
- [ ] Přepočítací součinitele teploty a seskupení jako výběr
- [ ] Všechny posudky a podmínka TN/TT v registru
- [ ] Referenční případ sedí ±1 %
- [ ] verify exit 0, render prohlédnut
