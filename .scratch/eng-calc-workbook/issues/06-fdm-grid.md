# 06 — FDM grid with a colour scale

**Delivers:** `DataSheet.grid(name, rows, cols, formula)` + colour scale + profile chart — pattern P11 (transient heat conduction through a wall, explicit scheme), including the stability `condition` Fo ≤ 0.5.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** analytical solution for a slab with a constant boundary temperature (first terms of the series) — comparison at a chosen time.

- [ ] Grid nodes × time steps, one formula copied across the whole range
- [ ] ColorScale min–mid–max, temperature legend
- [ ] Chart T(x) for selected times and T(t) for the centre
- [ ] Deviation from the analytical solution as a `check`, verify exit 0
