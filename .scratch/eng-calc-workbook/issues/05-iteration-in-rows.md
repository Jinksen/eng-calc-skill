# 05 — Iteration written out in rows (Colebrook, normal depth)

**Delivers:** `CalcSheet.iterate(key, label, x0, step_formula, n, tol)` — a block of iterations x_{k+1} = g(x_k) with an automatic convergence `condition`; reference build of pipe pressure loss (Darcy–Weisbach + Colebrook) with a flow-regime remark (patterns P4 + P16). Replaces Goal Seek / circular references.

**Blocked by:** Nothing — can start now.

**Status:** ready-for-agent

**Reference:** Colebrook–White; check against the explicit Haaland / Swamee–Jain relation (deviation < 2 %).

- [ ] Readable iteration block (k | x_k | residual), name on the last value
- [ ] Convergence condition and validity condition (Re > 4000)
- [ ] Works in path A too (described in patterns.md / excel-in-place.md)
- [ ] verify exit 0
