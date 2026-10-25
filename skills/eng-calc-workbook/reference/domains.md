# Fields — typical checks

The structure of the checks, not the values. Look up concrete limits, factors and tables
**always in the current standard / catalogue** and write the source into col. H. A value
without a source = a finding in review.

## Electrical (accent `BF8F00`)

| Task | Checks (`le` / `ge`) | Validity conditions |
|---|---|---|
| Cable sizing (IEC 60364-5-52, -4-43) | I_B ≤ I_n ≤ I_z·k; I_2 ≤ 1.45 I_z; ΔU ≤ ΔU_perm; k²S² ≥ I²t | installation method in the table, ambient temperature, number of loaded conductors |
| Automatic disconnection (IEC 60364-4-41) | Z_s·I_a ≤ U_0; t_disc ≤ t_max | system TN/TT/IT |
| Short-circuit currents (IEC 60909) | I″_k ≤ I_cu of the breaker; i_p ≤ dynamic withstand | voltage factor c, far / near-to-generator fault |
| Transformer, machine | temperature rise ≤ insulation class; η, losses, u_k within tolerance; B ≤ B_max of the core | steady state, sinusoidal supply |
| Instrument transformer (CT/VT) | burden ≤ rated; ALF/FS; error ≤ accuracy class | frequency, burden range 25–100 % |

Characteristics (torque, magnetisation, heating) → `91_ChartData` + XY chart; phasor diagram → live sketch.

## Mechanical (accent `2F5597`)

| Task | Checks | Validity conditions |
|---|---|---|
| Shaft | σ_eq ≤ σ_perm; fatigue safety ≥ k_min; φ ≤ φ_perm; n ≤ n_crit/k | material, notches, load cycle |
| Bolted joint / bolt group | F_v,Ed ≤ F_v,Rd; F_b,Ed ≤ F_b,Rd; F_t,Ed ≤ F_t,Rd; interaction | geometry (pitches, edge distances) |
| Weld | σ_w ≤ f_u/(β_w γ_M2) | length, throat thickness |
| Bearing | L_10h ≥ required | equivalent load, speed |
| Pressure vessel / pipe | thickness ≥ t_min + allowances; p ≤ p_perm | temperature, material |
| Flow (Darcy–Weisbach) | Δp ≤ Δp_perm; v in the recommended band | Re regime (remark + condition), relative roughness |
| Tolerances and fits (ISO 286, ISO 2768) | clearance_min ≥ 0 / interference within limits; tolerance chain T0 ≤ T0_perm (worst case and RSS) | size within the ISO 286 table interval; RSS only for a normal distribution |
| Part from a drawing (flange, bush) | t_wall ≥ t_min; m ≤ m_max; geometrical tolerances ≤ specified; edge distance and ligaments of holes | drawing and dimensions see [part-drawing.md](part-drawing.md), reference build `example_flange.py` |

Bolt group → live sketch of the pattern (XY points) + resultant.

## Civil (accent `548235`)

| Task | Checks | Validity conditions |
|---|---|---|
| Steel beam (EN 1993-1-1) | section class; M_Ed ≤ M_c,Rd; V_Ed ≤ V_pl,Rd; M+V; LTB; w ≤ L/n | see `example_ipe_beam.py` |
| RC section (EN 1992-1-1) | M_Ed ≤ M_Rd; V_Ed ≤ V_Rd; A_s,min ≤ A_s ≤ A_s,max; crack width | N–M interaction diagram (capacity envelope + effect point) |
| Slab (continuous / discontinuous edges) | span and support moments, reactions | edge support type as a selection |
| Truss | member forces (tension / compression), buckling of compression members | pinned joints |
| Actions (EN 1990/1991) | combinations 6.10 / 6.10a,b; reduction of imposed loads | category of use |

Sections and materials always as a `9x_` database with a selection (IPE pattern in the reference build).
