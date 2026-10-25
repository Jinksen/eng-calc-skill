"""Reference build: flange with bore fit, general tolerances, tolerance chain and a live drawing.

Demonstrates the part-drawing toolkit of engcalc: ISO 286 fit lookup (H7 / shaft field),
ISO 2768-1 general tolerances, worst-case and RSS tolerance stack-up, hole pattern and wall
checks, mass, automatic drawing scale (ISO 5455) and a parametric drawing — section A–A with
live hatching, dimensions with tolerances linked to cells, front view with the bolt pattern,
GD&T frames and an ISO 7200 title block.

    python example_flange.py out/flange_check_v1.0.xlsx
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engcalc import (  # noqa: E402
    Col, DrawSeries, EngWorkbook, Meta, drawing_chart, index_match, interval_lookup, tol_text,
)

# ISO 286-2 (excerpt): size ranges up to (mm); IT6, IT7 (µm); fundamental deviations of shafts (µm):
# f, g, h = upper deviation es; k, p = lower deviation ei (k for IT5…IT7)
ISO286 = [
    (3, 6, 10, -6, -2, 0, 0, 6),
    (6, 8, 12, -10, -4, 0, 1, 12),
    (10, 9, 15, -13, -5, 0, 1, 15),
    (18, 11, 18, -16, -6, 0, 1, 18),
    (30, 13, 21, -20, -7, 0, 2, 22),
    (50, 16, 25, -25, -9, 0, 2, 26),
    (80, 19, 30, -30, -10, 0, 2, 32),
    (120, 22, 35, -36, -12, 0, 3, 37),
    (180, 25, 40, -43, -14, 0, 3, 43),
]
# shaft field → column in ISO286 (1 = f … 5 = p), which deviation the table gives (1 = es, 2 = ei)
FITS = [("f6", 1, 1, "clearance"), ("g6", 2, 1, "clearance (sliding)"), ("h6", 3, 1, "clearance / locational"),
        ("k6", 4, 2, "transition"), ("p6", 5, 2, "interference")]
# ISO 2768-1 linear dimensions: size ranges up to (mm), permissible deviations ± (mm) for f / m / c
GEN = [(3, 0.05, 0.1, 0.2), (6, 0.05, 0.1, 0.3), (30, 0.1, 0.2, 0.5), (120, 0.15, 0.3, 0.8),
       (400, 0.2, 0.5, 1.2), (1000, 0.3, 0.8, 2.0)]
GEN_CLASSES = [("f", 1, "fine"), ("m", 2, "medium"), ("c", 3, "coarse")]
MATERIALS = [("S235JR", 7850), ("C45", 7850), ("16MnCr5", 7850), ("EN-GJL-250", 7200), ("EN AW-6082", 2700)]
SCALES = [("1:10", 0.1), ("1:5", 0.2), ("1:2", 0.5), ("1:1", 1), ("2:1", 2), ("5:1", 5)]  # ascending factor

DATA = "92_DrawingData"


def X(e: str) -> str:
    """Section view: model x [mm] → drawing x [paper mm]."""
    return f"calc_ox+({e})*calc_sc"


def Y(e: str) -> str:
    return f"({e})*calc_sc"


def gen_tol(x: str) -> str:
    """ISO 2768-1 deviation ± for size x in the selected class."""
    return interval_lookup("CHOOSE(calc_gcol,db_gen_f,db_gen_m,db_gen_c)", "db_gen_key", x)


def build(out: Path) -> Path:
    book = EngWorkbook(Meta(
        project="Reference project – drive unit",
        title="Flange: fit, tolerances and drawing",
        subject="Flange with hub, H7 bore, bolt pattern",
        author="A. Engineer",
        checker="",
        revision="A",
        date=dt.date(2026, 10, 25),
        organisation="eng-calc-workbook",
        standard="ISO 286, ISO 2768-1, ISO 1101, ISO 128",
        domain="mechanical",
    ))

    # -- databases ------------------------------------------------------------------------ #
    db = book.data_sheet("90_Database", "Tolerance tables, materials, scales",
                         "ISO 286 and ISO 2768 excerpts, materials, drawing scales — sources of the dropdowns")
    db.table("iso286", [Col("key", "up to [mm]", "0"), Col("IT6", "IT6 [µm]", "0"), Col("IT7", "IT7 [µm]", "0"),
                        Col("f", "f es [µm]", "0"), Col("g", "g es [µm]", "0"), Col("h", "h es [µm]", "0"),
                        Col("k", "k ei [µm]", "0"), Col("p", "p ei [µm]", "0")], ISO286,
             source="ISO 286-2:2010, Tab. 1 and fundamental deviations (excerpt — check against the standard)")
    db.table("fit", [Col("key", "Shaft field"), Col("col", "column", "0"), Col("side", "1 = es, 2 = ei", "0"),
                     Col("type", "Fit with H7")], FITS, source="ISO 286-1:2010, 4.3")
    db.table("gen", [Col("key", "up to [mm]", "0"), Col("f", "f ± [mm]", "0.00"), Col("m", "m ± [mm]", "0.00"),
                     Col("c", "c ± [mm]", "0.00")], GEN, source="ISO 2768-1:1989, Tab. 1 (from 0.5 mm)")
    db.table("gencls", [Col("key", "Class"), Col("col", "column", "0"), Col("name", "Name")], GEN_CLASSES,
             source="ISO 2768-1:1989")
    db.table("mat", [Col("key", "Material"), Col("rho", "ρ [kg/m³]", "0")], MATERIALS,
             source="EN 10025-2, EN 10083-2, EN 10084, EN 1561, EN 573-3 (typical densities)")
    db.table("scale", [Col("key", "Scale"), Col("f", "factor", "0.0")], SCALES, source="ISO 5455:1979")
    db.close()

    # -- calculation ----------------------------------------------------------------------- #
    s = book.calc_sheet("10_Flange", "Flange check", "Inputs, fit, general tolerances, tolerance chain, checks")
    s.section("Geometry")
    s.input("in_D", "Flange outer diameter", "D", 100, "mm", lo=40, hi=300, fmt="0.0")
    s.input("in_t", "Flange thickness", "t", 8, "mm", lo=3, hi=40, fmt="0.0")
    s.input("in_Dh", "Hub diameter", "D_h", 44, "mm", lo=15, hi=200, fmt="0.0")
    s.input("in_Lh", "Hub length", "L_h", 26, "mm", lo=5, hi=150, fmt="0.0")
    s.input("in_dbore", "Bore diameter (nominal)", "d", 20, "mm", lo=3, hi=180, fmt="0.0")
    s.input("in_c", "Hub chamfer 45°", "c", 1, "mm", lo=0, hi=5, fmt="0.0")
    s.input("in_Dk", "Bolt circle diameter", "D_k", 70, "mm", lo=20, hi=280, fmt="0.0")
    s.input("in_dhole", "Bolt hole diameter", "d_h", 9, "mm", lo=3, hi=30, fmt="0.0")
    s.input("in_n", "Number of bolt holes", "n", 4, "–", lo=3, hi=12, fmt="0")
    s.input("in_mat", "Material", "", "C45", "", choices="lst_mat")
    s.calc("calc_L", "Overall length", "L", "in_t+in_Lh", "mm", text="L = t + L_h", fmt="0.0")

    s.section("Requirements")
    s.input("in_fit", "Shaft tolerance field (bore is H7)", "", "g6", "", choices="lst_fit")
    s.input("in_cl_min", "Required minimum clearance", "s_min,req", 0, "µm", lo=-100, hi=200, fmt="0")
    s.input("in_cl_max", "Allowed maximum clearance", "s_max,req", 50, "µm", lo=1, hi=300, fmt="0")
    s.input("in_gen", "General tolerance class ISO 2768-1", "", "m", "", choices="lst_gencls")
    s.input("in_A1", "Housing recess depth", "A_1", 35, "mm", lo=10, hi=300, fmt="0.00")
    s.input("in_TA1", "Tolerance of A_1 (±)", "T_1", 0.05, "mm", lo=0.005, hi=1, fmt="0.000")
    s.input("in_s_min", "Required minimum axial gap", "s_min", 0.2, "mm", lo=0, hi=5, fmt="0.00")
    s.input("in_s_max", "Allowed maximum axial gap", "s_max", 1.8, "mm", lo=0.1, hi=10, fmt="0.00")
    s.input("in_tw_min", "Minimum hub wall", "t_w,min", 3, "mm", lo=1, hi=30, fmt="0.0")
    s.input("in_dw", "Washer outer diameter", "d_w", 16, "mm", lo=5, hi=60, fmt="0.0")
    s.input("in_dbolt", "Bolt diameter", "d_b", 8, "mm", lo=3, hi=30, fmt="0.0")
    s.input("in_gt_pos", "Position tolerance of the holes", "t_pos", 0.1, "mm", lo=0.01, hi=2, fmt="0.00",
            source="drawing, ISO 1101")
    s.input("in_gt_perp", "Perpendicularity of the flange face to A", "t_⊥", 0.05, "mm", lo=0.005, hi=1, fmt="0.00",
            source="drawing, ISO 1101")
    s.input("in_gt_run", "Circular run-out of the hub to A", "t_↗", 0.03, "mm", lo=0.005, hi=1, fmt="0.00",
            source="drawing, ISO 1101")
    s.input("in_m_max", "Maximum mass", "m_max", 1.0, "kg", lo=0.01, hi=100, fmt="0.00")

    s.section("Constants")
    s.const("c_EI", "Lower deviation of an H hole", "EI", 0, "µm", source="ISO 286-1, H: EI = 0", fmt="0")
    s.const("c_ke", "Minimum edge distance / ligament factor", "k_e", 1.0, "–",
            source="design rule e ≥ k_e·d_h (check company standard)")
    s.const("c_pw", "Drawing area width", "W", 200, "mm", source="drawing layout (A4 landscape, ISO 5457)", fmt="0")
    s.const("c_ph", "Drawing area height", "H", 150, "mm", source="drawing layout (A4 landscape, ISO 5457)", fmt="0")
    s.const("c_off", "Dimension line spacing", "a", 8, "mm", source="ISO 129-1 (drawing convention)", fmt="0")
    s.const("c_hatch", "Hatch line spacing", "s_h", 2.5, "mm", source="ISO 128-50", fmt="0.0")
    s.const("c_ov", "Centre line overshoot", "e_cl", 3, "mm", source="ISO 128-24", fmt="0")

    s.section("Fit H7 / shaft field (ISO 286)")
    s.equation(r"s_{max}=ES-ei\qquad s_{min}=EI-es")
    s.condition("chk_d_rng", "Bore within the ISO 286 table", "in_dbore<=MAX(db_iso286_key)",
                ok="in table", fail="outside table — extend 90_Database", text="d ≤ 180 mm", source="ISO 286-2")
    s.calc("calc_IT7", "Standard tolerance IT7", "IT7", interval_lookup("db_iso286_IT7", "db_iso286_key", "in_dbore"),
           "µm", text="size range of d", source="ISO 286-1, Tab. 1", fmt="0")
    s.calc("calc_IT6", "Standard tolerance IT6", "IT6", interval_lookup("db_iso286_IT6", "db_iso286_key", "in_dbore"),
           "µm", text="size range of d", source="ISO 286-1, Tab. 1", fmt="0")
    s.calc("calc_ES_hole", "Upper deviation of the bore H7", "ES", "c_EI+calc_IT7", "µm", text="ES = EI + IT7", fmt="0")
    s.calc("calc_fd", "Fundamental deviation of the shaft", "FD",
           interval_lookup(f"CHOOSE({index_match('fit', 'col', 'in_fit')},db_iso286_f,db_iso286_g,db_iso286_h,"
                           "db_iso286_k,db_iso286_p)", "db_iso286_key", "in_dbore"),
           "µm", text="table column of the field", source="ISO 286-2", fmt="0")
    s.calc("calc_side", "Deviation given by the table (1 = es, 2 = ei)", "", index_match("fit", "side", "in_fit"),
           "–", source="ISO 286-1, 4.3", fmt="0", aux=True)
    s.calc("calc_es_shaft", "Upper deviation of the shaft", "es", "IF(calc_side=1,calc_fd,calc_fd+calc_IT6)", "µm",
           text="es = FD, or ei + IT6", fmt="0")
    s.calc("calc_ei_shaft", "Lower deviation of the shaft", "ei", "calc_es_shaft-calc_IT6", "µm", text="ei = es − IT6", fmt="0")
    s.calc("out_cl_max", "Maximum clearance", "s_max", "calc_ES_hole-calc_ei_shaft", "µm", text="ES − ei", fmt="0")
    s.calc("out_cl_min", "Minimum clearance (negative = interference)", "s_min", "c_EI-calc_es_shaft", "µm",
           text="EI − es", fmt="0")
    s.remark("Fit type", 'IF(out_cl_min>=0,"clearance fit",IF(out_cl_max<=0,"interference fit","transition fit"))'
             '&" H7/"&in_fit')
    s.condition("chk_clmin", "Minimum clearance meets the requirement", "out_cl_min>=in_cl_min",
                ok="minimum clearance met", fail="clearance below requirement", text="s_min ≥ s_min,req")
    s.check("chk_clmax", "Maximum clearance", "η_s", "MAX(out_cl_max,0)", "in_cl_max", "µm", dec=0,
            source="requirement")
    s.calc("calc_dmax", "Bore upper limit", "d_max", "in_dbore+calc_ES_hole/1000", "mm", text="d + ES", fmt="0.000")
    s.calc("calc_dmin", "Bore lower limit", "d_min", "in_dbore+c_EI/1000", "mm", text="d + EI", fmt="0.000")

    s.section("General tolerances (ISO 2768-1)")
    s.calc("calc_gcol", "Column of the class", "", index_match("gencls", "col", "in_gen"), "–", fmt="0", aux=True)
    s.condition("chk_gen_rng", "Sizes within ISO 2768-1 (0.5 … 1000 mm)",
                "AND(in_t>=0.5,MAX(in_D,in_A1)<=MAX(db_gen_key))",
                ok="in table", fail="size outside ISO 2768-1", text="0.5 mm ≤ size ≤ 1000 mm", source="ISO 2768-1")
    for key, label, x in (("D", "outer diameter D", "in_D"), ("t", "thickness t", "in_t"),
                          ("Dh", "hub diameter D_h", "in_Dh"), ("Lh", "hub length L_h", "in_Lh"),
                          ("Dk", "bolt circle D_k", "in_Dk")):
        s.calc(f"calc_T_{key}", f"Deviation ± of {label}", f"T_{key}", gen_tol(x), "mm",
               text="size range × class", source="ISO 2768-1, Tab. 1", fmt="0.00")

    s.section("Tolerance chain — axial gap")
    s.equation(r"s=A_1-t-L_h\qquad T_{wc}=\sum T_i\qquad T_{rss}=\sqrt{\sum T_i^2}")
    s.calc("calc_s0", "Nominal gap", "s_0", "in_A1-in_t-in_Lh", "mm", text="s = A₁ − t − L_h", fmt="0.00")
    s.calc("calc_Twc", "Worst-case tolerance", "T_wc", "in_TA1+calc_T_t+calc_T_Lh", "mm", text="ΣT_i", fmt="0.00")
    s.calc("calc_Trss", "Statistical tolerance (RSS)", "T_rss", "SQRT(in_TA1^2+calc_T_t^2+calc_T_Lh^2)", "mm",
           text="√ΣT_i²", fmt="0.000")
    s.calc("out_s_min", "Minimum gap (worst case)", "s_min", "calc_s0-calc_Twc", "mm", text="s₀ − T_wc", fmt="0.00")
    s.calc("out_s_max", "Maximum gap (worst case)", "s_max", "calc_s0+calc_Twc", "mm", text="s₀ + T_wc", fmt="0.00")
    s.check("chk_smin", "Minimum axial gap", "η_s,min", "MAX(out_s_min,1e-6)", "in_s_min", "mm", kind="ge",
            source="requirement")
    s.check("chk_smax", "Maximum axial gap", "η_s,max", "out_s_max", "in_s_max", "mm", source="requirement")
    s.remark("Statistical gap", '"RSS: "&FIXED(calc_s0-calc_Trss,2)&" … "&FIXED(calc_s0+calc_Trss,2)'
             '&" mm — only for series production with normally distributed sizes"')

    s.section("Hole pattern and walls")
    s.condition("chk_geo", "Geometry consistent", "AND(in_D>in_Dk+in_dhole,in_Dk-in_dhole>in_Dh,in_Dh>in_dbore,"
                "2*in_c<in_Dh-in_dbore)", ok="consistent", fail="holes cut the hub or the rim",
                text="D > D_k + d_h > … > D_h > d")
    s.calc("calc_e", "Edge distance of the holes", "e", "(in_D-in_Dk)/2-in_dhole/2", "mm",
           text="e = (D − D_k)/2 − d_h/2", fmt="0.0")
    s.check("chk_edge", "Edge distance", "η_e", "MAX(calc_e,1e-6)", "c_ke*in_dhole", "mm", kind="ge", dec=1,
            source="design rule")
    s.calc("calc_a", "Hole axis to hub surface", "a", "(in_Dk-in_Dh)/2", "mm", text="a = (D_k − D_h)/2", fmt="0.0")
    s.check("chk_washer", "Room for the washer", "η_a", "MAX(calc_a,1e-6)", "in_dw/2", "mm", kind="ge", dec=1,
            source="a ≥ d_w/2")
    s.calc("calc_p", "Ligament between holes", "p", "PI()*in_Dk/in_n-in_dhole", "mm", text="p = π D_k / n − d_h",
           fmt="0.0")
    s.check("chk_pitch", "Ligament between holes", "η_p", "MAX(calc_p,1e-6)", "c_ke*in_dhole", "mm", kind="ge", dec=1,
            source="design rule")
    s.calc("calc_tw", "Hub wall (at maximum bore)", "t_w", "(in_Dh-calc_dmax)/2", "mm", text="(D_h − d_max)/2",
           fmt="0.00")
    s.check("chk_wall", "Hub wall", "η_w", "MAX(calc_tw,1e-6)", "in_tw_min", "mm", kind="ge", source="requirement")
    s.check("chk_pos", "Position tolerance vs. hole clearance", "η_pos", "in_gt_pos", "MAX(in_dhole-in_dbolt,1e-6)", "mm",
            source="floating fastener T = H − F (ISO 2692)")

    s.section("Mass")
    s.calc("calc_V", "Volume (chamfer neglected)", "V",
           "PI()/4*((in_D^2-in_dbore^2)*in_t+(in_Dh^2-in_dbore^2)*in_Lh-in_n*in_dhole^2*in_t)", "mm³",
           text="π/4 [(D² − d²)t + (D_h² − d²)L_h − n d_h² t]", fmt="0")
    s.calc("calc_rho", "Density", "ρ", index_match("mat", "rho", "in_mat"), "kg/m³", source="90_Database", fmt="0")
    s.calc("out_m", "Mass", "m", "calc_rho*calc_V*1e-9", "kg", text="m = ρ V (1e-9: mm³ → m³)", fmt="0.000")
    s.check("chk_m", "Mass", "η_m", "out_m", "in_m_max", "kg", dec=3, source="requirement")

    s.section("Drawing scale")
    s.calc("calc_sc_need", "Largest scale that fits", "M_req",
           "MIN((c_pw-6*c_off)/(calc_L+in_D),(c_ph-4*c_off)/in_D)", "–",
           text="min[(W − 6a)/(L + D) ; (H − 4a)/D]", fmt="0.00", aux=True)
    s.condition("chk_scale", "A standard scale fits the drawing area", "calc_sc_need>=MIN(db_scale_f)",
                ok="scale found", fail="part too large for 1:10", source="ISO 5455")
    match = "MATCH(MAX(calc_sc_need,MIN(db_scale_f)),db_scale_f,1)"
    s.calc("calc_sc", "Drawing scale factor", "M", f"INDEX(db_scale_f,{match})", "–",
           text="largest standard scale ≤ M_req", source="ISO 5455", fmt="0.0")
    s.calc("out_scale", "Drawing scale", "", f"INDEX(db_scale_key,{match})", "", source="ISO 5455", fmt="General")
    s.calc("calc_ox", "Section view origin x", "x_0", "(c_pw-(calc_L+in_D)*calc_sc-6*c_off)/2+2*c_off", "mm",
           text="centres both views; 6a = dimension space", fmt="0.0", aux=True)
    s.calc("calc_fx", "Front view centre x", "x_F", "calc_ox+calc_L*calc_sc+4*c_off+in_D/2*calc_sc", "mm",
           text="x₀ + L·M + 4a + D·M/2", fmt="0.0", aux=True)

    s.section("Result")
    s.result("out_eta", "Maximum utilisation", "η_max",
             "MAX(chk_clmax,chk_smin,chk_smax,chk_edge,chk_washer,chk_pitch,chk_wall,chk_pos,chk_m)", "–", fmt="0.00")
    s.close()

    # -- drawing data ---------------------------------------------------------------------- #
    gd = book.data_sheet(DATA, "Drawing coordinates", "Section A–A, hatching, dimensions and front view in paper mm")
    rk_in, rk_out = "(in_Dk-in_dhole)/2", "(in_Dk+in_dhole)/2"
    xy = [Col("x", "x [mm]", "0.00"), Col("y", "y [mm]", "0.00")]

    def poly(name: str, pts: list[tuple[str, str]], sign: str = "") -> object:
        return gd.block(name, xy, [(f"={X(x)}", f"={sign}{Y(y)}") for x, y in pts],
                        note="Outline in model mm → paper mm: x₀ + x·M, y·M")

    main = [("0", "in_dbore/2"), ("0", rk_in), ("in_t", rk_in), ("in_t", "in_Dh/2"), ("calc_L-in_c", "in_Dh/2"),
            ("calc_L", "in_Dh/2-in_c"), ("calc_L", "in_dbore/2"), ("0", "in_dbore/2")]
    ring = [("0", rk_out), ("0", "in_D/2"), ("in_t", "in_D/2"), ("in_t", rk_out), ("0", rk_out)]
    outlines = [poly("um", main), poly("ur", ring), poly("lm", main, "-"), poly("lr", ring, "-")]

    # hatch: the hub strip and the rim are split into rectangles; each one's moves run along visible edges
    hx = "c_hatch"
    hatches = [
        gd.hatch("h_hub_u", X("0"), X("calc_L"), Y("in_dbore/2"), Y("in_Dh/2"), spacing=hx, side="lower"),
        gd.hatch("h_web_u", X("0"), X("in_t"), Y("in_Dh/2"), Y(rk_in), spacing=hx, side="upper"),
        gd.hatch("h_rim_u", X("0"), X("in_t"), Y(rk_out), Y("in_D/2"), spacing=hx, side="lower"),
        gd.hatch("h_hub_l", X("0"), X("calc_L"), f"-{Y('in_Dh/2')}", f"-{Y('in_dbore/2')}", spacing=hx, side="upper"),
        gd.hatch("h_web_l", X("0"), X("in_t"), f"-{Y(rk_in)}", f"-{Y('in_Dh/2')}", spacing=hx, side="lower"),
        gd.hatch("h_rim_l", X("0"), X("in_t"), f"-{Y('in_D/2')}", f"-{Y(rk_out)}", spacing=hx, side="upper"),
    ]

    # dimension texts (series names shown as data labels)
    lbl_first = gd.r + 3
    labels = [
        ("od", '="Ø"&FIXED(in_D,0)&" ±"&FIXED(calc_T_D,1)'),
        ("bc", '="Ø"&FIXED(in_Dk,0)&"   "&in_n&"× Ø"&FIXED(in_dhole,0)'),
        ("hub", '="Ø"&FIXED(in_Dh,0)&" ±"&FIXED(calc_T_Dh,1)'),
        ("bore", f'="Ø"&FIXED(in_dbore,0)&" H7 ("&{tol_text("calc_ES_hole/1000", "c_EI/1000", 3)}&")   A"'),
        ("thk", '=FIXED(in_t,0)&" ±"&FIXED(calc_T_t,1)'),
        ("hublen", '=FIXED(in_Lh,0)&" ±"&FIXED(calc_T_Lh,1)'),
        ("len", '="("&FIXED(calc_L,0)&")"'),
        ("sec", '="SECTION A–A   "&out_scale'),
        ("fv", '="VIEW B"'),
    ]
    gd.block("lbl", [Col("txt", "text", "@"), Col("key", "dimension", "@")], [(f, k) for k, f in labels],
             note="Dimension texts linked to the calculation; (L) = reference dimension")
    ref = {k: f"'{DATA}'!$B${lbl_first + i}" for i, (k, _) in enumerate(labels)}

    items: list[DrawSeries] = [DrawSeries(b, "x", "y", "outline") for b in outlines]
    items += [DrawSeries(b, "x", "y", "hatch") for b in hatches]

    def vdim(key: str, x_dim: str, y_half: str, x_edge: str, pos: str = "l") -> None:
        """Vertical diameter dimension at paper x `x_dim`, extension lines from model x `x_edge`."""
        ext = gd.block(f"ext_{key}", xy, [(f"={X(x_edge)}", f"={Y(y_half)}"), (f"={x_dim}", f"={Y(y_half)}"),
                                          (f"={x_dim}", f"=-{Y(y_half)}"), (f"={X(x_edge)}", f"=-{Y(y_half)}")],
                       note="Extension lines")
        dim = gd.block(f"dim_{key}", xy, [(f"={x_dim}", f"=-{Y(y_half)}"), (f"={x_dim}", "=0"),
                                          (f"={x_dim}", f"={Y(y_half)}")], note="Dimension line")
        items.extend([DrawSeries(ext, "x", "y", "ext"),
                      DrawSeries(dim, "x", "y", "dim", label=ref[key], label_pos=pos, vertical=True)])

    def hdim(key: str, y_dim: str, xa: str, ya: str, xb: str, yb: str, pos: str = "t") -> None:
        """Horizontal length dimension at paper y `y_dim` between model points (xa, ya) and (xb, yb)."""
        ext = gd.block(f"ext_{key}", xy, [(f"={X(xa)}", f"={ya}"), (f"={X(xa)}", f"={y_dim}"),
                                          (f"={X(xb)}", f"={y_dim}"), (f"={X(xb)}", f"={yb}")],
                       note="Extension lines")
        dim = gd.block(f"dim_{key}", xy, [(f"={X(xa)}", f"={y_dim}"), (f"=({X(xa)}+{X(xb)})/2", f"={y_dim}"),
                                          (f"={X(xb)}", f"={y_dim}")], note="Dimension line")
        items.extend([DrawSeries(ext, "x", "y", "ext"), DrawSeries(dim, "x", "y", "dim", label=ref[key], label_pos=pos)])

    vdim("od", f"{X('0')}-2*c_off", "in_D/2", "0")
    vdim("bc", f"{X('0')}-c_off", "in_Dk/2", "0")
    vdim("hub", f"{X('calc_L')}+2*c_off", "in_Dh/2", "calc_L-in_c", pos="r")
    vdim("bore", f"{X('calc_L')}+c_off", "in_dbore/2", "calc_L", pos="r")
    hdim("thk", f"{Y('in_D/2')}+c_off", "0", Y("in_D/2"), "in_t", Y("in_D/2"))
    hdim("hublen", f"{Y('in_Dh/2')}+c_off", "in_t", Y("in_Dh/2"), "calc_L", Y("in_Dh/2-in_c"))
    hdim("len", f"-{Y('in_D/2')}-c_off", "0", f"-{Y('in_D/2')}", "calc_L", f"-{Y('in_Dh/2-in_c')}", pos="b")

    # centre lines of the section: part axis and hole axes
    for key, y in (("axis", "0"), ("hole_u", Y("in_Dk/2")), ("hole_l", f"-{Y('in_Dk/2')}")):
        x_end = "calc_L" if key == "axis" else "in_t"
        b = gd.block(f"cl_{key}", xy, [(f"={X('0')}-c_ov", f"={y}"), (f"={X(x_end)}+c_ov", f"={y}")],
                     note="Centre line, overshoot e_cl")
        items.append(DrawSeries(b, "x", "y", "axis"))

    # front view (view B): circles, bolt circle, holes, centre cross
    n_seg = 72
    circ_first = gd.r + 3
    circ_rows = []
    for i in range(n_seg + 1):
        r = circ_first + i
        a = f"B{r}"
        row: list[object] = [i * 2 * 3.141592653589793 / n_seg]
        for dia in ("in_D", "in_Dh", "in_dbore", "in_Dk"):
            row += [f"=calc_fx+{dia}/2*calc_sc*COS({a})", f"={dia}/2*calc_sc*SIN({a})"]
        circ_rows.append(tuple(row))
    circ = gd.block("fv", [Col("a", "angle [rad]", "0.000")] + [
        Col(f"{p}{k}", f"{p}{k}", "0.00") for k in ("od", "hub", "bore", "bc") for p in ("x", "y")], circ_rows,
        note=f"Front view circles, {n_seg} segments; x_F + r·M·cos a, r·M·sin a")
    items += [DrawSeries(circ, f"x{k}", f"y{k}", "outline") for k in ("od", "hub", "bore")]
    items.append(DrawSeries(circ, "xbc", "ybc", "axis"))

    hc_first = gd.r + 3
    hc_rows = []
    for i in range(1, 13):
        r = hc_first + i - 1
        hc_rows.append((i, f"=IF(B{r}<=in_n,1,0)",
                        f"=calc_fx+IF(C{r}=1,in_Dk/2*calc_sc*COS(PI()/2+2*PI()*(B{r}-1)/in_n),0)",
                        f"=IF(C{r}=1,in_Dk/2*calc_sc*SIN(PI()/2+2*PI()*(B{r}-1)/in_n),0)",
                        f"=IF(C{r}=1,in_dhole/2*calc_sc,0)"))
    gd.block("hc", [Col("i", "hole", "0"), Col("on", "active", "0"), Col("cx", "x centre", "0.00"),
                    Col("cy", "y centre", "0.00"), Col("r", "radius", "0.00")], hc_rows,
             note="Hole centres from 90° (cutting plane A–A); inactive holes collapse to the view centre")
    hole_first = gd.r + 3
    hole_rows = []
    for i in range(n_seg + 1):
        r = hole_first + i
        row = [i * 2 * 3.141592653589793 / n_seg]
        for h in range(12):
            hr = hc_first + h
            row += [f"=D{hr}+F{hr}*COS(B{r})", f"=E{hr}+F{hr}*SIN(B{r})"]
        hole_rows.append(tuple(row))
    holes = gd.block("holes", [Col("a", "angle [rad]", "0.000")] + [
        Col(f"{p}{h}", f"{p}{h}", "0.00") for h in range(1, 13) for p in ("x", "y")], hole_rows,
        note="Bolt holes: centre + r·cos a, r·sin a")
    items += [DrawSeries(holes, f"x{h}", f"y{h}", "outline") for h in range(1, 13)]
    cross = gd.block("cl_fv", [Col("xh", "x", "0.00"), Col("yh", "y", "0.00"), Col("xv", "x", "0.00"),
                               Col("yv", "y", "0.00")],
                     [("=calc_fx-in_D/2*calc_sc-c_ov", "=0", "=calc_fx", "=-in_D/2*calc_sc-c_ov"),
                      ("=calc_fx+in_D/2*calc_sc+c_ov", "=0", "=calc_fx", "=in_D/2*calc_sc+c_ov")],
                     note="Centre cross of the front view")
    items += [DrawSeries(cross, "xh", "yh", "axis"), DrawSeries(cross, "xv", "yv", "axis")]

    titles = gd.block("titles", [Col("x", "x", "0.00"), Col("y", "y", "0.00"), Col("x2", "x", "0.00")],
                      [(f"=({X('0')}+{X('calc_L')})/2", "=c_ph/2-c_off/4", "=calc_fx")],
                      note="Anchor points of the view titles")
    items += [DrawSeries(titles, "x", "y", "thin", label=ref["sec"], label_at=0, label_pos="b"),
              DrawSeries(titles, "x2", "y", "thin", label=ref["fv"], label_at=0, label_pos="b")]
    gd.close()

    x_range, y_range = (0.0, 200.0), (-75.0, 75.0)  # = c_pw × c_ph

    # -- drawing sheet --------------------------------------------------------------------- #
    dw = book.drawing_sheet("20_Drawing", "Drawing", "Section A–A and view B, GD&T, title block")
    dw.chart(drawing_chart(items, x_range=x_range, y_range=y_range, width_cm=24.0), "B8")
    r = 45
    dw.ws.cell(r, 2, "GEOMETRICAL TOLERANCES (ISO 1101) — datum A = bore axis").style = "ec_h2"
    for col in range(3, 10):
        dw.ws.cell(r, col).style = "ec_h2"
    dw.gdt_frame(r + 2, 3, "⊥", "=FIXED(in_gt_perp,2)", "A", "left flange face")
    dw.gdt_frame(r + 3, 3, "↗", "=FIXED(in_gt_run,2)", "A", "hub diameter D_h")
    dw.gdt_frame(r + 4, 3, "⌖", '="Ø"&FIXED(in_gt_pos,2)', "A", 'hole pattern on the bolt circle')
    date = '=YEAR(meta_date)&"-"&RIGHT("0"&MONTH(meta_date),2)&"-"&RIGHT("0"&DAY(meta_date),2)'
    end = dw.title_block(r + 7, 2, [
        ("Part", "Flange"), ("Drawing no.", "ECW-FL-001"), ("Material", '=in_mat&""'), ("Scale", '=out_scale&""'),
        ("General tolerances", '="ISO 2768-"&in_gen&"K"'), ("Edges", "ISO 13715"),
        ("Projection", "ISO 5456-2, method E"), ("Mass", '=FIXED(out_m,2)&" kg"'),
        ("Drawn", '=meta_author&""'), ("Checked", '=meta_checker&""'), ("Date", date), ("Revision", '=meta_rev&""'),
    ])
    dw.close(end)

    # -- overview -------------------------------------------------------------------------- #
    d = book.dashboard("01_Overview", "Overview", "Key results, drawing, check utilisation")
    d.kpis([
        ("Fit", '="Ø"&FIXED(in_dbore,0)&" H7/"&in_fit', "", "@"),
        ("Clearance min … max", '=FIXED(out_cl_min,0)&" … "&FIXED(out_cl_max,0)', "µm", "@"),
        ("Axial gap min … max", '=FIXED(out_s_min,2)&" … "&FIXED(out_s_max,2)', "mm", "@"),
        ("Utilisation η max", "=out_eta", "–", "0.00"),
    ])
    d.chart(drawing_chart(items, x_range=x_range, y_range=y_range, width_cm=18.0), "B13")
    d.utilization_chart("B41", width=18.0, height=7.0)
    d.close(56)

    book.readme(
        purpose="Check of a hub flange: bore fit H7 against the selected shaft field, general tolerances, "
                "axial tolerance chain in the housing, hole pattern and wall checks, mass; with a live "
                "drawing that follows every input.",
        scope=["Rotationally symmetric flange with a cylindrical hub and n through holes on one bolt circle",
               "Bore 3 … 180 mm (ISO 286 excerpt), shaft fields f6, g6, h6, k6, p6 against H7",
               "General tolerances ISO 2768-1 f / m / c for sizes 0.5 … 1000 mm",
               "Static geometry checks only — no strength check of the bolts or the flange"],
        assumptions=["Tolerance chain: housing depth A₁ minus flange thickness t minus hub length L_h",
                     "RSS result valid only for series production with normally distributed sizes",
                     "Hub chamfer neglected in the volume; bore chamfers not drawn",
                     "Section A–A runs through two hole axes; for odd n the lower hole is rotated into the "
                     "cutting plane (ISO 128-44 convention)",
                     "Tolerance tables are excerpts — verify against the current standards before release"],
        workflow=["Fill the yellow cells on 10_Flange (dropdowns for material, shaft field, tolerance class)",
                  "Read the banner: ALL CHECKS SATISFIED / FAILS",
                  "Check the drawing on 20_Drawing — dimensions, scale and title block update automatically",
                  "Details of every check in 80_Checks, overview in 01_Overview"],
        sources=["ISO 286-1/-2:2010 Geometrical product specifications — ISO code system for tolerances",
                 "ISO 2768-1:1989 General tolerances", "ISO 1101:2017 Geometrical tolerancing",
                 "ISO 128 Technical product documentation — presentation", "ISO 5455 Scales, ISO 7200 Title blocks"],
        revisions=[("2026-10-25", "A", "First issue (skill reference build)", "A. Engineer", "")],
    )
    return book.save(out)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("flange_check_v1.0.xlsx")
    print(build(target))
