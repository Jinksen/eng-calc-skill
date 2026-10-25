"""Reference build: steel beam check (IPE, simply supported, UDL) per ČSN EN 1993-1-1.

Demonstrates every engcalc primitive: dropdown from a database, bounded inputs,
constants with sources, documented formulas, limit checks (le), validity
conditions, dynamic remarks, parametric sketch chart, M(x)/w(x) diagrams,
utilisation chart, rendered equations and README.

    python example_ipe_beam.py out/posudek_IPE_v1.0.xlsx
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engcalc import Col, EngWorkbook, Meta, index_match, png_from_figure, sketch_chart, xy_chart  # noqa: E402

# IPE (EN 10365): h, b, tw, tf, r [mm]; A [cm²]; Iy [cm⁴]; Wpl,y [cm³]; G [kg/m]
IPE = [
    ("IPE 100", 100, 55, 4.1, 5.7, 7, 10.3, 171, 39.4, 8.1),
    ("IPE 120", 120, 64, 4.4, 6.3, 7, 13.2, 318, 60.7, 10.4),
    ("IPE 140", 140, 73, 4.7, 6.9, 7, 16.4, 541, 88.3, 12.9),
    ("IPE 160", 160, 82, 5.0, 7.4, 9, 20.1, 869, 124, 15.8),
    ("IPE 180", 180, 91, 5.3, 8.0, 9, 23.9, 1317, 166, 18.8),
    ("IPE 200", 200, 100, 5.6, 8.5, 12, 28.5, 1943, 221, 22.4),
    ("IPE 220", 220, 110, 5.9, 9.2, 12, 33.4, 2772, 285, 26.2),
    ("IPE 240", 240, 120, 6.2, 9.8, 15, 39.1, 3892, 367, 30.7),
    ("IPE 270", 270, 135, 6.6, 10.2, 15, 45.9, 5790, 484, 36.1),
    ("IPE 300", 300, 150, 7.1, 10.7, 15, 53.8, 8356, 628, 42.2),
]
STEEL = [("S235", 235), ("S275", 275), ("S355", 355)]  # fy for t ≤ 40 mm


def beam_sketch() -> bytes:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.2, 1.5))
    ax.plot([0, 10], [0, 0], color="#1F3864", lw=4)
    for x in range(0, 11):
        ax.annotate("", xy=(x, 0.08), xytext=(x, 0.7), arrowprops=dict(arrowstyle="-|>", color="#C55A11", lw=1))
    ax.plot([0, 10], [0.7, 0.7], color="#C55A11", lw=1)
    ax.text(5, 0.82, r"$q_{Ed}$  [kN/m]", ha="center", color="#C55A11", fontsize=10)
    ax.plot([0, -0.35, 0.35, 0], [0, -0.45, -0.45, 0], color="#1F3864", lw=1.5)
    ax.plot([10, 9.65, 10.35, 10], [0, -0.45, -0.45, 0], color="#1F3864", lw=1.5)
    ax.plot([9.6, 10.4], [-0.55, -0.55], color="#1F3864", lw=1.5)
    ax.annotate("", xy=(0, -0.9), xytext=(10, -0.9), arrowprops=dict(arrowstyle="<->", color="#595959"))
    ax.text(5, -1.2, r"$L$", ha="center", fontsize=11)
    ax.set_xlim(-0.8, 10.8)
    ax.set_ylim(-1.4, 1.1)
    ax.axis("off")
    png = png_from_figure(fig)
    plt.close(fig)
    return png


def build(out: Path) -> Path:
    book = EngWorkbook(Meta(
        project="Ukázkový projekt – ocelová lávka",
        title="Posudek prostého nosníku IPE",
        subject="Stropní nosník, rovnoměrné zatížení",
        author="A. Engineer",
        checker="",
        revision="A",
        date=dt.date(2026, 10, 25),
        organisation="VŠB-TU Ostrava · FEI",
        standard="ČSN EN 1993-1-1, ČSN EN 1990",
        domain="civil",
    ))

    # -- databases ------------------------------------------------------------------- #
    db = book.data_sheet("90_Databaze", "Databáze průřezů a materiálů", "Katalog IPE (EN 10365) a ocelí — zdroj rozbalovacích seznamů")
    db.table("IPE", [
        Col("key", "Průřez"), Col("h", "h [mm]", "0"), Col("b", "b [mm]", "0"), Col("tw", "tw [mm]", "0.0"),
        Col("tf", "tf [mm]", "0.0"), Col("r", "r [mm]", "0"), Col("A", "A [cm²]", "0.0"),
        Col("Iy", "Iy [cm⁴]", "0"), Col("Wpl", "Wpl,y [cm³]", "0.0"), Col("G", "G [kg/m]", "0.0"),
    ], IPE, source="EN 10365:2017, Tab. IPE (hodnoty ověř proti katalogu výrobce)")
    db.table("steel", [Col("key", "Ocel"), Col("fy", "fy [MPa]", "0")], STEEL,
             source="ČSN EN 1993-1-1, Tab. 3.1 (t ≤ 40 mm)")
    db.close()

    # -- calculation ------------------------------------------------------------------ #
    s = book.calc_sheet("10_Posudek", "Posudek nosníku", "Vstupy, výpočet, posudky MSÚ a MSP")
    s.section("Vstupní údaje")
    s.figure(beam_sketch(), width_px=430)
    s.input("in_L", "Rozpětí nosníku", "L", 6.0, "m", lo=1.0, hi=12.0)
    s.input("in_gk", "Stálé zatížení bez vlastní tíhy", "g_k", 6.0, "kN/m", lo=0.0, hi=60.0)
    s.input("in_qk", "Proměnné zatížení", "q_k", 5.0, "kN/m", lo=0.0, hi=60.0)
    s.input("in_sec", "Průřez", "", "IPE 240", "", choices="lst_IPE")
    s.input("in_steel", "Ocel", "", "S235", "", choices="lst_steel")
    s.input("in_wlim", "Limitní průhyb jako L/n", "n", 250, "–", lo=150, hi=500, fmt="0",
            source="ČSN EN 1993-1-1 NA.2.23")
    s.input("in_ltb", "Tlačená pásnice zajištěna proti klopení (1 = ano)", "", 1, "–", lo=0, hi=1, fmt="0")

    s.section("Konstanty a součinitele")
    s.const("c_gG", "Dílčí součinitel stálého zatížení", "γ_G", 1.35, "–", source="ČSN EN 1990, Tab. A1.2(B)")
    s.const("c_gQ", "Dílčí součinitel proměnného zatížení", "γ_Q", 1.50, "–", source="ČSN EN 1990, Tab. A1.2(B)")
    s.const("c_gM0", "Dílčí součinitel odolnosti průřezu", "γ_M0", 1.00, "–", source="ČSN EN 1993-1-1, 6.1 + NA")
    s.const("c_E", "Modul pružnosti oceli", "E", 210000, "MPa", source="ČSN EN 1993-1-1, 3.2.6", fmt="0")
    s.const("c_g", "Tíhové zrychlení", "g", 9.81, "m/s²", source="konvence")
    s.const("c_eta_v", "Součinitel smykové plochy (konzervativně)", "η", 1.0, "–", source="ČSN EN 1993-1-1, 6.2.6(3)")

    s.section("Průřezové charakteristiky")
    for key, label, sym, unit, fmt in (
        ("h", "Výška průřezu", "h", "mm", "0"), ("b", "Šířka pásnice", "b", "mm", "0"),
        ("tw", "Tloušťka stojiny", "t_w", "mm", "0.0"), ("tf", "Tloušťka pásnice", "t_f", "mm", "0.0"),
        ("r", "Poloměr zaoblení", "r", "mm", "0"), ("A", "Plocha průřezu", "A", "cm²", "0.0"),
        ("Iy", "Moment setrvačnosti", "I_y", "cm⁴", "0"), ("Wpl", "Plastický průřezový modul", "W_pl,y", "cm³", "0.0"),
        ("G", "Hmotnost", "G", "kg/m", "0.0"),
    ):
        s.calc(f"calc_{key}", label, sym, index_match("IPE", key, "in_sec"), unit, fmt=fmt, source="90_Databaze")
    s.calc("calc_fy", "Mez kluzu", "f_y", index_match("steel", "fy", "in_steel"), "MPa", fmt="0", source="90_Databaze")
    s.calc("calc_eps", "Součinitel ε", "ε", "SQRT(235/calc_fy)", "–", text="ε = √(235 / f_y)", source="Tab. 5.2", fmt="0.000")

    s.section("Klasifikace průřezu")
    s.calc("calc_cf_t", "Štíhlost přečnívající pásnice", "c/t_f", "(calc_b-calc_tw-2*calc_r)/2/calc_tf", "–",
           text="c = (b − t_w − 2r)/2", source="Tab. 5.2", fmt="0.00")
    s.calc("calc_cw_t", "Štíhlost stojiny", "c/t_w", "(calc_h-2*calc_tf-2*calc_r)/calc_tw", "–",
           text="c = h − 2t_f − 2r", source="Tab. 5.2", fmt="0.00")
    s.check("chk_cl_f", "Pásnice třídy 1 (tlak)", "η_cf", "calc_cf_t", "9*calc_eps", "–", source="Tab. 5.2, 9ε")
    s.check("chk_cl_w", "Stojina třídy 1 (ohyb)", "η_cw", "calc_cw_t", "72*calc_eps", "–", source="Tab. 5.2, 72ε")

    s.section("Zatížení a účinky")
    s.calc("calc_gsw", "Vlastní tíha nosníku", "g_sw", "calc_G*c_g/1000", "kN/m", text="g_sw = G·g", fmt="0.000")
    s.calc("calc_qEd", "Návrhové zatížení MSÚ", "q_Ed", "c_gG*(in_gk+calc_gsw)+c_gQ*in_qk", "kN/m",
           text="q_Ed = γ_G(g_k + g_sw) + γ_Q q_k", source="ČSN EN 1990, 6.10", fmt="0.00")
    s.calc("calc_qk", "Charakteristické zatížení MSP", "q_k,tot", "in_gk+calc_gsw+in_qk", "kN/m",
           text="q = g_k + g_sw + q_k", source="ČSN EN 1990, 6.14b", fmt="0.00")
    s.equation(r"M_{Ed}=\frac{q_{Ed}\,L^2}{8}\qquad V_{Ed}=\frac{q_{Ed}\,L}{2}")
    s.calc("out_MEd", "Návrhový ohybový moment", "M_Ed", "calc_qEd*in_L^2/8", "kNm", text="M = q L² / 8", fmt="0.0")
    s.calc("out_VEd", "Návrhová posouvající síla", "V_Ed", "calc_qEd*in_L/2", "kN", text="V = q L / 2", fmt="0.0")

    s.section("Únosnost průřezu (MSÚ)")
    s.equation(r"M_{c,Rd}=\frac{W_{pl,y}\,f_y}{\gamma_{M0}}\qquad V_{pl,Rd}=\frac{A_v\,f_y}{\sqrt{3}\,\gamma_{M0}}")
    s.calc("out_McRd", "Ohybová únosnost", "M_c,Rd", "calc_Wpl*calc_fy/c_gM0/1000", "kNm",
           text="W_pl·f_y / γ_M0", source="6.2.5(2)", fmt="0.0")
    s.calc("calc_Av0", "Smyková plocha (válcovaný I)", "A_v", "calc_A*100-2*calc_b*calc_tf+(calc_tw+2*calc_r)*calc_tf",
           "mm²", text="A − 2b t_f + (t_w + 2r) t_f", source="6.2.6(3)a", fmt="0")
    s.calc("calc_Av", "Smyková plocha (≥ η h_w t_w)", "A_v", "MAX(calc_Av0,c_eta_v*(calc_h-2*calc_tf)*calc_tw)",
           "mm²", text="max(A_v ; η h_w t_w)", source="6.2.6(3)a", fmt="0")
    s.calc("out_VplRd", "Plastická smyková únosnost", "V_pl,Rd", "calc_Av*calc_fy/(SQRT(3)*c_gM0)/1000", "kN",
           text="A_v f_y / (√3 γ_M0)", source="6.2.6(2)", fmt="0.0")
    s.check("chk_M", "Ohyb", "η_M", "out_MEd", "out_McRd", "kNm", dec=1, source="6.2.5(1)")
    s.check("chk_V", "Smyk", "η_V", "out_VEd", "out_VplRd", "kN", dec=1, source="6.2.6(1)")
    s.remark("Interakce M + V", 'IF(out_VEd<=0.5*out_VplRd,"V_Ed ≤ 0,5 V_pl,Rd → bez redukce ohybové únosnosti",'
             '"V_Ed > 0,5 V_pl,Rd → nutná redukce (6.2.8), mimo rozsah listu")')
    s.condition("chk_MV", "Interakce M+V bez redukce", "out_VEd<=0.5*out_VplRd",
                ok="bez redukce", fail="nutná redukce 6.2.8", text="V_Ed ≤ 0,5 V_pl,Rd", source="6.2.8(2)")
    s.condition("chk_ltb", "Předpoklad: zajištění proti klopení", "in_ltb=1",
                ok="klopení vyloučeno", fail="posuď klopení (6.3.2) — mimo rozsah", source="6.3.2")

    s.section("Použitelnost (MSP)")
    s.equation(r"w=\frac{5\,q\,L^4}{384\,E\,I_y}\leq\frac{L}{n}")
    s.calc("out_w", "Průhyb uprostřed rozpětí", "w", "5*calc_qk*(in_L*1000)^4/(384*c_E*calc_Iy*10^4)", "mm",
           text="5 q L⁴ / (384 E I_y)", fmt="0.0")
    s.calc("calc_wlim", "Limitní průhyb", "w_lim", "in_L*1000/in_wlim", "mm", text="L / n", fmt="0.0")
    s.check("chk_w", "Průhyb", "η_w", "out_w", "calc_wlim", "mm", dec=1, source="NA.2.23")

    s.section("Výsledek")
    s.result("out_eta", "Maximální využití průřezu", "η_max", "MAX(chk_M,chk_V,chk_w,chk_cl_f,chk_cl_w)", "–", fmt="0.00")
    s.remark("Rezerva", 'IF(out_eta<=1,"Rezerva "&FIXED((1-out_eta)*100,0)&" % – rozhoduje "&'
             'IF(out_eta=chk_M,"ohyb",IF(out_eta=chk_V,"smyk",IF(out_eta=chk_w,"průhyb",'
             'IF(out_eta=chk_cl_f,"třída pásnice","třída stojiny")))),'
             '"Navrhni větší průřez nebo vyšší pevnost oceli")')
    s.close()

    # -- chart data -------------------------------------------------------------------- #
    gd = book.data_sheet("91_Grafdata", "Data grafů a skic", "Souřadnice parametrické skici průřezu, průběh M(x) a w(x)")
    outline = [
        ("-calc_b/2", "calc_h/2"), ("calc_b/2", "calc_h/2"), ("calc_b/2", "calc_h/2-calc_tf"),
        ("calc_tw/2", "calc_h/2-calc_tf"), ("calc_tw/2", "-calc_h/2+calc_tf"), ("calc_b/2", "-calc_h/2+calc_tf"),
        ("calc_b/2", "-calc_h/2"), ("-calc_b/2", "-calc_h/2"), ("-calc_b/2", "-calc_h/2+calc_tf"),
        ("-calc_tw/2", "-calc_h/2+calc_tf"), ("-calc_tw/2", "calc_h/2-calc_tf"), ("-calc_b/2", "calc_h/2-calc_tf"),
        ("-calc_b/2", "calc_h/2"),
    ]
    sec = gd.block("sec", [Col("i", "bod", "0"), Col("x", "y [mm]", "0.0"), Col("y", "z [mm]", "0.0")],
                   [(i, f"={x}", f"={y}") for i, (x, y) in enumerate(outline)],
                   note="Obrys průřezu bez zaoblení — kreslí se jako XY graf, mění se s výběrem průřezu")
    n = 20
    first = gd.r + 3
    rows = []
    for i in range(n + 1):
        r = first + i
        rows.append((i, f"=B{r}/MAX($B${first}:$B${first + n})*in_L", f"=calc_qEd*C{r}*(in_L-C{r})/2",
                     f"=calc_qk*(C{r}*1000)*((in_L*1000)^3-2*in_L*1000*(C{r}*1000)^2+(C{r}*1000)^3)/(24*c_E*calc_Iy*10^4)"))
    diag = gd.block("diag", [Col("i", "i", "0"), Col("x", "x [m]", "0.00"), Col("M", "M_Ed(x) [kNm]", "0.0"),
                             Col("w", "w(x) [mm]", "0.00")], rows,
                    note=f"{n + 1} bodů po délce nosníku; M = q x (L − x)/2, w = q x (L³ − 2Lx² + x³)/(24 E I); 10^4: cm⁴ → mm⁴")
    gd.close()

    # -- dashboard --------------------------------------------------------------------- #
    d = book.dashboard("01_Prehled", "Přehled", "Klíčové výsledky, skica průřezu, průběhy, využití posudků")
    d.kpis([
        ("Průřez · ocel", '=in_sec&" · "&in_steel', "", "@"),
        ("M_Ed / M_c,Rd", '=FIXED(out_MEd,1)&" / "&FIXED(out_McRd,1)', "kNm", "@"),
        ("Průhyb w / w_lim", '=FIXED(out_w,1)&" / "&FIXED(calc_wlim,1)', "mm", "@"),
        ("Využití η max", "=out_eta", "–", "0.00"),
    ])
    d.chart(sketch_chart(sec, "x", "y", half_range=170, size_cm=6.2, title="Průřez (živá skica)"), "B13")
    d.chart(xy_chart("Ohybový moment M_Ed(x)", "x [m]", "M [kNm]", [(diag, "x", "M", "M_Ed")],
                     width=11.5, height=6.2, smooth=True), "E13")
    d.chart(xy_chart("Průhyb w(x) – MSP", "x [m]", "w [mm]", [(diag, "x", "w", "w")],
                     width=11.5, height=6.2, smooth=True), "E26")
    d.utilization_chart("B39", width=18.0, height=6.5)
    d.figure(beam_sketch(), "B28", width_px=250)
    d.close(52)

    book.readme(
        purpose="Posudek prostého ocelového nosníku z válcovaného IPE při rovnoměrném zatížení: "
                "klasifikace průřezu, ohyb, smyk, interakce M+V a průhyb.",
        scope=["Prostý nosník, rovnoměrné spojité zatížení, jedno pole",
               "Průřezy IPE 100 – IPE 300, oceli S235/S275/S355, t ≤ 40 mm",
               "Průřez třídy 1 (plastická únosnost) — ověřeno posudkem klasifikace"],
        assumptions=["Klopení vyloučeno průběžným držením tlačené pásnice (jinak list hlásí NEVYHOVUJE)",
                     "Zaoblení v obrysu skici zanedbáno (jen vizualizace)",
                     "Kombinace MSP charakteristická, bez dotvarování a nadvýšení",
                     "Lokální účinky (vnesení sil, boulení stojiny) neposuzovány"],
        workflow=["Na listu 10_Posudek vyplň žluté buňky sekce 1 (rozbalovací seznamy pro průřez a ocel)",
                  "Zkontroluj banner nahoře: VŠE VYHOVUJE / NEVYHOVUJE",
                  "Podrobnosti posudků v 80_Kontroly, grafy v 01_Prehled",
                  "Při změně verze doplň revizní log níže"],
        sources=["ČSN EN 1990 Zásady navrhování konstrukcí",
                 "ČSN EN 1993-1-1 Navrhování ocelových konstrukcí – Obecná pravidla",
                 "EN 10365 Za tepla válcované ocelové profily I a H — rozměry"],
        revisions=[("2026-10-25", "A", "První vydání (referenční build skillu)", "A. Engineer", "")],
    )
    return book.save(out)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("posudek_IPE_v1.0.xlsx")
    print(build(target))
