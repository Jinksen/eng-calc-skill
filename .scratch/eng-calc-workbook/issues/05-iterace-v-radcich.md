# 05 — Iterace rozepsaná v řádcích (Colebrook, normální hloubka)

**Co dodá:** `CalcSheet.iterate(key, label, x0, step_formula, n, tol)` — blok iterací x_{k+1} = g(x_k) s automatickou `condition` konvergence; referenční build tlakové ztráty potrubí (Darcy–Weisbach + Colebrook) s remark režimu proudění (vzor P4 + P16). Nahrazuje Goal Seek / cyklické odkazy.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** Colebrook–White; kontrola proti explicitnímu Haalandovu / Swameeho–Jainovu vztahu (odchylka < 2 %).

- [ ] Iterační blok čitelný (k | x_k | reziduum), jméno na poslední hodnotě
- [ ] Condition konvergence a condition platnosti (Re > 4000)
- [ ] Funguje i v cestě A (popis v patterns.md / excel-in-place.md)
- [ ] verify exit 0
