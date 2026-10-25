# 06 — FDM mřížka s barevnou škálou

**Co dodá:** `DataSheet.grid(name, rows, cols, formula)` + barevná škála + graf profilů — vzor P11 (nestacionární vedení tepla stěnou, explicitní schéma), včetně `condition` stability Fo ≤ 0,5.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

**Reference:** analytické řešení pro deskou s konstantní okrajovou teplotou (první členy řady) — porovnání ve zvoleném čase.

- [ ] Mřížka uzly × časové kroky, jeden vzorec kopírovaný přes celou oblast
- [ ] ColorScale min–střed–max, legenda teploty
- [ ] Graf T(x) pro vybrané časy a T(t) pro střed
- [ ] Odchylka od analytického řešení jako `check`, verify exit 0
