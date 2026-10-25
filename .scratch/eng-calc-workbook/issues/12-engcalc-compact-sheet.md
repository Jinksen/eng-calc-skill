# 12 — engcalc: compact check sheet (style K)

**Delivers:** class `FormSheet` in `engcalc.py` generating style K from `reference/sheet-styles.md` — identification strip, title + sketch top right, red sections, rows "description symbol = value unit" two side by side, load case table, design status with a coloured utilisation chart, calculation table LC1/LC2 with relations and √, assumptions a)–f). Same names, register and banner as `CalcSheet`.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** artboard "Target look – compact check sheet (TCC style)" on the canvas *Bearing calculation – sheet design*; `example_bearing.py` (ticket 10) as the first use.

- [ ] Cell styles `ec_input_k`, `ec_section_k`, `ec_status_k`, `ec_rel_k`
- [ ] Column grid without merging, labels aligned right
- [ ] Utilisation chart with colours by point and a 100 % line
- [ ] Sketch: `drawing_chart` with dimension texts linked to cells, or a picture
- [ ] Render through verify.py matches the artboard on 1 A4 page
