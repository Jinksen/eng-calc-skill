# 11 — Komplexní čísla a fázorový diagram

**Co dodá:** helpery `CalcSheet.complex_input(key, R, X)` a `phasor_chart()` + referenční build náhradního obvodu (např. T-článek asynchronního motoru nebo úbytek napětí na vedení s R + jX): impedance, proudy, výkony P/Q/S a cos φ přes funkce `IM*`, fázorový diagram jako živá skica.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** učebnicový příklad náhradního schématu s ručním výpočtem; kontrola P = Re(U·I*) proti U·I·cos φ.

- [ ] Vstupy R a X jako čísla s ověřením dat, komplexní buňka složená `COMPLEX`
- [ ] Zobrazení modul + úhel jako čísla s jednotkou, ne text komplexního čísla
- [ ] Bilanční `check`: S² = P² + Q² (tolerance 1e-6)
- [ ] Jen funkce, které LibreOffice přečte (bez `_xlfn.IM…H`), verify exit 0
