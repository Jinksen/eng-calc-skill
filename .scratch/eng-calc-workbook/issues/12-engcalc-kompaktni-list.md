# 12 — engcalc: kompaktní posudkový list (styl K)

**Co dodá:** třída `FormSheet` v `engcalc.py` generující styl K ze `reference/sheet-styles.md` — proužek identifikace, název + skica vpravo nahoře, červené sekce, řádky „popis symbol = hodnota jednotka“ po dvou vedle sebe, tabulka zatěžovacích stavů, stav návrhu s barevným grafem využití, tabulka výpočtu ZS1/ZS2 se vztahy a √, předpoklady a)–f). Stejná jména, registr a banner jako `CalcSheet`.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** artboard „Cílový vzhled – kompaktní posudkový list (styl TCC)“ na plátně *Výpočet ložisek – návrh listů*; `example_bearing.py` (ticket 10) jako první použití.

- [ ] Buňkové styly `ec_input_k`, `ec_section_k`, `ec_status_k`, `ec_rel_k`
- [ ] Sloupcová mřížka bez slučování, popisky zarovnané vpravo
- [ ] Graf využití s barvou podle bodu a čárou 100 %
- [ ] Skica: obrázek + text kót propojený na buňky (kde openpyxl umí) nebo XY skica
- [ ] Render přes verify.py odpovídá artboardu na 1 stranu A4
