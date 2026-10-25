# Contributing

1. Take a ticket from the queue (`.scratch/eng-calc-workbook/issues/` or GitHub Issues labelled
   `ready-for-agent`) whose blocking tickets are done.
2. A new library capability = a method in `engcalc.py` + its use in a reference build
   `scripts/example_*.py` + a description in the matching `reference/*.md`. Nothing is added
   without a reference use.
3. A visual change goes into `reference/visual-language.md` and `engcalc.py` (`C`, `GRID`,
   `_style_defs`, `_LINE`) at the same time.
4. Locally:
   ```bash
   pip install openpyxl pillow matplotlib      # + LibreOffice and poppler-utils
   python skills/eng-calc-workbook/scripts/example_ipe_beam.py out/example_ipe_beam.xlsx
   python skills/eng-calc-workbook/scripts/example_flange.py out/example_flange.xlsx
   python skills/eng-calc-workbook/scripts/verify.py out/example_flange.xlsx --render out/render
   ```
   Exit 0 is a merge condition; CI (`.github/workflows/verify.yml`) does the same for every build.
5. Values from standards and catalogues only with a source (standard, clause / table, catalogue and year).
6. Add an entry to `CHANGELOG.md`.
7. Screenshots in `docs/images/` are regenerated from the render when the look changes.
