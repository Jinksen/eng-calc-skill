# 07 — Varianty ve sloupcích

**Co dodá:** `VariantSheet` — calc pad s N sloupci variant (vstupy jako řádky, identický vzorec napříč řádkem, posudek a stav pro každou variantu, nejlepší varianta zvýrazněná) — vzor P18, náhrada What-If Data Table, kterou Claude in Excel nepodporuje.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** referenční build IPE: varianty IPE 200 / 220 / 240 / 270 se stejným zatížením.

- [ ] Jména po variantách (`out_MEd_v1`…) nebo sloupcová jména, rozhodnutí zapsat do python-engcalc.md
- [ ] Registr rozlišuje variantu; banner hodnotí zvolenou variantu
- [ ] verify lint kontroluje konzistenci vzorců napříč řádkem
