# 03 — Kapacitní obálka + bod účinku (interakční diagram)

**Co dodá:** helper `capacity_chart()` a `CalcSheet.inside_polygon()` (condition „bod účinku uvnitř obálky“) — vzor P15 z posledního referenčního obrázku (interakční diagram ŽB sloupu). Použití v referenčním buildu.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** ČSN EN 1992-1-1 interakční diagram obdélníkového průřezu (body: čistý tlak, vyvážený stav, čistý ohyb, čistý tah); hodnoty ověřit proti příkladu z literatury.

- [ ] Obálka = série bloku bodů, účinek = jednobodová série jinou barvou
- [ ] Condition „uvnitř“ počítaná vzorcem (paprsek z počátku / lineární interpolace), bez maker
- [ ] η = |účinek| / |obálka ve směru účinku| jako `check`
- [ ] Referenční build + verify exit 0
