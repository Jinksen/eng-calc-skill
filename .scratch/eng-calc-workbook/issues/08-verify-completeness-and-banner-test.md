# 08 — verify: row completeness and automatic banner test

**Delivers:** `verify.py --stress` — checks that every calc pad row has a symbol, unit and (for const/check) a source; automatically pushes every numeric input beyond its upper limit, recalculates and verifies that the banner ends in ✘; reports inputs that do not switch the banner.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

- [ ] New lint rule "incomplete row" with the location and the missing field
- [ ] Stress test passes on the reference builds (every input switches the banner)
- [ ] Run time < 2 min per reference build
