"""Reference build — template T1 "design-office sheet" (TCC / RCC spreadsheet style, layout K).

Two-pile cap, truss method (EN 1992-1-1). The look follows the TCC / RCC design spreadsheets:
job box, STATUS top right, red section headings, blue underlined inputs two blocks per row,
live plan view, checks with relations, assumptions a) b) …, OPERATING INSTRUCTIONS and input
messages right of the page. Inputs on 10_Main, every step traceable on 11_Details.

    python example_pile_cap.py out/pile_cap.xlsx
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engcalc import Col, DrawSeries, EngWorkbook, Meta, drawing_chart  # noqa: E402

INPUTS_DIM = [  # key, label, symbol, value, unit, lo, hi, fmt
    ("in_s", "Pile spacing", "s", 1800, "mm", 900, 3600, "0"),
    ("in_dp", "Pile diameter", "φ_p", 600, "mm", 300, 1200, "0"),
    ("in_e", "Edge distance", "e", 150, "mm", 100, 500, "0"),
    ("in_h", "Cap depth", "h", 900, "mm", 400, 2500, "0"),
    ("in_c", "Cover to tie", "c", 75, "mm", 40, 100, "0"),
    ("in_a", "Column width", "a", 400, "mm", 200, 1000, "0"),
]
INPUTS_LOAD = [
    ("in_NEd", "Column load", "N_Ed", 1500, "kN", 0, 20000, "0"),
    ("in_PRd", "Pile resistance", "P_Rd", 1000, "kN", 100, 10000, "0"),
    ("in_fck", "Concrete", "f_ck", 30, "MPa", 20, 50, "0"),
    ("in_fyk", "Steel", "f_yk", 500, "MPa", 400, 600, "0"),
    ("in_fb", "Bar diameter", "φ", 25, "mm", 12, 40, "0"),
    ("in_nb", "Tie bars", "n", 5, "–", 2, 20, "0"),
]


def build(out: Path) -> Path:
    book = EngWorkbook(Meta(
        project="Reference project – warehouse extension", client="Reference client",
        title="Two-pile cap – truss method", subject="Grid A/1, column C1",
        author="A. Engineer", checker="", revision="A", date=dt.date(2026, 11, 9), job_no="R-001",
        organisation="eng-calc-workbook", standard="EN 1992-1-1, EN 1990", domain="civil",
    ))

    # -- 10_Main: the sheet the engineer works on (inputs) ----------------------------- #
    fm = book.form_sheet("10_Main", "Two-pile cap design", "Design sheet (style K): inputs, plan view, status, checks",
                         instructions=["Piles in one line, column centred.", "Steps and sources: sheet 11_Details."])
    fm.section("Dimensions", unit="mm", at="left")
    for key, label, sym, v, unit, lo, hi, fmt in INPUTS_DIM:
        fm.input(key, label, sym, v, unit, lo=lo, hi=hi, fmt=fmt, at="left")
    fm.section("Loads and materials", at="mid")
    for key, label, sym, v, unit, lo, hi, fmt in INPUTS_LOAD:
        fm.input(key, label, sym, v, unit, lo=lo, hi=hi, fmt=fmt, at="mid")

    # -- 11_Details: calc pad, every step with its relation and source ------------------ #
    s = book.calc_sheet("11_Details", "Pile cap – calculation details", "All steps of the truss method with sources")
    s.section("Input data (from 10_Main)")
    for key, label, sym, _, unit, *_rest in INPUTS_DIM + INPUTS_LOAD:
        s.calc(None, label, sym, key, unit, fmt="0", source="10_Main")
    s.section("Constants")
    s.const("c_gc", "Unit weight of reinforced concrete", "γ_c", 25, "kN/m³", source="EN 1991-1-1, Tab. A.1", fmt="0")
    s.const("c_gG", "Partial factor, permanent actions", "γ_G", 1.35, "–", source="EN 1990, Tab. A1.2(B)")
    s.const("c_gS", "Partial factor, reinforcement", "γ_S", 1.15, "–", source="EN 1992-1-1, Tab. 2.1N")
    s.section("Geometry")
    s.calc("calc_d", "Effective depth", "d", "in_h-in_c-in_fb/2", "mm", text="d = h − c − φ/2", fmt="0.0")
    s.calc("calc_Lc", "Cap length", "L", "in_s+in_dp+2*in_e", "mm", text="L = s + φ_p + 2e", fmt="0")
    s.calc("calc_Bc", "Cap width", "B", "in_dp+2*in_e", "mm", text="B = φ_p + 2e", fmt="0")
    s.section("Actions")
    s.calc("calc_Gk", "Self-weight of the cap", "G_k", "c_gc*calc_Lc*calc_Bc*in_h/1E9", "kN", text="G_k = γ_c·L·B·h / 1E9 (mm³ → m³)", fmt="0.0")
    s.result("out_PEd", "Design load per pile", "P_Ed", "in_NEd/2+c_gG*calc_Gk/2", "kN", text="P_Ed = N_Ed/2 + γ_G·G_k/2", fmt="0.0")
    s.section("Tie")
    s.calc("calc_T", "Tie force (truss)", "T", "out_PEd*(in_s/2)/calc_d", "kN", text="T = P_Ed·(s/2)/d",
           source="TCC How to: Foundations, truss", fmt="0.0")
    s.calc("calc_fyd", "Design yield strength", "f_yd", "in_fyk/c_gS", "MPa", text="f_yd = f_yk/γ_S", fmt="0.0")
    s.calc("calc_Asreq", "Required tie area", "A_s,req", "calc_T*1000/calc_fyd", "mm²", text="A_s,req = T/f_yd", fmt="0")
    s.result("out_Asprov", "Provided tie area", "A_s,prov", "in_nb*PI()*in_fb^2/4", "mm²", text="A_s = n·π·φ²/4", fmt="0")
    s.calc("calc_fctm", "Mean tensile strength", "f_ctm", "0.30*in_fck^(2/3)", "MPa", text="f_ctm = 0.30·f_ck^(2/3)",
           source="EN 1992-1-1, Tab. 3.1", fmt="0.00")
    s.calc("calc_Asmin", "Minimum reinforcement", "A_s,min", "MAX(0.26*calc_fctm/in_fyk,0.0013)*calc_Bc*calc_d", "mm²",
           text="max(0.26·f_ctm/f_yk ; 0.0013)·B·d", source="EN 1992-1-1, 9.2.1.1(1)", fmt="0")
    s.calc("calc_lb", "Tie bar length", "l_b", "calc_Lc-2*in_c", "mm", text="l_b = L − 2c (straight bar)", fmt="0")
    s.const("c_rhos", "Density of reinforcing steel", "ρ_s", 7850, "kg/m³", source="EN 1992-1-1, 3.2.7(3)", fmt="0")
    s.calc("calc_mass", "Mass of the tie", "m", "in_nb*calc_lb*PI()*in_fb^2/4*c_rhos/1E9", "kg",
           text="m = n·l_b·π·φ²/4·ρ_s / 1E9 (mm³ → m³)", fmt="0.0")
    s.section("Checks")
    s.check("chk_pile", "Pile load", "P_Ed / P_Rd", "out_PEd", "in_PRd", "kN", dec=0, source="geotechnical report")
    s.check("chk_tie", "Tie reinforcement", "A_s,req / A_s,prov", "calc_Asreq", "out_Asprov", "mm²", dec=0,
            source="EN 1992-1-1, 6.5.4")
    s.check("chk_min", "Minimum reinforcement", "A_s,min / A_s,prov", "calc_Asmin", "out_Asprov", "mm²", dec=0,
            source="EN 1992-1-1, 9.2.1.1")
    s.condition("chk_truss", "Truss method applicable (s ≤ 3φ_p)", "in_s<=3*in_dp", ok="s ≤ 3φ_p",
                fail="s > 3φ_p – use bending theory", text="s ≤ 3·φ_p", source="TCC How to: Foundations")
    s.close()

    # -- plan view data ----------------------------------------------------------------- #
    gd = book.data_sheet("91_ChartData", "Plan view coordinates", "Cap outline, piles and column for the live plan view")
    rect = lambda name, hx, hy: gd.block(name, [Col("x", "x [mm]", "0"), Col("y", "y [mm]", "0")],  # noqa: E731
                                         [(f"={sx}*({hx})", f"={sy}*({hy})")
                                          for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))])
    cap = rect("cap", "calc_Lc/2", "calc_Bc/2")
    col = rect("col", "in_a/2", "in_a/2")
    first = gd.r + 3  # same pattern as example_flange: the angle is data in column B
    piles = gd.block("piles", [Col("a", "angle [°]", "0"), Col("x1", "x pile 1", "0"), Col("y", "y", "0"),
                               Col("x2", "x pile 2", "0")],
                     [(5 * k, f"=-in_s/2+in_dp/2*COS(RADIANS(B{first + k}))", f"=in_dp/2*SIN(RADIANS(B{first + k}))",
                       f"=in_s/2+in_dp/2*COS(RADIANS(B{first + k}))") for k in range(73)],
                     note="Pile circles, 72 segments: ±s/2 + φ_p/2·cos a, φ_p/2·sin a")
    axis = gd.block("axis", [Col("x", "x [mm]", "0"), Col("y", "y [mm]", "0")],
                    [("=-calc_Lc/2", 0), ("=calc_Lc/2", 0)])
    gd.close()
    plan = drawing_chart([DrawSeries(cap, "x", "y", "outline"), DrawSeries(piles, "x1", "y", "thin"),
                          DrawSeries(piles, "x2", "y", "thin"), DrawSeries(col, "x", "y", "outline"),
                          DrawSeries(axis, "x", "y", "axis")],
                         x_range=(-2100, 2100), y_range=(-900, 900), width_cm=12.5)

    # -- 10_Main: results, plan view, status, checks, assumptions ----------------------- #
    # three blocks per row, then a wide sketch beside the utilisation chart: the page has no empty corner
    fm.section("Results", at="right")
    fm.value("Effective depth", "d", "calc_d", "mm", fmt="0", at="right")
    fm.value("Load per pile", "P_Ed", "out_PEd", "kN", fmt="0", at="right")
    fm.value("Tie force", "T", "calc_T", "kN", fmt="0", at="right")
    fm.value("Required", "A_s,req", "calc_Asreq", "mm²", fmt="0", at="right")
    fm.value("Provided", "A_s,prov", "out_Asprov", "mm²", fmt="0", at="right", result=True)
    fm.section("Plan view", at="half")
    fm.chart(plan, at="half")
    fm.utilization_chart(at="right", width=6.4, height=5.4)
    fm.checks()
    fm.table([Col("mark", "Mark", "@"), Col("loc", "Location", "@"), Col("n", "n", "0"), Col("fb", "φ [mm]", "0"),
              Col("lb", "Length [mm]", "0"), Col("m", "Mass [kg]", "0.0")],
             [("01", "Tie, bottom", "=in_nb", "=in_fb", "=calc_lb", "=calc_mass")],
             spans=(2, 5, 2, 2, 2, 2), total={"m": "SUM"}, title="Reinforcement schedule")
    fm.notes(["Two piles in one line, column centred on the cap; pile loads equal.",
              "Truss method: tie force T = P_Ed·(s/2)/d, column width neglected (conservative).",
              "Shear, punching at the column and the piles and anchorage of the tie are not covered "
              "by this sheet — check them separately.",
              "Pile resistance P_Rd from the geotechnical report, ULS design value."], title="Assumptions")
    fm.close()

    book.readme(
        purpose="Template T1 (design-office sheet, TCC / RCC style): two-pile cap designed by the truss method.",
        scope=["Two piles in one line, centred column, axial load only",
               "Pile spacing ≤ 3 pile diameters (truss method), C20/25 – C50/60, B400 – B600"],
        assumptions=["Shear, punching and anchorage not checked on this sheet",
                     "Self-weight of the cap included, soil above the cap neglected"],
        workflow=["On 10_Main type into the blue underlined cells only",
                  "Read STATUS top right; a message right of the page names an input out of range",
                  "Every step with its relation and source is on 11_Details, the register in 80_Checks"],
        sources=["EN 1990 Basis of structural design", "EN 1991-1-1 Densities, self-weight",
                 "EN 1992-1-1 Design of concrete structures", "The Concrete Centre: How to design concrete "
                 "structures using Eurocode 2 — Foundations (truss method for pile caps)"],
        revisions=[("2026-11-09", "A", "First issue (template T1 reference build)", "A. Engineer", "")],
    )
    return book.save(out)


if __name__ == "__main__":
    print(build(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pile_cap_v1.0.xlsx")))
