# 09 — GitHub CI and release

**Delivers:** GitHub Actions (LibreOffice install, build of all reference workbooks, `verify.py` exit 0, PNG artifacts) — in place; still missing: the skill ZIP and the sample `.xlsx` attached as release assets when a tag `vX.Y.Z` is pushed.

**Blocked by:** 01 — Live test in Claude in Excel; 08 — verify completeness and banner test

**Status:** ready-for-agent

- [ ] Workflow green on a clean Ubuntu runner
- [ ] Release contains `eng-calc-workbook.zip` and the sample `.xlsx` files
- [ ] README screenshots regenerated from the render
- [ ] CHANGELOG entry for the release
