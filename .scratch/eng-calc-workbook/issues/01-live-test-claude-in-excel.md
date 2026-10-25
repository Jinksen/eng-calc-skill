# 01 — Živý test v Claude in Excel

**Co dodá:** ověření, že cesta A funguje bez Pythonu: Claude in Excel se zapnutým skillem postaví v prázdném sešitu posudek nosníku IPE (stejné zadání jako `example_ipe_beam.py`) a výsledek se shoduje s referenčním buildem.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** `scripts/example_ipe_beam.py` (η_M = 0,84; η_w = 0,97 pro IPE 240, S235, L = 6 m, g_k = 6, q_k = 5 kN/m).

- [ ] Skill nahraný a zapnutý, prompt „Postav posudek nosníku IPE podle skillu eng-calc-workbook“
- [ ] Zapsat, co Claude in Excel umí / neumí: styly buňky, pojmenované oblasti, CF se vzorcem, ověření dat, grafy, ochrana listu, tisk
- [ ] η_M a η_w ±0,01 proti referenci; banner reaguje na L = 15 m (mimo rozsah)
- [ ] Odchylky promítnuté do `reference/excel-in-place.md` (tabulka náhrad)
