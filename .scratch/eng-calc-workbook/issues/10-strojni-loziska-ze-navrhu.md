# 10 — Referenční build strojní: valivé ložisko (z návrhu na plátně)

**Co dodá:** `example_bearing.py` — sešit podle schváleného návrhu „Výpočet ložisek – návrh listů“: výběr ložiska z katalogu, interpolace e/Y, větev X/Y, trvanlivost L₁₀ₕ s a₁, statická bezpečnost s₀, otáčky, minimální zatížení, teplota; přehled s křivkou L₁₀ₕ(n) a seznamem vyhovujících ložisek.

**Blokováno:** Nic — lze začít hned (připomínky z plátna zapracovat jako první krok).

**Status:** ready-for-agent

**Reference:** ČSN ISO 281, ČSN ISO 76; kontrolní případ 6206, F_r = 2 kN, F_a = 0,5 kN, n = 1450 min⁻¹ → P = 2,00 kN, L₁₀ = 1045,7 mil. ot., L₁₀ₕ = 12 019 h, s₀ = 5,60. Katalogové hodnoty ověřit v aktuálním katalogu výrobce.

- [ ] `CalcSheet.interp()` — interpolace v tabulce s `condition` „v rozsahu tabulky“ (kompatibilní INDEX/MATCH)
- [ ] Křivka L₁₀ₕ(n) s čárou požadavku a pracovním bodem
- [ ] Kontrolní případ sedí ±0,5 %
- [ ] verify exit 0, render odpovídá návrhu
