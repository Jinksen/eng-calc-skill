# 03 — Capacity envelope + effect point (interaction diagram)

**Delivers:** helper `capacity_chart()` and `CalcSheet.inside_polygon()` (condition "effect point inside the envelope") — pattern P15 (interaction diagram of an RC column). Used in a reference build.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** EN 1992-1-1 interaction diagram of a rectangular section (points: pure compression, balanced point, pure bending, pure tension); values checked against a worked example from the literature.

- [ ] Envelope = series from a block of points, effect = one-point series in another colour
- [ ] "Inside" condition computed by formula (ray from the origin / linear interpolation), no macros
- [ ] η = |effect| / |envelope in the direction of the effect| as a `check`
- [ ] Reference build + verify exit 0
