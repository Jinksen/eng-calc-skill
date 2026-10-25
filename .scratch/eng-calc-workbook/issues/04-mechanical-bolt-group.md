# 04 — Mechanical reference build: eccentrically loaded bolt group

**Delivers:** `example_bolt_group.py` — table of bolt coordinates (input), centroid, polar moment, force on the farthest bolt, shear / bearing checks, live sketch of the bolt pattern with the resultant vector (patterns P6 + P13).

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** EN 1993-1-8 (bolt resistances, pitches and edge distances as `condition`s); elastic instantaneous-centre method — hand example.

- [ ] Input table of bolts with data validation (coordinate range), variable number of rows up to 16
- [ ] Sketch: bolts as markers (or circles via `drawing_chart`), resultant as a two-point series
- [ ] Checks and geometric conditions in the register
- [ ] Reference case matches ±1 %, verify exit 0
