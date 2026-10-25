"""Reference build: steel beam check (IPE, simply supported, UDL) per EN 1993-1-1.

Demonstrates every engcalc primitive: dropdown from a database, bounded inputs,
constants with sources, documented formulas, limit checks (le), validity
conditions, dynamic remarks, parametric sketch chart, M(x)/w(x) diagrams,
utilisation chart, rendered equations and README.

    python example_ipe_beam.py out/beam_check_IPE_v1.0.xlsx
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
        project="Reference project – steel footbridge",
        title="Simply supported IPE beam check",
        subject="Floor beam, uniformly distributed load",
        author="A. Engineer",
        checker="",
        revision="A",
        date=dt.date(2026, 10, 25),
        organisation="eng-calc-workbook",
        standard="EN 1993-1-1, EN 1990",
        domain="civil",
    ))

    # -- databases ------------------------------------------------------------------- #
    db = book.data_sheet("90_Database", "Sections and materials", "IPE catalogue (EN 10365) and steels — dropdown sources")
    db.table("IPE", [
        Col("key", "Section"), Col("h", "h [mm]", "0"), Col("b", "b [mm]", "0"), Col("tw", "tw [mm]", "0.0"),
        Col("tf", "tf [mm]", "0.0"), Col("r", "r [mm]", "0"), Col("A", "A [cm²]", "0.0"),
        Col("Iy", "Iy [cm⁴]", "0"), Col("Wpl", "Wpl,y [cm³]", "0.0"), Col("G", "G [kg/m]", "0.0"),
    ], IPE, source="EN 10365:2017, IPE table (verify against the mill catalogue)")
    db.table("steel", [Col("key", "Steel"), Col("fy", "fy [MPa]", "0")], STEEL,
             source="EN 1993-1-1, Tab. 3.1 (t ≤ 40 mm)")
    db.close()

    # -- calculation ------------------------------------------------------------------ #
    s = book.calc_sheet("10_Beam", "Beam check", "Inputs, calculation, ULS and SLS checks")
    s.section("Input data")
    s.figure(beam_sketch(), width_px=430)
    s.input("in_L", "Span", "L", 6.0, "m", lo=1.0, hi=12.0)
    s.input("in_gk", "Permanent load excluding self-weight", "g_k", 6.0, "kN/m", lo=0.0, hi=60.0)
    s.input("in_qk", "Variable load", "q_k", 5.0, "kN/m", lo=0.0, hi=60.0)
    s.input("in_sec", "Section", "", "IPE 240", "", choices="lst_IPE")
    s.input("in_steel", "Steel grade", "", "S235", "", choices="lst_steel")
    s.input("in_wlim", "Deflection limit as L/n", "n", 250, "–", lo=150, hi=500, fmt="0",
            source="EN 1993-1-1 NA.2.23")
    s.input("in_ltb", "Compression flange restrained against LTB (1 = yes)", "", 1, "–", lo=0, hi=1, fmt="0")

    s.section("Constants and factors")
    s.const("c_gG", "Partial factor, permanent actions", "γ_G", 1.35, "–", source="EN 1990, Tab. A1.2(B)")
    s.const("c_gQ", "Partial factor, variable actions", "γ_Q", 1.50, "–", source="EN 1990, Tab. A1.2(B)")
    s.const("c_gM0", "Partial factor, cross-section resistance", "γ_M0", 1.00, "–", source="EN 1993-1-1, 6.1 + NA")
    s.const("c_E", "Modulus of elasticity", "E", 210000, "MPa", source="EN 1993-1-1, 3.2.6", fmt="0")
    s.const("c_g", "Gravitational acceleration", "g", 9.81, "m/s²", source="convention")
    s.const("c_eta_v", "Shear area factor (conservative)", "η", 1.0, "–", source="EN 1993-1-1, 6.2.6(3)")

    s.section("Section properties")
    for key, label, sym, unit, fmt in (
        ("h", "Section depth", "h", "mm", "0"), ("b", "Flange width", "b", "mm", "0"),
        ("tw", "Web thickness", "t_w", "mm", "0.0"), ("tf", "Flange thickness", "t_f", "mm", "0.0"),
        ("r", "Root radius", "r", "mm", "0"), ("A", "Cross-section area", "A", "cm²", "0.0"),
        ("Iy", "Second moment of area", "I_y", "cm⁴", "0"), ("Wpl", "Plastic section modulus", "W_pl,y", "cm³", "0.0"),
        ("G", "Mass per metre", "G", "kg/m", "0.0"),
    ):
        s.calc(f"calc_{key}", label, sym, index_match("IPE", key, "in_sec"), unit, fmt=fmt, source="90_Database")
    s.calc("calc_fy", "Yield strength", "f_y", index_match("steel", "fy", "in_steel"), "MPa", fmt="0", source="90_Database")
    s.calc("calc_eps", "Factor ε", "ε", "SQRT(235/calc_fy)", "–", text="ε = √(235 / f_y)", source="Tab. 5.2", fmt="0.000")

    s.section("Section classification")
    s.calc("calc_cf_t", "Outstand flange slenderness", "c/t_f", "(calc_b-calc_tw-2*calc_r)/2/calc_tf", "–",
           text="c = (b − t_w − 2r)/2", source="Tab. 5.2", fmt="0.00")
    s.calc("calc_cw_t", "Web slenderness", "c/t_w", "(calc_h-2*calc_tf-2*calc_r)/calc_tw", "–",
           text="c = h − 2t_f − 2r", source="Tab. 5.2", fmt="0.00")
    s.check("chk_cl_f", "Flange class 1 (compression)", "η_cf", "calc_cf_t", "9*calc_eps", "–", source="Tab. 5.2, 9ε")
    s.check("chk_cl_w", "Web class 1 (bending)", "η_cw", "calc_cw_t", "72*calc_eps", "–", source="Tab. 5.2, 72ε")

    s.section("Actions and effects")
    s.calc("calc_gsw", "Self-weight of the beam", "g_sw", "calc_G*c_g/1000", "kN/m", text="g_sw = G·g", fmt="0.000")
    s.calc("calc_qEd", "Design load ULS", "q_Ed", "c_gG*(in_gk+calc_gsw)+c_gQ*in_qk", "kN/m",
           text="q_Ed = γ_G(g_k + g_sw) + γ_Q q_k", source="EN 1990, 6.10", fmt="0.00")
    s.calc("calc_qk", "Characteristic load SLS", "q_k,tot", "in_gk+calc_gsw+in_qk", "kN/m",
           text="q = g_k + g_sw + q_k", source="EN 1990, 6.14b", fmt="0.00")
    s.equation(r"M_{Ed}=\frac{q_{Ed}\,L^2}{8}\qquad V_{Ed}=\frac{q_{Ed}\,L}{2}")
    s.calc("out_MEd", "Design bending moment", "M_Ed", "calc_qEd*in_L^2/8", "kNm", text="M = q L² / 8", fmt="0.0")
    s.calc("out_VEd", "Design shear force", "V_Ed", "calc_qEd*in_L/2", "kN", text="V = q L / 2", fmt="0.0")

    s.section("Cross-section resistance (ULS)")
    s.equation(r"M_{c,Rd}=\frac{W_{pl,y}\,f_y}{\gamma_{M0}}\qquad V_{pl,Rd}=\frac{A_v\,f_y}{\sqrt{3}\,\gamma_{M0}}")
    s.calc("out_McRd", "Bending resistance", "M_c,Rd", "calc_Wpl*calc_fy/c_gM0/1000", "kNm",
           text="W_pl·f_y / γ_M0", source="6.2.5(2)", fmt="0.0")
    s.calc("calc_Av0", "Shear area (rolled I)", "A_v", "calc_A*100-2*calc_b*calc_tf+(calc_tw+2*calc_r)*calc_tf",
           "mm²", text="A − 2b t_f + (t_w + 2r) t_f", source="6.2.6(3)a", fmt="0")
    s.calc("calc_Av", "Shear area (≥ η h_w t_w)", "A_v", "MAX(calc_Av0,c_eta_v*(calc_h-2*calc_tf)*calc_tw)",
           "mm²", text="max(A_v ; η h_w t_w)", source="6.2.6(3)a", fmt="0")
    s.calc("out_VplRd", "Plastic shear resistance", "V_pl,Rd", "calc_Av*calc_fy/(SQRT(3)*c_gM0)/1000", "kN",
           text="A_v f_y / (√3 γ_M0)", source="6.2.6(2)", fmt="0.0")
    s.check("chk_M", "Bending", "η_M", "out_MEd", "out_McRd", "kNm", dec=1, source="6.2.5(1)")
    s.check("chk_V", "Shear", "η_V", "out_VEd", "out_VplRd", "kN", dec=1, source="6.2.6(1)")
    s.remark("Interaction M + V", 'IF(out_VEd<=0.5*out_VplRd,"V_Ed ≤ 0.5 V_pl,Rd → no reduction of the bending resistance",'
             '"V_Ed > 0.5 V_pl,Rd → reduction required (6.2.8), outside the scope of this sheet")')
    s.condition("chk_MV", "M+V interaction without reduction", "out_VEd<=0.5*out_VplRd",
                ok="no reduction", fail="reduction 6.2.8 required", text="V_Ed ≤ 0.5 V_pl,Rd", source="6.2.8(2)")
    s.condition("chk_ltb", "Assumption: restrained against lateral-torsional buckling", "in_ltb=1",
                ok="LTB excluded", fail="check LTB (6.3.2) — outside scope", source="6.3.2")

    s.section("Serviceability (SLS)")
    s.equation(r"w=\frac{5\,q\,L^4}{384\,E\,I_y}\leq\frac{L}{n}")
    s.calc("out_w", "Midspan deflection", "w", "5*calc_qk*(in_L*1000)^4/(384*c_E*calc_Iy*10^4)", "mm",
           text="5 q L⁴ / (384 E I_y)", fmt="0.0")
    s.calc("calc_wlim", "Deflection limit", "w_lim", "in_L*1000/in_wlim", "mm", text="L / n", fmt="0.0")
    s.check("chk_w", "Deflection", "η_w", "out_w", "calc_wlim", "mm", dec=1, source="NA.2.23")

    s.section("Result")
    s.result("out_eta", "Maximum utilisation", "η_max", "MAX(chk_M,chk_V,chk_w,chk_cl_f,chk_cl_w)", "–", fmt="0.00")
    s.remark("Reserve", 'IF(out_eta<=1,"Reserve "&FIXED((1-out_eta)*100,0)&" % – governed by "&'
             'IF(out_eta=chk_M,"bending",IF(out_eta=chk_V,"shear",IF(out_eta=chk_w,"deflection",'
             'IF(out_eta=chk_cl_f,"flange class","web class")))),'
             '"Choose a larger section or a higher steel grade")')
    s.close()

    # -- chart data -------------------------------------------------------------------- #
    gd = book.data_sheet("91_ChartData", "Chart and sketch data", "Coordinates of the parametric section sketch, M(x) and w(x)")
    outline = [
        ("-calc_b/2", "calc_h/2"), ("calc_b/2", "calc_h/2"), ("calc_b/2", "calc_h/2-calc_tf"),
        ("calc_tw/2", "calc_h/2-calc_tf"), ("calc_tw/2", "-calc_h/2+calc_tf"), ("calc_b/2", "-calc_h/2+calc_tf"),
        ("calc_b/2", "-calc_h/2"), ("-calc_b/2", "-calc_h/2"), ("-calc_b/2", "-calc_h/2+calc_tf"),
        ("-calc_tw/2", "-calc_h/2+calc_tf"), ("-calc_tw/2", "calc_h/2-calc_tf"), ("-calc_b/2", "calc_h/2-calc_tf"),
        ("-calc_b/2", "calc_h/2"),
    ]
    sec = gd.block("sec", [Col("i", "point", "0"), Col("x", "y [mm]", "0.0"), Col("y", "z [mm]", "0.0")],
                   [(i, f"={x}", f"={y}") for i, (x, y) in enumerate(outline)],
                   note="Section outline without root radii — drawn as an XY chart, follows the section dropdown")
    n = 20
    first = gd.r + 3
    rows = []
    for i in range(n + 1):
        r = first + i
        rows.append((i, f"=B{r}/MAX($B${first}:$B${first + n})*in_L", f"=calc_qEd*C{r}*(in_L-C{r})/2",
                     f"=calc_qk*(C{r}*1000)*((in_L*1000)^3-2*in_L*1000*(C{r}*1000)^2+(C{r}*1000)^3)/(24*c_E*calc_Iy*10^4)"))
    diag = gd.block("diag", [Col("i", "i", "0"), Col("x", "x [m]", "0.00"), Col("M", "M_Ed(x) [kNm]", "0.0"),
                             Col("w", "w(x) [mm]", "0.00")], rows,
                    note=f"{n + 1} points along the beam; M = q x (L − x)/2, w = q x (L³ − 2Lx² + x³)/(24 E I); 10^4: cm⁴ → mm⁴")
    gd.close()

    # -- dashboard --------------------------------------------------------------------- #
    d = book.dashboard("01_Overview", "Overview", "Key results, section sketch, diagrams, check utilisation")
    d.kpis([
        ("Section · steel", '=in_sec&" · "&in_steel', "", "@"),
        ("M_Ed / M_c,Rd", '=FIXED(out_MEd,1)&" / "&FIXED(out_McRd,1)', "kNm", "@"),
        ("Deflection w / w_lim", '=FIXED(out_w,1)&" / "&FIXED(calc_wlim,1)', "mm", "@"),
        ("Utilisation η max", "=out_eta", "–", "0.00"),
    ])
    d.chart(sketch_chart(sec, "x", "y", half_range=170, size_cm=6.2, title="Section (live sketch)"), "B13")
    d.chart(xy_chart("Bending moment M_Ed(x)", "x [m]", "M [kNm]", [(diag, "x", "M", "M_Ed")],
                     width=11.5, height=6.2, smooth=True), "E13")
    d.chart(xy_chart("Deflection w(x) – SLS", "x [m]", "w [mm]", [(diag, "x", "w", "w")],
                     width=11.5, height=6.2, smooth=True), "E26")
    d.utilization_chart("B39", width=18.0, height=6.5)
    d.figure(beam_sketch(), "B28", width_px=250)
    d.close(52)

    # -- printable calculation report ---------------------------------------------------- #
    rp = book.report_sheet("70_Report", "Calculation report",
                           "Printable report: inputs, relations with substituted values, M(x) table, checks, signatures")
    rp.fields([("Span L", "=in_L", "m", "0.00"), ("Permanent load g_k", "=in_gk", "kN/m", "0.00"),
               ("Variable load q_k", "=in_qk", "kN/m", "0.00"), ("Section", "=in_sec", "", "@"),
               ("Steel grade", "=in_steel", "", "@"), ("Deflection limit L/n", "=in_wlim", "–", "0")],
              title="Input data")
    rp.figure(beam_sketch(), at="right", caption="Static scheme: simply supported beam, UDL")
    rp.fields([("Section depth h", "=calc_h", "mm", "0"), ("Plastic modulus W_pl,y", "=calc_Wpl", "cm³", "0.0"),
               ("Second moment I_y", "=calc_Iy", "cm⁴", "0"), ("Yield strength f_y", "=calc_fy", "MPa", "0")],
              title="Section and material")
    rp.panel("Maximum utilisation η", "=out_eta", "governing check", "0.00",
             tiles=[("M_Ed [kNm]", "=out_MEd", "0.0"), ("V_Ed [kN]", "=out_VEd", "0.0"), ("w [mm]", "=out_w", "0.0")])
    rp.status()

    rp.section("Calculation procedure")
    rp.step("calc_qEd", "Design load (ULS)", "q_Ed", "γ_G·(g_k + g_sw) + γ_Q·q_k", "kN/m",
            values="{c_gG}·({in_gk} + {calc_gsw:3}) + {c_gQ}·{in_qk}", source="EN 1990, 6.10")
    rp.step("out_MEd", "Design bending moment", "M_Ed", "q_Ed·L²/8", "kNm", fmt="0.0",
            latex=r"M_{Ed}=\frac{q_{Ed}\,L^2}{8}", values="{calc_qEd}·{in_L}²/8")
    rp.step("out_VEd", "Design shear force", "V_Ed", "q_Ed·L/2", "kN", fmt="0.0", values="{calc_qEd}·{in_L}/2")
    rp.step("out_McRd", "Bending resistance", "M_c,Rd", "W_pl,y·f_y/γ_M0", "kNm", fmt="0.0",
            latex=r"M_{c,Rd}=\frac{W_{pl,y}\,f_y}{\gamma_{M0}}", values="{calc_Wpl:1}·10³·{calc_fy:0}/{c_gM0}·10⁻⁶",
            source="EN 1993-1-1, 6.2.5(2)")
    rp.step("out_VplRd", "Plastic shear resistance", "V_pl,Rd", "A_v·f_y/(√3·γ_M0)", "kN", fmt="0.0",
            values="{calc_Av:0}·{calc_fy:0}/(√3·{c_gM0})·10⁻³", source="6.2.6(2)")
    rp.step("out_w", "Midspan deflection (SLS)", "w", "5·q·L⁴/(384·E·I_y)", "mm", fmt="0.0",
            latex=r"w=\frac{5\,q\,L^4}{384\,E\,I_y}",
            values="5·{calc_qk}·{in_L}⁴·10¹²/(384·{c_E:0}·{calc_Iy:0}·10⁴)", source="SLS, char. combination")
    rp.check_step("chk_M", "Bending check", "M_Ed ≤ M_c,Rd")
    rp.check_step("chk_V", "Shear check", "V_Ed ≤ V_pl,Rd")
    rp.check_step("chk_w", "Deflection check", "w ≤ L/n")

    rp.section("Internal forces along the beam")
    rp.table([Col("i", "i", "0"), Col("x", "x [m]", "0.00"), Col("M", "M_Ed [kNm]", "0.0"), Col("w", "w [mm]", "0.00")],
             [(i, f"=INDEX(gd_diag_x,{i + 1})", f"=INDEX(gd_diag_M,{i + 1})", f"=INDEX(gd_diag_w,{i + 1})")
              for i in range(n + 1)],
             at="left", spans=(1, 1, 2, 2), total={"M": "MAX", "w": "MAX"}, total_label="max")
    rp.chart(xy_chart("M_Ed(x)", "x [m]", "M [kNm]", [(diag, "x", "M", "M_Ed")], width=9.5, height=6.0, smooth=True))
    rp.chart(xy_chart("w(x)", "x [m]", "w [mm]", [(diag, "x", "w", "w")], width=9.5, height=6.0, smooth=True))
    rp.checks()
    rp.notes(["Lateral-torsional buckling prevented by continuous restraint of the compression flange.",
              "Class 1 section, plastic resistance; root radii neglected in the sketch only.",
              "SLS characteristic combination, no pre-camber; local effects (load introduction, web "
              "buckling) are not checked."])
    rp.signatures()
    rp.close()

    book.readme(
        purpose="Check of a simply supported rolled IPE steel beam under a uniformly distributed load: "
                "section classification, bending, shear, M+V interaction and deflection.",
        scope=["Simply supported beam, uniformly distributed load, single span",
               "Sections IPE 100 – IPE 300, steels S235/S275/S355, t ≤ 40 mm",
               "Class 1 section (plastic resistance) — verified by the classification check"],
        assumptions=["Lateral-torsional buckling prevented by continuous restraint of the compression flange "
                     "(otherwise the sheet reports FAILS)",
                     "Root radii neglected in the sketch outline (visualisation only)",
                     "SLS characteristic combination, no creep, no pre-camber",
                     "Local effects (load introduction, web buckling) not checked"],
        workflow=["On 10_Beam fill the yellow cells of section 1 (dropdowns for section and steel)",
                  "Read the banner at the top: ALL CHECKS SATISFIED / FAILS",
                  "Details of the checks in 80_Checks, charts in 01_Overview",
                  "Add a line to the revision log below when issuing a new revision"],
        sources=["EN 1990 Basis of structural design",
                 "EN 1993-1-1 Design of steel structures – General rules",
                 "EN 10365 Hot rolled steel channels, I and H sections — dimensions"],
        revisions=[("2026-10-25", "A", "First issue (skill reference build)", "A. Engineer", "")],
    )
    return book.save(out)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("beam_check_IPE_v1.0.xlsx")
    print(build(target))
