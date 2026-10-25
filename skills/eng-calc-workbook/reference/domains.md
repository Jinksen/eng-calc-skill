# Obory — typické posudky

Struktura posudků, ne hodnoty. Konkrétní meze, součinitele a tabulky **vždy dohledej v
platné normě / katalogu** a zapiš zdroj do sl. H. Hodnota bez zdroje = nález v revizi.

## Elektro (akcent `BF8F00`)

| Úloha | Posudky (`le` / `ge`) | Podmínky platnosti |
|---|---|---|
| Dimenzování kabelu (ČSN 33 2000-5-52, -4-43) | I_B ≤ I_n ≤ I_z·k; I_2 ≤ 1,45 I_z; ΔU ≤ ΔU_dov; k²S² ≥ I²t | způsob uložení v tabulce, teplota okolí, počet zatížených vodičů |
| Automatické odpojení (ČSN 33 2000-4-41) | Z_s·I_a ≤ U_0; t_odp ≤ t_max | soustava TN/TT/IT |
| Zkratové poměry (ČSN EN 60909) | I″_k ≤ I_cu jističe; i_p ≤ dynamická odolnost | napěťový součinitel c, vzdálený/blízký zkrat |
| Transformátor, stroj | oteplení ≤ třída izolace; η, ztráty, u_k v toleranci; B ≤ B_max jádra | ustálený stav, sinusové napájení |
| Přístrojový transformátor (JTP/MTP) | zátěž ≤ jmenovitá; ALF/FS; chyba ≤ třída přesnosti | kmitočet, rozsah zatížení 25–100 % |

Charakteristiky (momentová, magnetizační, oteplovací) → `91_Grafdata` + XY graf; fázorový
diagram → živá skica.

## Strojní (akcent `2F5597`)

| Úloha | Posudky | Podmínky platnosti |
|---|---|---|
| Hřídel | σ_red ≤ σ_dov; k_únava ≥ k_min; φ ≤ φ_dov; n ≤ n_krit/k | materiál, vruby, cyklus |
| Šroubový spoj / skupina šroubů | F_v,Ed ≤ F_v,Rd; F_b,Ed ≤ F_b,Rd; F_t,Ed ≤ F_t,Rd; interakce | geometrie (rozteče, vzdálenosti od okraje) |
| Svar | σ_w ≤ f_u/(β_w γ_M2) | délka, tloušťka |
| Ložisko | L_10h ≥ požadovaná | ekvivalentní zatížení, otáčky |
| Tlaková nádoba / potrubí | tloušťka ≥ t_min + přídavky; p ≤ p_dov | teplota, materiál |
| Tolerance a uložení (ČSN EN ISO 286, ISO 2768) | vůle_min ≥ 0 / přesah v mezích; rozměrový řetězec T0 ≤ T0_dov (nejhorší případ i RSS) | rozměr v intervalu tabulky ISO 286; RSS jen při normálním rozdělení |
| Díl z výkresu (příruba, pouzdro) | t_stěny ≥ t_min; m ≤ m_max; geometrické tolerance ≤ předepsané | výkres + kóty viz [part-drawing.md](part-drawing.md) |
| Proudění (Darcy–Weisbach) | Δp ≤ Δp_dov; v v doporučeném pásmu | Re režim (remark + condition), relativní drsnost |

Skupina šroubů → živá skica rozmístění (XY body) + výslednice.

## Stavební (akcent `548235`)

| Úloha | Posudky | Podmínky platnosti |
|---|---|---|
| Ocelový nosník (ČSN EN 1993-1-1) | třída průřezu; M_Ed ≤ M_c,Rd; V_Ed ≤ V_pl,Rd; M+V; klopení; w ≤ L/n | viz `example_ipe_beam.py` |
| ŽB průřez (ČSN EN 1992-1-1) | M_Ed ≤ M_Rd; V_Ed ≤ V_Rd; A_s,min ≤ A_s ≤ A_s,max; šířka trhlin | interakční diagram N–M (kapacitní obálka + bod účinku) |
| Deska (spojité/nespojité okraje) | momenty v polích a nad podporami, reakce do podpor | typ uložení okrajů jako výběr |
| Příhradovina | síly v prutech (tah/tlak), vzpěr tlačených prutů | kloubové styčníky |
| Zatížení (ČSN EN 1990/1991) | kombinace 6.10 / 6.10a,b; redukce užitného | kategorie užití |

Průřezy a materiály vždy jako databáze `9x_` s výběrem (vzor IPE v referenčním buildu).
