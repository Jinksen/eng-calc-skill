# Jak přispívat

1. Vezmi ticket z fronty (`.scratch/eng-calc-workbook/issues/` nebo GitHub Issues se štítkem
   `ready-for-agent`), jehož blokující tickety jsou hotové.
2. Nová schopnost knihovny = metoda v `engcalc.py` + použití v referenčním buildu
   `scripts/example_*.py` + popis v příslušném `reference/*.md`. Bez referenčního použití se nepřidává.
3. Vizuální změna se dělá v `reference/visual-language.md` a zároveň v `engcalc.py` (`C`, `GRID`, `_style_defs`).
4. Lokálně:
   ```bash
   pip install openpyxl pillow matplotlib      # + LibreOffice a poppler-utils
   python skills/eng-calc-workbook/scripts/example_ipe_beam.py out/ipe.xlsx
   python skills/eng-calc-workbook/scripts/verify.py out/ipe.xlsx --render out/render
   ```
   exit 0 je podmínka merge; CI (`.github/workflows/verify.yml`) dělá totéž pro všechny buildy.
5. Hodnoty z norem a katalogů jen se zdrojem (norma, článek / tabulka, katalog a rok).
6. Záznam do `CHANGELOG.md`.
