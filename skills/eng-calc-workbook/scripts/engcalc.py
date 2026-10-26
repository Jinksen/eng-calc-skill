"""engcalc — openpyxl builder for engineering calculation workbooks.

One visual language for electrical / mechanical / civil calc sheets:
title block -> status banner -> inputs -> calculation steps -> limit checks
-> results, plus an auto-generated check register (80_Checks), README with
colour legend, named ranges for every quantity and print-ready A4 setup.

Requires: openpyxl>=3.1, Pillow; matplotlib only for equation()/figure().
"""
from __future__ import annotations

import datetime as dt
import io
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from itertools import accumulate
from typing import Literal, Sequence, Union

from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.chart.data_source import StrRef
from openpyxl.chart.label import DataLabel, DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.text import RichText
from openpyxl.drawing.line import LineEndProperties
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties, RichTextProperties
from openpyxl.drawing.image import Image as XLImage
from openpyxl.formatting.rule import DataBarRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, NamedStyle, PatternFill, Protection, Side
from openpyxl.utils import absolute_coordinate, get_column_letter, quote_sheetname
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.pagebreak import Break
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

Scalar = Union[int, float, str, dt.date, None]
Domain = Literal["electrical", "mechanical", "civil", "general"]
CheckKind = Literal["le", "ge"]
Place = Literal["left", "mid", "right", "wide", "full"]

# --------------------------------------------------------------------------- #
# Visual language (single source of truth — reference/visual-language.md)
# --------------------------------------------------------------------------- #


class C:
    """Colour tokens (hex RRGGBB)."""

    NAVY = "1F3864"
    BLUE = "2E75B6"
    BLUE_LT = "D9E1F2"
    BLUE_XLT = "F2F6FC"
    GRID = "BFBFBF"
    TEXT = "000000"
    MUTED = "7F7F7F"
    INPUT_FILL = "FFF2CC"
    INPUT_FONT = "0000FF"
    INPUT_BORDER = "8EA9DB"
    SELECT_FILL = "DDF4F7"
    CONST_FILL = "EDE4F5"
    CONST_FONT = "5B2C83"
    LINK_FONT = "00703C"
    RESULT_FILL = "FCE4D6"
    RESULT_EDGE = "C55A11"
    NOTE_FONT = "1F4E79"
    META_FILL = "F2F2F2"
    OK_FILL, OK_FONT = "C6EFCE", "006100"
    WARN_FILL, WARN_FONT = "FFEB9C", "9C5700"
    FAIL_FILL, FAIL_FONT = "FFC7CE", "9C0006"
    NA_FILL, NA_FONT = "EDEDED", "595959"
    SERIES = ("2E75B6", "C55A11", "548235", "7030A0", "BF8F00", "1F3864")


DOMAIN_ACCENT: dict[str, str] = {
    "electrical": "BF8F00",  # amber / copper
    "mechanical": "2F5597",  # steel blue
    "civil": "548235",  # structural green
    "general": "1F3864",
}

TAB = {
    "readme": "7F7F7F",
    "dashboard": C.NAVY,
    "calc": C.BLUE,
    "checks": "548235",
    "data": "7030A0",
    "report": "C55A11",
}

FONT = "Calibri"
OK, WARN, FAIL, NA = "✔", "▲", "✘", "–"

# Calc-sheet column grid: role -> (column index, width)
GRID: dict[str, tuple[int, float]] = {
    "margin": (1, 1.5),
    "id": (2, 5.0),
    "label": (3, 30.0),
    "sym": (4, 9.0),
    "val": (5, 12.0),
    "unit": (6, 8.0),
    "text": (7, 26.0),
    "src": (8, 18.0),
    "stat": (9, 22.0),
    "margin_r": (10, 1.5),
}
COL = {k: v[0] for k, v in GRID.items()}
LAST_COL = get_column_letter(COL["stat"])
HEADER_ROWS = 7  # title block 1-4, banner 5, instructions 6, column header 7

_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_CELLISH_RE = re.compile(r"^[A-Za-z]{1,3}\d+$|^[RrCc]$|^[RrCc]\d+$")
_SHEET_RE = re.compile(r"^\d{2}_[A-Za-z0-9_]+$")

# --------------------------------------------------------------------------- #
# Formula utilities
# --------------------------------------------------------------------------- #

_XLFN = (
    "XLOOKUP", "XMATCH", "IFS", "SWITCH", "MAXIFS", "MINIFS", "TEXTJOIN", "CONCAT",
    "IFNA", "SHEETS", "SHEET", "FORMULATEXT", "ISFORMULA", "XOR", "NUMBERVALUE",
    "CEILING.MATH", "FLOOR.MATH", "LET", "LAMBDA",
    # Excel 2010+ statistics (stored with _xlfn.)
    "FORECAST.LINEAR", "STDEV.S", "STDEV.P", "VAR.S", "VAR.P", "PERCENTILE.INC", "PERCENTILE.EXC",
    "QUARTILE.INC", "QUARTILE.EXC", "MODE.SNGL", "RANK.EQ", "NORM.DIST", "NORM.INV", "NORM.S.DIST",
    "NORM.S.INV", "LOGNORM.DIST", "LOGNORM.INV", "WEIBULL.DIST", "EXPON.DIST", "BINOM.DIST",
    "POISSON.DIST", "T.DIST", "T.INV", "T.INV.2T", "T.TEST", "F.TEST", "CHISQ.TEST", "CONFIDENCE.T",
    "CONFIDENCE.NORM", "COVARIANCE.S", "ERF.PRECISE", "ERFC.PRECISE", "GAMMALN.PRECISE", "GAMMA",
    "AGGREGATE",
    # Excel 2013+ engineering
    "IMCOSH", "IMCOT", "IMCSC", "IMCSCH", "IMSEC", "IMSECH", "IMSINH", "IMTAN",
    "BITAND", "BITOR", "BITXOR", "BITLSHIFT", "BITRSHIFT",
)
_DYNAMIC = ("FILTER", "SORT", "SORTBY", "UNIQUE", "SEQUENCE", "RANDARRAY")
_FUNC_RE = re.compile(r"(?<![\w.])(" + "|".join(re.escape(f) for f in _XLFN) + r")\s*\(", re.I)
_DYN_RE = re.compile(r"(?<![\w.])(" + "|".join(_DYNAMIC) + r")\s*\(", re.I)


def fx(formula: str) -> str:
    """Normalise a formula: leading '=', `_xlfn.` prefixes outside string literals.

    Raises ValueError for dynamic-array functions, which openpyxl writes as
    legacy array formulas (Excel then shows implicit intersection `@`).
    """
    body = formula[1:] if formula.startswith("=") else formula
    parts = body.split('"')
    for i in range(0, len(parts), 2):  # even segments are outside string literals
        if _DYN_RE.search(parts[i]):
            raise ValueError(f"dynamic-array function in {formula!r}: write it by hand in Excel")
        parts[i] = _FUNC_RE.sub(lambda m: f"_xlfn.{m.group(1).upper()}(", parts[i])
    return "=" + '"'.join(parts)


def let(bindings: dict[str, str], body: str) -> str:
    """LET with Excel's on-disk `_xlpm.` parameter prefix. Use `{var}` placeholders.

    Not evaluated by LibreOffice < 24.8 (verify.py then reports #NAME?).
    """
    def sub(s: str) -> str:
        return re.sub(r"\{(\w+)\}", lambda m: f"_xlpm.{m.group(1)}", s)

    args: list[str] = []
    for k, v in bindings.items():
        args += [f"_xlpm.{k}", sub(v)]
    return f"_xlfn.LET({','.join(args + [sub(body)])})"


def index_match(table: str, col: str, key_expr: str) -> str:
    """Lookup into a DataSheet table: INDEX/MATCH works in every Excel and LibreOffice."""
    return f"INDEX(db_{table}_{col},MATCH({key_expr},db_{table}_key,0))"


def interval_lookup(values: str, upper_bounds: str, x: str) -> str:
    """Value for the interval ⟨prev ; upper] containing x (ISO 286 / ISO 2768 size ranges).

    `upper_bounds` ascending; x exactly on a bound belongs to the lower interval, as in the
    standards. Works in every Excel and LibreOffice (no array formula).
    """
    return f'INDEX({values},COUNTIF({upper_bounds},"<"&{x})+1)'


def tol_text(upper: str, lower: str, dec: int = 2) -> str:
    """Tolerance text for a dimension label: '±0.10', '+0.021/0', '-0.007/-0.020'."""
    def signed(e: str) -> str:
        return f'IF({e}=0,"0",IF({e}>0,"+","")&FIXED({e},{dec}))'

    return (f'IF(ABS(({upper})+({lower}))<1e-6,"±"&FIXED({upper},{dec}),'
            f'{signed(upper)}&"/"&{signed(lower)})')


def _check_name(name: str) -> None:
    if not _NAME_RE.match(name) or _CELLISH_RE.match(name):
        raise ValueError(f"invalid defined name {name!r} (ASCII, no spaces, not cell-like)")


def _tokens(formula: str) -> set[str]:
    stripped = re.sub(r'"[^"]*"', "", formula)
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", stripped))


# --------------------------------------------------------------------------- #
# Styles
# --------------------------------------------------------------------------- #


def _side(color: str = C.GRID, style: str = "thin") -> Side:
    return Side(style=style, color=color)


def _box(color: str = C.GRID, style: str = "thin") -> Border:
    s = _side(color, style)
    return Border(left=s, right=s, top=s, bottom=s)


def _fill(color: str) -> PatternFill:
    return PatternFill("solid", fgColor=color)


def _font(color: str = C.TEXT, *, size: float = 10, bold: bool = False, italic: bool = False) -> Font:
    return Font(name=FONT, size=size, color=color, bold=bold, italic=italic)


def _style_defs() -> list[NamedStyle]:
    def ns(name: str, font: Font, *, fill: str | None = None, border: Border | None = None,
           h: str = "left", fmt: str = "General", locked: bool = True, wrap: bool = False) -> NamedStyle:
        st = NamedStyle(name=name)
        st.font = font
        if fill:
            st.fill = _fill(fill)
        if border:
            st.border = border
        st.alignment = Alignment(horizontal=h, vertical="center", wrap_text=wrap)
        st.number_format = fmt
        st.protection = Protection(locked=locked)
        return st

    bottom = Border(bottom=_side("D9D9D9"))
    return [
        ns("ec_input", _font(C.INPUT_FONT, bold=True), fill=C.INPUT_FILL, border=_box(C.INPUT_BORDER), h="right", locked=False),
        ns("ec_select", _font(C.INPUT_FONT, bold=True), fill=C.SELECT_FILL, border=_box(C.INPUT_BORDER), h="center", locked=False),
        ns("ec_const", _font(C.CONST_FONT), fill=C.CONST_FILL, border=_box("C9B8DB"), h="right"),
        ns("ec_calc", _font(), border=bottom, h="right"),
        ns("ec_link", _font(C.LINK_FONT), border=bottom, h="right"),
        ns("ec_aux", _font(C.MUTED, italic=True), border=bottom, h="right"),
        ns("ec_result", _font(size=11, bold=True), fill=C.RESULT_FILL, border=_box(C.RESULT_EDGE, "medium"), h="right"),
        ns("ec_label", _font(), border=bottom),
        ns("ec_symbol", _font(bold=True, italic=True), border=bottom, h="right"),
        ns("ec_unit", _font(C.MUTED), border=bottom),
        ns("ec_text", Font(name="Cambria Math", size=10, color="404040"), border=bottom),
        ns("ec_source", _font(C.MUTED, size=8, italic=True), border=bottom),
        ns("ec_status", _font(bold=True), border=bottom, h="center"),
        ns("ec_note", _font(C.NOTE_FONT, bold=True, italic=True)),
        ns("ec_comment", _font(C.MUTED, size=9, italic=True), wrap=False),
        ns("ec_h1", _font("FFFFFF", size=11, bold=True), fill=C.NAVY),
        ns("ec_h2", _font(C.NAVY, bold=True), fill=C.BLUE_LT, border=Border(bottom=_side(C.NAVY))),
        ns("ec_colhead", _font(C.NAVY, size=8, bold=True), fill=C.BLUE_XLT, border=Border(bottom=_side(C.NAVY, "medium")), h="center"),
        ns("ec_meta_label", _font(C.MUTED, size=7)),
        ns("ec_meta", _font(bold=True)),
        ns("ec_meta_input", _font(C.INPUT_FONT, bold=True), fill=C.INPUT_FILL, border=_box(C.INPUT_BORDER), locked=False),
        ns("ec_banner", _font(size=12, bold=True), fill=C.NA_FILL, border=_box(C.NAVY, "medium"), h="centerContinuous"),
        ns("ec_kpi_label", _font(C.MUTED, size=9), fill=C.BLUE_XLT, h="centerContinuous"),
        ns("ec_kpi", _font(C.NAVY, size=18, bold=True), fill=C.BLUE_XLT, h="centerContinuous"),
        # report sheet (style R)
        ns("ec_rep_title", _font(C.NAVY, size=20, bold=True)),
        ns("ec_rep_band", _font("FFFFFF", bold=True), fill=C.NAVY, h="centerContinuous"),
        ns("ec_rep_sec", _font("FFFFFF", bold=True), fill=C.BLUE),
        ns("ec_rep_label", _font(size=9), border=bottom),
        ns("ec_rep_value", _font(bold=True), fill=C.META_FILL, border=bottom, h="right"),
        ns("ec_rep_th", _font("FFFFFF", size=9, bold=True), fill=C.BLUE, h="centerContinuous"),
        ns("ec_rep_td", _font(size=9), border=bottom, h="right"),
        ns("ec_rep_total", _font(C.NAVY, bold=True), fill=C.BLUE_LT, border=Border(top=_side(C.NAVY, "medium")), h="right"),
        ns("ec_rep_tile", _font(C.NAVY, size=12, bold=True), fill=C.BLUE_XLT, h="centerContinuous"),
        ns("ec_rep_step", _font(C.NAVY, bold=True)),
        ns("ec_rep_formula", Font(name="Cambria Math", size=10)),
        ns("ec_rep_res", _font(bold=True), border=Border(bottom=_side(C.NAVY)), h="right"),
        ns("ec_rep_status", _font(bold=True), h="centerContinuous"),
        ns("ec_rep_note", _font(C.NOTE_FONT, size=9, italic=True)),
    ]


def _status_rules(ws: Worksheet, rng: str, anchor: str) -> None:
    """Colour a range by the first character of a status cell (anchor, relative row)."""
    for ch, fill, font in (
        (FAIL, C.FAIL_FILL, C.FAIL_FONT),
        (WARN, C.WARN_FILL, C.WARN_FONT),
        (OK, C.OK_FILL, C.OK_FONT),
        (NA, C.NA_FILL, C.NA_FONT),
    ):
        ws.conditional_formatting.add(
            rng,
            FormulaRule(formula=[f'LEFT({anchor},1)="{ch}"'], fill=_fill(fill),
                        font=Font(color=font, bold=True), stopIfTrue=True),
        )


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Meta:
    project: str
    title: str
    subject: str
    author: str
    date: dt.date
    checker: str = ""
    revision: str = "A"
    organisation: str = ""
    standard: str = ""
    domain: Domain = "general"


@dataclass(frozen=True)
class CheckRecord:
    sheet: str
    row: int
    label: str
    symbol: str
    numeric: bool  # True -> η in column E, False -> boolean condition


@dataclass(frozen=True)
class Col:
    key: str
    header: str
    fmt: str = "General"


@dataclass
class Block:
    """A contiguous data block on a DataSheet, usable as chart source."""

    ws: Worksheet
    first: int
    last: int
    cols: dict[str, int]

    def ref(self, key: str, *, header: bool = False) -> Reference:
        c = self.cols[key]
        return Reference(self.ws, min_col=c, max_col=c, min_row=self.first - (1 if header else 0), max_row=self.last)


# --------------------------------------------------------------------------- #
# Workbook
# --------------------------------------------------------------------------- #


class EngWorkbook:
    CHECKS = "80_Checks"
    README = "00_README"

    def __init__(self, meta: Meta) -> None:
        self.meta = meta
        self.wb = Workbook()
        for st in _style_defs():
            self.wb.add_named_style(st)
        self.names: dict[str, str] = {}  # name -> sheet title
        self.checks: list[CheckRecord] = []
        self.check_keys: dict[str, CheckRecord] = {}  # check / condition name -> record (report steps)
        self.input_spans: list[tuple[str, int, int, str]] = []  # sheet, first, last row, status column
        self.sheet_purpose: dict[str, str] = {}
        self._util_chart_requests: list[tuple[Worksheet, str, float, float]] = []
        self._readme = self.wb.active
        self._readme.title = self.README
        self._readme.sheet_properties.tabColor = TAB["readme"]
        self._checks_ws = self.wb.create_sheet(self.CHECKS)
        self._checks_ws.sheet_properties.tabColor = TAB["checks"]
        self.sheet_purpose[self.CHECKS] = "Register of all checks and conditions, overall status, η warning limit"
        self._init_readme_meta()
        self._init_checks_config()

    # -- names ------------------------------------------------------------- #
    def define(self, name: str, ws: Worksheet, coord: str) -> None:
        _check_name(name)
        clash = next((n for n in self.names if n.lower() == name.lower()), None)
        if clash:  # Excel names are case-insensitive: in_D and in_d are the same name
            raise ValueError(f"defined name {name!r} collides with {clash!r} (names are case-insensitive)")
        ref = f"{quote_sheetname(ws.title)}!{absolute_coordinate(coord)}"
        self.wb.defined_names[name] = DefinedName(name, attr_text=ref)
        self.names[name] = ws.title

    def sheet_of(self, formula: str) -> set[str]:
        return {self.names[t] for t in _tokens(formula) if t in self.names}

    # -- sheets ------------------------------------------------------------ #
    def _new_ws(self, name: str, tab: str, purpose: str) -> Worksheet:
        if not _SHEET_RE.match(name):
            raise ValueError(f"sheet name {name!r} must be NN_AsciiName")
        ws = self.wb.create_sheet(name)
        ws.sheet_properties.tabColor = tab
        self.sheet_purpose[name] = purpose
        return ws

    def calc_sheet(self, name: str, title: str, purpose: str) -> "CalcSheet":
        return CalcSheet(self, self._new_ws(name, TAB["calc"], purpose), title)

    def dashboard(self, name: str, title: str, purpose: str) -> "Dashboard":
        return Dashboard(self, self._new_ws(name, TAB["dashboard"], purpose), title)

    def data_sheet(self, name: str, title: str, purpose: str) -> "DataSheet":
        return DataSheet(self, self._new_ws(name, TAB["data"], purpose), title)

    def drawing_sheet(self, name: str, title: str, purpose: str) -> "DrawingSheet":
        return DrawingSheet(self, self._new_ws(name, TAB["calc"], purpose), title)

    def report_sheet(self, name: str, title: str, purpose: str, *, subtitle: str = "") -> "ReportSheet":
        return ReportSheet(self, self._new_ws(name, TAB["report"], purpose), title, subtitle)

    def screen_sheet(self, name: str, title: str, purpose: str) -> "ScreenSheet":
        return ScreenSheet(self, self._new_ws(name, TAB["calc"], purpose), title)

    # -- README ------------------------------------------------------------ #
    _META_ROWS = (
        ("meta_project", "Project", "project"),
        ("meta_title", "Calculation", "title"),
        ("meta_subject", "Subject", "subject"),
        ("meta_org", "Organisation", "organisation"),
        ("meta_std", "Standard / method", "standard"),
        ("meta_author", "Prepared by", "author"),
        ("meta_checker", "Checked by", "checker"),
        ("meta_rev", "Revision", "revision"),
        ("meta_date", "Date", "date"),
    )

    def _init_readme_meta(self) -> None:
        ws = self._readme
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 1.5
        ws.column_dimensions["B"].width = 24
        for col in "CDEFG":
            ws.column_dimensions[col].width = 16
        ws.column_dimensions["H"].width = 30
        ws["B1"] = "=meta_title&\"\""
        ws["B1"].font = _font(C.NAVY, size=16, bold=True)
        ws["B2"] = "README · workbook description, scope of validity, legend, revisions"
        ws["B2"].style = "ec_comment"
        self._section(ws, 4, "Calculation identification")
        for i, (name, label, attr) in enumerate(self._META_ROWS):
            r = 5 + i
            ws.cell(r, 2, label).style = "ec_label"
            c = ws.cell(r, 3, getattr(self.meta, attr))
            c.style = "ec_meta_input"
            if attr == "date":
                c.number_format = "yyyy-mm-dd"
            self.define(name, ws, c.coordinate)
        self._readme_row = 5 + len(self._META_ROWS) + 1

    @staticmethod
    def _section(ws: Worksheet, row: int, text: str, last_col: int = 8) -> None:
        for col in range(2, last_col + 1):
            ws.cell(row, col).style = "ec_h1"
        ws.cell(row, 2, text)

    def readme(self, *, purpose: str, scope: Sequence[str], assumptions: Sequence[str],
               workflow: Sequence[str], sources: Sequence[str],
               revisions: Sequence[tuple[str, str, str, str, str]]) -> None:
        """Fill the README body. Called once, any time before save()."""
        self._readme_spec = (purpose, scope, assumptions, workflow, sources, revisions)

    def _build_readme(self) -> None:
        ws = self._readme
        r = self._readme_row
        spec = getattr(self, "_readme_spec", None)
        if spec is None:
            raise RuntimeError("call EngWorkbook.readme(...) before save(): README is mandatory")
        purpose, scope, assumptions, workflow, sources, revisions = spec

        def para(title: str, lines: Sequence[str], bullet: str = "•") -> None:
            nonlocal r
            self._section(ws, r, title)
            r += 1
            for line in lines:
                ws.cell(r, 2, f"{bullet} {line}" if bullet else line).style = "ec_label"
                r += 1
            r += 1

        para("Purpose", [purpose], bullet="")
        para("Scope of validity", scope)
        para("Assumptions and limitations (outside scope = do not use)", assumptions)
        para("Workflow", [f"{i}. {s}" for i, s in enumerate(workflow, 1)], bullet="")

        self._section(ws, r, "Cell legend")
        r += 1
        legend = (
            ("ec_input", 12.5, "Manual input — the only cells you type into (unlocked)"),
            ("ec_select", "S235", "Selection from a list (data validation → lookup table)"),
            ("ec_const", 1.35, "Constant / value from a standard — do not change without a revision"),
            ("ec_calc", 42.0, "Formula on the same sheet"),
            ("ec_link", 42.0, "Formula reading another sheet (named range)"),
            ("ec_aux", 0.25, "Auxiliary intermediate result"),
            ("ec_result", 99.9, "Key result"),
        )
        for style, sample, text in legend:
            ws.cell(r, 2).value = sample
            ws.cell(r, 2).style = style
            ws.cell(r, 3, text).style = "ec_label"
            r += 1
        for status, text in (
            (f"{OK} OK", "Condition met, η ≤ warning limit"),
            (f"{WARN} OK – low reserve", "warning limit < η ≤ 1.00"),
            (f"{FAIL} FAILS", "η > 1.00, condition not met or input out of range"),
        ):
            c = ws.cell(r, 2, status)
            c.style = "ec_status"
            _status_rules(ws, c.coordinate, f"${get_column_letter(2)}{r}")
            ws.cell(r, 3, text).style = "ec_label"
            r += 1
        r += 1

        self._section(ws, r, "Contents")
        r += 1
        for ws_ in self.wb.worksheets:
            if ws_.title == self.README:
                continue
            c = ws.cell(r, 2, f'=HYPERLINK("#{quote_sheetname(ws_.title)}!A1","{ws_.title}")')
            c.font = _font(C.BLUE, bold=True)
            ws.cell(r, 3, self.sheet_purpose.get(ws_.title, "")).style = "ec_label"
            r += 1
        r += 1
        para("Sources", sources)

        self._section(ws, r, "Revision log")
        r += 1
        heads = ("Date", "Revision", "Change", "Prepared by", "Checked by")
        cols = (2, 3, 4, 7, 8)
        for col, h in zip(cols, heads):
            ws.cell(r, col, h).style = "ec_colhead"
        r += 1
        for rev in list(revisions) + [("", "", "", "", "")] * 3:
            for col, v in zip(cols, rev):
                ws.cell(r, col, v).style = "ec_meta_input"
            for col in (5, 6):
                ws.cell(r, col).style = "ec_meta_input"
            r += 1
        _page_setup(ws, f"A1:H{r}", title_rows=None)

    # -- checks register --------------------------------------------------- #
    def _init_checks_config(self) -> None:
        ws = self._checks_ws
        _scaffold(self, ws, "Check register", columns=False)
        ws.cell(8, COL["label"], "η warning limit (above it ▲ low reserve)").style = "ec_label"
        ws.cell(8, COL["sym"], "η_warn =").style = "ec_symbol"
        c = ws.cell(8, COL["val"], 0.9)
        c.style = "ec_input"
        c.number_format = "0.00"
        dv = DataValidation(type="decimal", operator="between", formula1="0.5", formula2="1",
                            showErrorMessage=True, errorTitle="Out of range",
                            error="Enter 0.50 … 1.00", promptTitle="η_warn", prompt="0.50 … 1.00")
        ws.add_data_validation(dv)
        dv.add(c.coordinate)
        ws.cell(8, COL["unit"], "–").style = "ec_unit"
        self.define("cfg_eta_warn", ws, c.coordinate)

    def _build_checks(self) -> None:
        ws = self._checks_ws
        heads = ("#", "Check / condition", "Symbol", "η [–]", "Status", "Sheet", "Link", "fail", "warn")
        hr = 10
        for i, h in enumerate(heads):
            ws.cell(hr, 2 + i, h).style = "ec_colhead"
        r = hr + 1
        first = r
        rows: list[tuple[str, str, str, str, str]] = []  # label, sym, eta, status, link
        ordered = [c for c in self.checks if c.numeric] + [c for c in self.checks if not c.numeric]
        for rec in ordered:  # numeric first: the utilisation chart reads a contiguous η block
            q = quote_sheetname(rec.sheet)
            eta = f"=IF(ISNUMBER({q}!$E${rec.row}),{q}!$E${rec.row},\"{NA}\")" if rec.numeric else f'="{NA}"'
            rows.append((rec.label, rec.symbol, eta, f"={q}!$I${rec.row}", rec.sheet + "|" + str(rec.row)))
        for sheet, a, b, col in self.input_spans:
            q = quote_sheetname(sheet)
            rng = f"{q}!${col}${a}:${col}${b}"
            status = (f'=IF(COUNTIF({rng},"{FAIL}*")=0,"{OK} all inputs within limits",'
                      f'"{FAIL} inputs out of range: "&COUNTIF({rng},"{FAIL}*"))')
            rows.append((f"Inputs of sheet {sheet} within allowed limits", "", f'="{NA}"', status, f"{sheet}|{a}"))
        for i, (label, sym, eta, status, link) in enumerate(rows, 1):
            sheet, row = link.split("|")
            ws.cell(r, 2, i).style = "ec_unit"
            ws.cell(r, 3, label).style = "ec_label"
            ws.cell(r, 4, sym).style = "ec_symbol"
            e = ws.cell(r, 5, eta)
            e.style = "ec_link"
            e.number_format = "0.00"
            ws.cell(r, 6, status).style = "ec_status"
            ws.cell(r, 7, sheet).style = "ec_unit"
            ws.cell(r, 8, f'=HYPERLINK("#{quote_sheetname(sheet)}!C{row}","→ row {row}")').font = _font(C.BLUE)
            ws.cell(r, 9, f'=IF(LEFT(F{r},1)="{FAIL}",1,0)').style = "ec_aux"
            ws.cell(r, 10, f'=IF(LEFT(F{r},1)="{WARN}",1,0)').style = "ec_aux"
            r += 1
        last = max(r - 1, first)
        self.define("chk_eta", ws, f"E{first}:E{last}")
        self.define("chk_fail", ws, f"I{first}:I{last}")
        self.define("chk_warn", ws, f"J{first}:J{last}")
        self._chk_span = (first, last)
        _status_rules(ws, f"F{first}:F{last}", f"$F{first}")
        ws.conditional_formatting.add(
            f"E{first}:E{last}",
            DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1.2, color=C.BLUE, showValue=True),
        )
        for col, w in zip("ABCDEFGHIJ", (1.5, 5, 46, 10, 10, 30, 12, 10, 6, 6)):
            ws.column_dimensions[col].width = w
        ws.cell(r + 1, 3, "η = utilisation (effect / resistance); fail/warn = flags for the overall status").style = "ec_comment"
        _page_setup(ws, f"A1:J{r + 1}", title_rows="1:7")

    def _build_util_charts(self) -> None:
        if not self._util_chart_requests:
            return
        first, last = self._chk_span
        n_numeric = sum(1 for c in self.checks if c.numeric)
        if n_numeric == 0:
            return
        ws = self._checks_ws
        lim_col = 12
        ws.cell(10, lim_col, "limit").style = "ec_colhead"
        for r in range(first, first + n_numeric):
            ws.cell(r, lim_col, 1).style = "ec_const"
        for target, anchor, w, h in self._util_chart_requests:
            bar = BarChart()
            bar.type = "bar"
            bar.style = 2
            bar.title = "Check utilisation η"
            bar.y_axis.title = "η [–]"
            bar.y_axis.scaling.min = 0
            bar.y_axis.scaling.max = 1.2
            bar.y_axis.majorGridlines = None
            bar.add_data(Reference(ws, min_col=5, min_row=first, max_row=first + n_numeric - 1), titles_from_data=False)
            bar.set_categories(Reference(ws, min_col=4, min_row=first, max_row=first + n_numeric - 1))
            s = bar.series[0]
            s.graphicalProperties.solidFill = C.BLUE
            s.graphicalProperties.line.noFill = True
            bar.legend = None
            bar.layout = Layout(manualLayout=ManualLayout(layoutTarget="inner", xMode="edge", yMode="edge",
                                                          x=0.14, y=0.14, w=0.82, h=0.68))
            bar.x_axis.delete = False
            bar.y_axis.delete = False
            bar.width, bar.height = w, h
            target.add_chart(bar, anchor)

    # -- output ------------------------------------------------------------ #
    def _order_sheets(self) -> None:
        for i, title in enumerate(sorted(self.wb.sheetnames)):
            ws = self.wb[title]
            self.wb.move_sheet(ws, offset=i - self.wb.index(ws))

    def save(self, path: str | Path, *, protect: bool = True) -> Path:
        self._order_sheets()
        self._build_checks()
        self._build_util_charts()
        self._build_readme()
        if protect:
            for ws in self.wb.worksheets:
                ws.protection.sheet = True
                ws.protection.formatColumns = False
                ws.protection.formatRows = False
        self.wb.active = 0
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.wb.save(out)
        return out


# --------------------------------------------------------------------------- #
# Shared scaffold: title block, banner, instructions, column header
# --------------------------------------------------------------------------- #


def _scaffold(book: EngWorkbook, ws: Worksheet, title: str, *, columns: bool = True) -> None:
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 100
    for _, (idx, width) in GRID.items():
        ws.column_dimensions[get_column_letter(idx)].width = width
    accent = DOMAIN_ACCENT[book.meta.domain]
    b, c, d, e, g, h, i = (COL[k] for k in ("id", "label", "sym", "val", "text", "src", "stat"))

    def meta(row: int, label_col: int, label: str, val_col: int, value: str, span_to: int) -> None:
        ws.cell(row, label_col, label).style = "ec_meta_label"
        cell = ws.cell(row, val_col, value)
        cell.style = "ec_meta"
        for col in range(val_col + 1, span_to + 1):
            ws.cell(row, col).style = "ec_meta"

    # left block: organisation / standard on accent colour
    for r in range(1, 5):
        for col in (b, c):
            ws.cell(r, col).fill = _fill(accent)
    ws.cell(1, b, "=meta_org&\"\"").font = _font("FFFFFF", size=11, bold=True)
    ws.cell(2, b, "Engineering calculation").font = _font("FFFFFF", size=9)
    ws.cell(3, b, "=meta_std&\"\"").font = _font("FFFFFF", size=8, italic=True)
    ws.cell(4, b, '="Revision "&meta_rev').font = _font("FFFFFF", size=8)
    meta(1, d, "Project", e, "=meta_project&\"\"", g)
    meta(2, d, "Calculation", e, "=meta_title&\"\"", g)
    ws.cell(2, e).font = _font(C.NAVY, size=12, bold=True)
    meta(3, d, "Sheet", e, f'="{title}"', g)
    meta(4, d, "Subject", e, "=meta_subject&\"\"", g)
    meta(1, h, "Sheet no.", i, fx('=SHEET()&" / "&SHEETS()'), i)
    meta(2, h, "Date", i, "=meta_date", i)
    ws.cell(2, i).number_format = "yyyy-mm-dd"
    meta(3, h, "Prepared by", i, "=meta_author&\"\"", i)
    meta(4, h, "Checked by", i, "=meta_checker&\"\"", i)
    for col in range(b, i + 1):
        ws.cell(4, col).border = Border(bottom=_side(C.NAVY, "medium"))
        ws.cell(1, col).border = Border(top=_side(C.NAVY, "medium"))
    for col in (d, h):
        for r in range(1, 5):
            cell = ws.cell(r, col)
            cell.border = Border(left=_side(C.GRID), top=cell.border.top, bottom=cell.border.bottom)
    for r in range(1, 5):
        ws.row_dimensions[r].height = 16

    # banner
    ws.row_dimensions[5].height = 26
    banner = ws.cell(5, b, _banner_formula())
    for col in range(b, i + 1):
        ws.cell(5, col).style = "ec_banner"
    _status_rules(ws, f"{get_column_letter(b)}5:{get_column_letter(i)}5", f"${get_column_letter(b)}$5")
    del banner
    ws.cell(6, b, (
        "Type only into yellow cells (blue font) · teal = pick from list · purple = value from a standard · "
        f"{OK} OK  {WARN} low reserve  {FAIL} fails"
    )).style = "ec_comment"
    if columns:
        for key, text in (("id", "#"), ("label", "Quantity"), ("sym", "Symbol"), ("val", "Value"),
                          ("unit", "Unit"), ("text", "Relation / condition"), ("src", "Source / standard"),
                          ("stat", "Limit / status")):
            ws.cell(HEADER_ROWS, COL[key], text).style = "ec_colhead"
        ws.freeze_panes = ws.cell(HEADER_ROWS + 1, 1)


def _bounded(book: EngWorkbook, key: str, name: str, unit: str, *, lo: float | None, hi: float | None,
             choices: str | None, ref: str, short: bool = False) -> tuple[DataValidation, str, str]:
    """Data validation, status formula (✔ / ✘) and range hint for a manual input cell `ref`."""
    if choices:
        if choices not in book.names:
            raise KeyError(f"list name {choices!r} not defined yet (DataSheet.table first)")
        dv = DataValidation(type="list", formula1=f"={choices}", allow_blank=False, showErrorMessage=True,
                            errorTitle="Invalid choice", error="Pick a value from the list",
                            promptTitle=name[:30], prompt="Pick from the list", showInputMessage=True)
        ok, bad = ("", "") if short else (" from list", " not in list")
        return dv, f'=IF(ISNUMBER(MATCH({ref},{choices},0)),"{OK}{ok}","{FAIL}{bad}")', "pick from list"
    if lo is None or hi is None:
        raise ValueError(f"input {key!r} needs lo/hi or choices — every input must be bounded")
    if lo > hi:
        raise ValueError(f"{key}: lo > hi")
    dv = DataValidation(type="decimal", operator="between", formula1=repr(float(lo)), formula2=repr(float(hi)),
                        showErrorMessage=True, errorTitle="Outside scope of validity",
                        error=f"{name}: allowed {lo:g} … {hi:g} {unit}",
                        promptTitle=name[:32], prompt=f"{lo:g} … {hi:g} {unit}", showInputMessage=True)
    ok, bad = ("", "") if short else (" within limits", " out of range")
    return (dv, f'=IF(AND(ISNUMBER({ref}),{ref}>={lo!r},{ref}<={hi!r}),"{OK}{ok}","{FAIL}{bad}")',
            f"⟨{lo:g} ; {hi:g}⟩ {unit}")


def _banner_formula(short: bool = False) -> str:
    """Overall status from the register totals; `short` for the narrow report status panel."""
    fail, warn, ok, sep = (("FAILS: ", "LOW RESERVE: ", "OK", "   ") if short else
                           ("FAILS – conditions not met: ", "OK WITH LOW RESERVE – checks: ",
                            "ALL CHECKS AND CONDITIONS SATISFIED", "     "))
    return (f'=IF(SUM(chk_fail)>0,"{FAIL} {fail}"&SUM(chk_fail),'
            f'IF(SUM(chk_warn)>0,"{WARN} {warn}"&SUM(chk_warn),"{OK} {ok}"))'
            f'&"{sep}η max = "&IF(COUNT(chk_eta)>0,FIXED(MAX(chk_eta),2),"{NA}")')


def _page_setup(ws: Worksheet, area: str, *, title_rows: str | None, landscape: bool = False) -> None:
    ws.print_area = area
    if title_rows:
        ws.print_title_rows = title_rows
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    ws.oddFooter.left.text = "&8&F"
    ws.oddFooter.center.text = "&8&A"
    ws.oddFooter.right.text = "&8Page &P / &N"
    ws.print_options.horizontalCentered = True


# --------------------------------------------------------------------------- #
# Calc sheet
# --------------------------------------------------------------------------- #


class CalcSheet:
    """Vertical calculation pad: one row = one quantity / step / condition."""

    def __init__(self, book: EngWorkbook, ws: Worksheet, title: str) -> None:
        self.book, self.ws, self.title = book, ws, title
        self.r = HEADER_ROWS + 2
        self._sec = 0
        self._item = 0
        self._in_first: int | None = None
        self._in_last: int | None = None
        self._status_first = self.r
        _scaffold(book, ws, title)

    # -- layout primitives -------------------------------------------------- #
    def _cell(self, key: str, value: Scalar, style: str, row: int | None = None) -> Cell:
        c = self.ws.cell(row or self.r, COL[key], value)
        c.style = style
        return c

    def _row_frame(self, label: str, symbol: str, unit: str, source: str) -> None:
        self._item += 1
        self._cell("id", f"{self._sec}.{self._item}", "ec_unit")
        self._cell("label", label, "ec_label")
        self._cell("sym", f"{symbol} =" if symbol else "", "ec_symbol")
        self._cell("unit", unit, "ec_unit")
        self._cell("text", None, "ec_text")
        self._cell("src", source, "ec_source")
        self._cell("stat", None, "ec_status")

    def section(self, title: str) -> None:
        if self.r > HEADER_ROWS + 2:
            self.r += 1
        self._sec += 1
        self._item = 0
        for col in range(COL["id"], COL["stat"] + 1):
            self.ws.cell(self.r, col).style = "ec_h1"
        self.ws.cell(self.r, COL["id"], f"{self._sec}")
        self.ws.cell(self.r, COL["label"], title.upper())
        self.ws.row_dimensions[self.r].height = 18
        self.r += 1

    def subsection(self, title: str) -> None:
        for col in range(COL["id"], COL["stat"] + 1):
            self.ws.cell(self.r, col).style = "ec_h2"
        self.ws.cell(self.r, COL["label"], title)
        self.r += 1

    def comment(self, text: str) -> None:
        self._cell("label", text, "ec_comment")
        self.r += 1

    # -- quantities --------------------------------------------------------- #
    def input(self, key: str, label: str, symbol: str, value: Scalar, unit: str, *,
              lo: float | None = None, hi: float | None = None, choices: str | None = None,
              fmt: str = "0.00", source: str = "brief") -> Cell:
        """Manual input. Numeric inputs need lo/hi; selection inputs need a list name (lst_*)."""
        self._row_frame(label, symbol, unit, source)
        cell = self._cell("val", value, "ec_select" if choices else "ec_input")
        cell.number_format = fmt if not choices else "@"
        ref = f"${get_column_letter(COL['val'])}{self.r}"
        dv, status, hint = _bounded(self.book, key, symbol or label, unit, lo=lo, hi=hi, choices=choices, ref=ref)
        self._cell("text", hint, "ec_comment")
        self.ws.add_data_validation(dv)
        dv.add(cell.coordinate)
        self._cell("stat", status, "ec_status")
        self.book.define(key, self.ws, cell.coordinate)
        self._in_first = self._in_first or self.r
        self._in_last = self.r
        self.r += 1
        return cell

    def const(self, key: str, label: str, symbol: str, value: float, unit: str, *, source: str,
              fmt: str = "0.00") -> Cell:
        """Fixed value from a standard / datasheet. Source is mandatory."""
        if not source:
            raise ValueError(f"const {key!r} needs a source")
        self._row_frame(label, symbol, unit, source)
        cell = self._cell("val", value, "ec_const")
        cell.number_format = fmt
        self.book.define(key, self.ws, cell.coordinate)
        self.r += 1
        return cell

    def calc(self, key: str | None, label: str, symbol: str, formula: str, unit: str, *,
             text: str = "", source: str = "", fmt: str = "0.00", aux: bool = False,
             result: bool = False) -> Cell:
        """Formula row. `text` = the relation as written in the report (documents literals)."""
        f = fx(formula)
        foreign = self.book.sheet_of(f) - {self.ws.title}
        style = "ec_result" if result else "ec_aux" if aux else "ec_link" if foreign else "ec_calc"
        self._row_frame(label, symbol, unit, source)
        cell = self._cell("val", f, style)
        cell.number_format = fmt
        if text:
            self.ws.cell(self.r, COL["text"], text)
        if key:
            self.book.define(key, self.ws, cell.coordinate)
        self.r += 1
        return cell

    def result(self, key: str, label: str, symbol: str, formula: str, unit: str, **kw: object) -> Cell:
        return self.calc(key, label, symbol, formula, unit, result=True, **kw)  # type: ignore[arg-type]

    # -- conditions --------------------------------------------------------- #
    def check(self, key: str, label: str, symbol: str, value: str, limit: str, unit: str, *,
              kind: CheckKind = "le", dec: int = 2, source: str = "") -> Cell:
        """Limit state: le → value ≤ limit (η = value/limit); ge → value ≥ limit (η = limit/value)."""
        v, lim = fx(value)[1:], fx(limit)[1:]
        eta = f"=({v})/({lim})" if kind == "le" else f"=({lim})/({v})"
        op = "≤" if kind == "le" else "≥"
        self._row_frame(label, symbol, "–", source)
        cell = self._cell("val", eta, "ec_calc")
        cell.number_format = "0.00"
        cell.font = _font(bold=True)
        e = f"${get_column_letter(COL['val'])}{self.r}"
        u = f" {unit}" if unit else ""
        self.ws.cell(self.r, COL["text"], f'=FIXED({v},{dec})&" {op} "&FIXED({lim},{dec})&"{u}"')
        self._cell("stat", (
            f'=IF(NOT(ISNUMBER({e})),"{FAIL} CANNOT EVALUATE",IF({e}>1,"{FAIL} FAILS",'
            f'IF({e}>cfg_eta_warn,"{WARN} OK – low reserve","{OK} OK")))'
        ), "ec_status")
        self.book.define(key, self.ws, cell.coordinate)
        rec = CheckRecord(self.ws.title, self.r, label, symbol, True)
        self.book.checks.append(rec)
        self.book.check_keys[key] = rec
        self.r += 1
        return cell

    def condition(self, key: str, label: str, condition: str, *, ok: str, fail: str,
                  text: str = "", source: str = "") -> Cell:
        """Boolean validity condition (scope of the method, regime, required assumption)."""
        cond = fx(condition)[1:]
        self._row_frame(label, "", "", source)
        self._cell("val", f'=IF({cond},"YES","NO")', "ec_calc")
        if text:
            self.ws.cell(self.r, COL["text"], text)
        cell = self._cell("stat", f'=IF({cond},"{OK} {ok}","{FAIL} {fail}")', "ec_status")
        self.book.define(key, self.ws, cell.coordinate)
        rec = CheckRecord(self.ws.title, self.r, label, "", False)
        self.book.checks.append(rec)
        self.book.check_keys[key] = rec
        self.r += 1
        return cell

    def remark(self, label: str, formula: str) -> Cell:
        """Dynamic engineering remark (regime / interpretation), e.g. IF(Re>4000,"turbulent",…)."""
        self._cell("id", "", "ec_unit")
        self._cell("label", label, "ec_label")
        self._cell("sym", "→", "ec_symbol")
        cell = self._cell("val", fx(formula), "ec_note")
        cell.alignment = Alignment(horizontal="left", vertical="center")
        self.r += 1
        return cell

    # -- graphics ----------------------------------------------------------- #
    def equation(self, latex: str, *, fontsize: int = 13) -> None:
        """Render a relation with matplotlib mathtext and place it in the label column."""
        img = _mathtext_png(latex, fontsize=fontsize)
        self._place_image(img)

    def figure(self, png: bytes | str | Path, *, width_px: int | None = None) -> None:
        """Static sketch (matplotlib PNG bytes or a file)."""
        data = png if isinstance(png, bytes) else Path(png).read_bytes()
        self._place_image(data, width_px=width_px)

    def _place_image(self, data: bytes, *, width_px: int | None = None) -> None:
        from PIL import Image as PILImage

        with PILImage.open(io.BytesIO(data)) as im:
            w, h = im.size
            dpi = im.info.get("dpi", (96, 96))[0] or 96
        scale = 96.0 / float(dpi)
        w, h = w * scale, h * scale
        if width_px:
            h, w = h * width_px / w, width_px
        img = XLImage(io.BytesIO(data))
        img.width, img.height = int(w), int(h)
        self.ws.add_image(img, f"{get_column_letter(COL['label'])}{self.r}")
        rows = max(1, int(h / 20) + 1)
        if rows == 1:
            self.ws.row_dimensions[self.r].height = h * 0.75 + 6
        self.r += rows

    def chart(self, chart: ScatterChart | BarChart | LineChart, *, rows: int = 16) -> None:
        self.ws.add_chart(chart, f"{get_column_letter(COL['label'])}{self.r}")
        self.r += rows

    # -- finish ------------------------------------------------------------- #
    def close(self) -> None:
        """Call after the last row: status colouring, input span, print area."""
        last = self.r
        stat = get_column_letter(COL["stat"])
        val = get_column_letter(COL["val"])
        _status_rules(self.ws, f"{stat}{self._status_first}:{stat}{last}", f"${stat}{self._status_first}")
        self.ws.conditional_formatting.add(
            f"{val}{self._status_first}:{val}{last}",
            FormulaRule(formula=[f'LEFT(${stat}{self._status_first},1)="{FAIL}"'],
                        fill=_fill(C.FAIL_FILL), font=Font(color=C.FAIL_FONT, bold=True)),
        )
        if self._in_first is not None and self._in_last is not None:
            self.book.input_spans.append((self.ws.title, self._in_first, self._in_last, stat))
        _page_setup(self.ws, f"A1:{get_column_letter(COL['margin_r'])}{last}", title_rows=f"1:{HEADER_ROWS}")


# --------------------------------------------------------------------------- #
# Data sheet (databases, chart data)
# --------------------------------------------------------------------------- #


class DataSheet:
    def __init__(self, book: EngWorkbook, ws: Worksheet, title: str) -> None:
        self.book, self.ws = book, ws
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 1.5
        ws["B1"] = title
        ws["B1"].font = _font(C.NAVY, size=14, bold=True)
        ws["B2"] = "=meta_title&\"\""
        ws["B2"].style = "ec_comment"
        self.r = 4
        self._max_col = 2

    def table(self, name: str, cols: Sequence[Col], rows: Sequence[Sequence[Scalar]], *,
              source: str, key: str | None = None) -> Block:
        """Excel Table + names db_<name>_<col>, db_<name>_key and lst_<name> (dropdown source).

        The first column is the lookup key unless `key` names another column.
        """
        if not rows:
            raise ValueError(f"table {name!r} is empty")
        ws = self.ws
        ws.cell(self.r, 2, f"tbl_{name}").font = _font(C.NAVY, bold=True)
        ws.cell(self.r + 1, 2, f"Source: {source}").style = "ec_source"
        hr = self.r + 2
        for j, col in enumerate(cols):
            ws.cell(hr, 2 + j, col.header)
            ws.column_dimensions[get_column_letter(2 + j)].width = max(10, len(col.header) + 2)
        for i, row in enumerate(rows, 1):
            if len(row) != len(cols):
                raise ValueError(f"table {name!r} row {i}: {len(row)} values for {len(cols)} columns")
            for j, (v, col) in enumerate(zip(row, cols)):
                c = ws.cell(hr + i, 2 + j, fx(v) if isinstance(v, str) and v.startswith("=") else v)
                c.number_format = col.fmt
                c.style = "ec_const" if not (isinstance(v, str) and v.startswith("=")) else "ec_calc"
                c.number_format = col.fmt
        last = hr + len(rows)
        ref = f"B{hr}:{get_column_letter(1 + len(cols))}{last}"
        t = Table(displayName=f"tbl_{name}", ref=ref)
        t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(t)
        colmap = {col.key: 2 + j for j, col in enumerate(cols)}
        for col in cols:
            if col.key == "key":
                continue  # defined below as db_<name>_key
            letter = get_column_letter(colmap[col.key])
            self.book.define(f"db_{name}_{col.key}", ws, f"{letter}{hr + 1}:{letter}{last}")
        key_letter = get_column_letter(colmap[key or cols[0].key])
        self.book.define(f"db_{name}_key", ws, f"{key_letter}{hr + 1}:{key_letter}{last}")
        self.book.define(f"lst_{name}", ws, f"{key_letter}{hr + 1}:{key_letter}{last}")
        self._max_col = max(self._max_col, 1 + len(cols))
        self.r = last + 3
        return Block(ws, hr + 1, last, colmap)

    def block(self, name: str, cols: Sequence[Col], rows: Sequence[Sequence[Scalar]], *, note: str = "") -> Block:
        """Formula-driven block (chart data, sketch coordinates). Names gd_<name>_<col>."""
        ws = self.ws
        ws.cell(self.r, 2, name).font = _font(C.NAVY, bold=True)
        if note:
            ws.cell(self.r + 1, 2, note).style = "ec_source"
        hr = self.r + 2
        for j, col in enumerate(cols):
            ws.cell(hr, 2 + j, col.header).style = "ec_colhead"
        for i, row in enumerate(rows, 1):
            for j, (v, col) in enumerate(zip(row, cols)):
                is_f = isinstance(v, str) and v.startswith("=")
                c = ws.cell(hr + i, 2 + j, fx(v) if is_f else v)
                c.style = "ec_calc" if is_f else "ec_const"
                c.number_format = col.fmt
        last = hr + len(rows)
        colmap = {col.key: 2 + j for j, col in enumerate(cols)}
        for col in cols:
            letter = get_column_letter(colmap[col.key])
            self.book.define(f"gd_{name}_{col.key}", ws, f"{letter}{hr + 1}:{letter}{last}")
        self._max_col = max(self._max_col, 1 + len(cols))
        self.r = last + 3
        return Block(ws, hr + 1, last, colmap)

    def hatch(self, name: str, x0: str, x1: str, y0: str, y1: str, *, spacing: str,
              side: Literal["lower", "upper"] = "lower", n: int = 40) -> Block:
        """Live 45° section hatching of the rectangle ⟨x0;x1⟩ × ⟨y0;y1⟩ (formulas, drawing units).

        One chart series draws the whole hatch: each line y = x + k is drawn there and back,
        and the moves to the next line run along two rectangle edges — `side="lower"` uses the
        bottom and left edges, `"upper"` the top and right edges. Pick the side whose edges are
        visible outline of the part (not an edge shared with the neighbouring rectangle), so
        the moves hide under the outline. Spacing grows when more than n lines would be needed.
        Returns the path block (columns x, y) for `drawing_chart`.
        """
        p = f"gd_{name}_rect_"
        self.block(f"{name}_rect", [Col(k, k, "0.00") for k in ("x0", "x1", "y0", "y1", "kmin", "kmax", "s")], [(
            f"={x0}", f"={x1}", f"={y0}", f"={y1}", f"={p}y0-{p}x1", f"={p}y1-{p}x0",
            f"=MAX({spacing},({p}kmax-{p}kmin)/{n})",
        )], note=f"Hatched rectangle; hatch lines y = x + k, k from kmin to kmax with step s (at most {n} lines)")
        first = self.r + 3
        lines = []
        for j in range(1, n + 1):
            r = first + j - 1
            lines.append((j, f"=MIN({p}kmax,{p}kmin+B{r}*{p}s)", f"=MAX({p}x0,{p}y0-C{r})", f"=D{r}+C{r}",
                          f"=MIN({p}x1,{p}y1-C{r})", f"=F{r}+C{r}"))
        self.block(f"{name}_lines", [Col("j", "j", "0"), Col("k", "k", "0.00"), Col("xl", "x lower", "0.00"),
                                      Col("yl", "y lower", "0.00"), Col("xu", "x upper", "0.00"),
                                      Col("yu", "y upper", "0.00")], lines,
                   note="Intersections of each hatch line with the rectangle (lower / upper end)")
        path: list[tuple[str, str]] = []
        for j in range(n):
            r, nxt = first + j, first + min(j + 1, n - 1)
            low, up = (f"=D{r}", f"=E{r}"), (f"=F{r}", f"=G{r}")
            if side == "lower":  # corner between two lower ends = (min x, min y)
                path += [low, up, low, (f"=MIN(D{r},D{nxt})", f"=MIN(E{r},E{nxt})")]
            else:  # corner between two upper ends = (max x, max y)
                path += [up, low, up, (f"=MAX(F{r},F{nxt})", f"=MAX(G{r},G{nxt})")]
        return self.block(f"{name}_path", [Col("x", "x", "0.00"), Col("y", "y", "0.00")], path,
                          note=f"Hatch path: each line there and back, moves along the {side} edges of the rectangle")

    def close(self) -> None:
        _page_setup(self.ws, f"A1:{get_column_letter(self._max_col + 1)}{self.r}", title_rows=None, landscape=True)


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #


class Dashboard:
    """Overview page: banner, KPI tiles, charts. References only — no inputs, no logic."""

    def __init__(self, book: EngWorkbook, ws: Worksheet, title: str) -> None:
        self.book, self.ws = book, ws
        _scaffold(book, ws, title, columns=False)
        self.r = HEADER_ROWS + 1

    def kpis(self, tiles: Sequence[tuple[str, str, str, str]]) -> None:
        """Up to 4 tiles per row: (label, formula, unit, number format)."""
        spans = ((2, 3), (4, 5), (6, 7), (8, 9))
        for start in range(0, len(tiles), 4):
            for (label, formula, unit, fmt), (c0, c1) in zip(tiles[start:start + 4], spans):
                for col in range(c0, c1 + 1):
                    for rr, st in ((self.r, "ec_kpi_label"), (self.r + 1, "ec_kpi"), (self.r + 2, "ec_kpi_label")):
                        self.ws.cell(rr, col).style = st
                self.ws.cell(self.r, c0, label)
                v = self.ws.cell(self.r + 1, c0, fx(formula))
                v.number_format = fmt
                self.ws.cell(self.r + 2, c0, unit)
                for col in range(c0, c1 + 1):
                    self.ws.cell(self.r, col).border = Border(top=_side(C.NAVY, "medium"))
            self.ws.row_dimensions[self.r + 1].height = 32
            self.r += 4

    def chart(self, chart: ScatterChart | BarChart | LineChart, anchor: str) -> None:
        self.ws.add_chart(chart, anchor)

    def utilization_chart(self, anchor: str, *, width: float = 12.0, height: float = 7.0) -> None:
        self.book._util_chart_requests.append((self.ws, anchor, width, height))

    def figure(self, png: bytes, anchor: str, *, width_px: int) -> None:
        from PIL import Image as PILImage

        with PILImage.open(io.BytesIO(png)) as im:
            w, h = im.size
        img = XLImage(io.BytesIO(png))
        img.width, img.height = width_px, int(h * width_px / w)
        self.ws.add_image(img, anchor)

    def close(self, last_row: int) -> None:
        _page_setup(self.ws, f"A1:{get_column_letter(COL['margin_r'])}{last_row}", title_rows=None)


class DrawingSheet(Dashboard):
    """Part drawing page: live section / view charts, GD&T frames, title block (ISO 7200)."""

    def gdt_frame(self, row: int, col: int, symbol: str, value: str, datum: str = "", note: str = "") -> None:
        """Feature control frame as three boxed cells: symbol | tolerance (formula) | datum."""
        for k, v in enumerate((symbol, fx(value) if value.startswith("=") else value, datum)):
            c = self.ws.cell(row, col + k, v)
            c.border = _box(C.NAVY, "medium")
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.font = _font(C.NAVY, size=12 if k == 0 else 10, bold=k != 1)
        if note:
            self.ws.cell(row, col + 3, note).style = "ec_comment"

    def title_block(self, row: int, col: int, fields: Sequence[tuple[str, str]], *, width: int = 4) -> int:
        """Title block: (label, value or formula) pairs, `width` fields per row. Returns next free row."""
        for k, (label, value) in enumerate(fields):
            r, c = row + 2 * (k // width), col + 2 * (k % width)
            lab = self.ws.cell(r, c, label)
            lab.style = "ec_meta_label"
            val = self.ws.cell(r + 1, c, fx(value) if value.startswith("=") else value)
            val.style = "ec_meta"
            for cell in (lab, val, self.ws.cell(r, c + 1), self.ws.cell(r + 1, c + 1)):
                left = _side(C.NAVY, "medium") if cell.column == c else None
                cell.border = Border(left=left, top=_side(C.NAVY) if cell.row == r else None,
                                     bottom=_side(C.NAVY) if cell.row == r + 1 else None)
        rows = 2 * ((len(fields) + width - 1) // width)
        for c in range(col, col + 2 * width):
            self.ws.cell(row, c).border = Border(top=_side(C.NAVY, "medium"), left=self.ws.cell(row, c).border.left)
            last = self.ws.cell(row + rows - 1, c)
            last.border = Border(bottom=_side(C.NAVY, "medium"), left=last.border.left)
        return row + rows


# --------------------------------------------------------------------------- #
# Report sheet (style R — printable calculation report / data sheet)
# --------------------------------------------------------------------------- #

_SUBST_RE = re.compile(r"\{([^{}:]+)(?::(\d+))?\}")


def subst(template: str, dec: int = 2) -> str:
    """Substituted values as text: '{calc_qEd}·{in_L:1}²/8' → FIXED(calc_qEd,2,TRUE)&"·"&FIXED(in_L,1,TRUE)&"²/8".

    Placeholders are names or expressions, optionally with decimals after a colon. Returns an
    Excel string expression without the leading '=' (the substitution line of a report step).
    """
    def lit(text: str) -> str:
        return '"' + text.replace('"', '""') + '"'

    parts: list[str] = []
    pos = 0
    for m in _SUBST_RE.finditer(template):
        if m.start() > pos:
            parts.append(lit(template[pos:m.start()]))
        parts.append(f"FIXED({m.group(1)},{m.group(2) or dec},TRUE)")
        pos = m.end()
    if pos < len(template):
        parts.append(lit(template[pos:]))
    return "&".join(parts) or '""'


def _val(v: Scalar) -> Scalar:
    return fx(v) if isinstance(v, str) and v.startswith("=") else v


class ReportSheet:
    """Printable calculation report / data sheet (style R), A4 portrait on a 12-column grid.

    Blocks flow in two halves side by side (`at="left"` columns B–G, `at="right"` H–M) or
    across the full width (`at="full"`, starts below both halves). References only: every
    value is a formula reading a named quantity from a calc sheet — the report adds layout,
    relations with substituted values, tables and signatures, never logic.
    """

    NCOLS, COL_W, COL_PX = 12, 8.0, 61  # content columns B..M, width in characters / pixels
    SPANS: dict[str, tuple[int, int]] = {"left": (2, 7), "right": (8, 13), "full": (2, 13)}
    ZONES: dict[str, tuple[str, ...]] = {"left": ("left",), "right": ("right",), "full": ("left", "right")}

    def __init__(self, book: EngWorkbook, ws: Worksheet, title: str, subtitle: str = "") -> None:
        self.book, self.ws, self.title = book, ws, title
        self._sec = 0
        self._item = 0
        self._next = {z: 4 for z in self.ZONES["full"]}
        ws.sheet_view.showGridLines = False
        ws.column_dimensions["A"].width = 1.5
        ws.column_dimensions[get_column_letter(self.NCOLS + 2)].width = 1.5
        for c in range(2, self.NCOLS + 2):
            ws.column_dimensions[get_column_letter(c)].width = self.COL_W
        self._header(title, subtitle)

    def _header(self, title: str, subtitle: str) -> None:
        ws, book = self.ws, self.book
        ws.cell(1, 2, title.upper()).style = "ec_rep_title"
        org = ws.cell(1, self.NCOLS + 1, '=meta_org&""')
        org.font = _font(DOMAIN_ACCENT[book.meta.domain], size=11, bold=True)
        org.alignment = Alignment(horizontal="right", vertical="center")
        ws.row_dimensions[1].height = 30
        for c in range(2, self.NCOLS + 2):
            ws.cell(2, c).style = "ec_rep_band"
        ws.cell(2, 2, subtitle or '=meta_subject&""')
        ws.row_dimensions[2].height = 20
        self.fields([("Project", '=meta_project&""', "", "@"), ("Calculation", '=meta_title&""', "", "@"),
                     ("Standard / method", '=meta_std&""', "", "@")], at="left", label_cols=2)
        iso = 'YEAR(meta_date)&"-"&RIGHT("0"&MONTH(meta_date),2)&"-"&RIGHT("0"&DAY(meta_date),2)'
        self.fields([("Date", f"=IF(ISNUMBER(meta_date),{iso},meta_date&\"\")", "", "@"), ("Revision", '=meta_rev&""', "", "@"),
                     ("Prepared by", '=meta_author&""', "", "@"), ("Checked by", '=meta_checker&""', "", "@")],
                    at="right", label_cols=2)

    # -- flow --------------------------------------------------------------- #
    def _at(self, at: Place) -> tuple[int, int, int]:
        c0, c1 = self.SPANS[at]
        return max(self._next[z] for z in self.ZONES[at]), c0, c1

    def _done(self, at: Place, row: int, gap: int = 1) -> None:
        for z in self.ZONES[at]:
            self._next[z] = row + gap

    def _image(self, data: bytes, row: int, col: int, width_px: int | None) -> int:
        """Place a PNG at (row, col); returns the number of rows it covers."""
        from PIL import Image as PILImage

        with PILImage.open(io.BytesIO(data)) as im:
            w, h = im.size
            dpi = im.info.get("dpi", (96, 96))[0] or 96
        w, h = w * 96.0 / float(dpi), h * 96.0 / float(dpi)
        if width_px and w > width_px:
            h, w = h * width_px / w, width_px
        img = XLImage(io.BytesIO(data))
        img.width, img.height = int(w), int(h)
        self.ws.add_image(img, f"{get_column_letter(col)}{row}")
        return max(1, int(h / 20) + 1)

    def page_break(self) -> None:
        """Start a new printed page below everything placed so far."""
        row = max(self._next.values())
        self.ws.row_breaks.append(Break(id=row - 1))

    # -- blocks ------------------------------------------------------------- #
    def section(self, title: str, *, at: Place = "full", unit: str = "") -> None:
        """Section band; full-width sections are numbered and number the steps below them."""
        r, c0, c1 = self._at(at)
        text = title.upper() + (f"  ({unit})" if unit else "")
        if at == "full":
            self._sec += 1
            self._item = 0
            text = f"{self._sec}   {text}"
        for c in range(c0, c1 + 1):
            self.ws.cell(r, c).style = "ec_rep_sec"
        self.ws.cell(r, c0, text)
        self.ws.row_dimensions[r].height = 18
        self._done(at, r + 1, gap=0)

    def fields(self, rows: Sequence[tuple[str, str, str, str]], *, at: Place = "left",
               label_cols: int | None = None, title: str = "") -> None:
        """Label | value | unit rows: (label, formula, unit, number format; "@" = text, left aligned)."""
        if title:
            self.section(title, at=at)
        r, c0, c1 = self._at(at)
        lc = label_cols or (c1 - c0 + 1) // 2
        for label, formula, unit, fmt in rows:
            for c in range(c0, c1 + 1):
                self.ws.cell(r, c).style = "ec_rep_label" if c < c0 + lc else "ec_rep_value"
            self.ws.cell(r, c0, label)
            if fmt == "@":
                v = self.ws.cell(r, c0 + lc, _val(formula))
                v.alignment = Alignment(horizontal="left", vertical="center")
            else:
                v = self.ws.cell(r, c1 - 1, _val(formula))
                v.number_format = fmt
            if unit:
                u = self.ws.cell(r, c1, unit)
                u.font = _font(C.MUTED, size=9)
                u.alignment = Alignment(horizontal="left", vertical="center")
            r += 1
        self._done(at, r)

    def panel(self, label: str, formula: str, unit: str = "", fmt: str = "0.00", *, at: Place = "right",
              tiles: Sequence[tuple[str, str, str]] = ()) -> None:
        """Highlighted key result (big number) with up to 3 small tiles below: (label, formula, format)."""
        r, c0, c1 = self._at(at)
        for rr, st in ((r, "ec_kpi_label"), (r + 1, "ec_kpi"), (r + 2, "ec_kpi_label")):
            for c in range(c0, c1 + 1):
                self.ws.cell(rr, c).style = st
        for c in range(c0, c1 + 1):
            self.ws.cell(r, c).border = Border(top=_side(C.NAVY, "medium"))
        self.ws.cell(r, c0, label)
        self.ws.cell(r + 1, c0, _val(formula)).number_format = fmt
        self.ws.cell(r + 2, c0, unit)
        self.ws.row_dimensions[r + 1].height = 28
        r += 3
        if tiles:
            w = (c1 - c0 + 1) // len(tiles)
            for k, (lab, f, ft) in enumerate(tiles):
                a = c0 + k * w
                b = c1 if k == len(tiles) - 1 else a + w - 1
                for c in range(a, b + 1):
                    self.ws.cell(r, c).style = "ec_rep_th"
                    self.ws.cell(r + 1, c).style = "ec_rep_tile"
                self.ws.cell(r, a, lab)
                self.ws.cell(r + 1, a, _val(f)).number_format = ft
            self.ws.row_dimensions[r + 1].height = 22
            r += 2
        self._done(at, r)

    def status(self, *, at: Place = "right") -> None:
        """DESIGN STATUS: overall result from the check register, coloured ✔ / ▲ / ✘."""
        r, c0, c1 = self._at(at)
        for c in range(c0, c1 + 1):
            self.ws.cell(r, c).style = "ec_kpi_label"
            self.ws.cell(r + 1, c).style = "ec_banner"
        self.ws.cell(r, c0, "DESIGN STATUS")
        self.ws.cell(r + 1, c0, _banner_formula(short=True))
        a, b = get_column_letter(c0), get_column_letter(c1)
        _status_rules(self.ws, f"{a}{r + 1}:{b}{r + 1}", f"${a}${r + 1}")
        self.ws.row_dimensions[r + 1].height = 24
        self._done(at, r + 2)

    def table(self, cols: Sequence[Col], rows: Sequence[Sequence[Scalar]], *, at: Place = "full",
              spans: Sequence[int] | None = None, total: dict[str, str] | None = None,
              total_label: str = "Total", title: str = "") -> tuple[int, int]:
        """Printable data table: header band, striped rows, optional total row.

        `spans` = report columns per table column (default: even split of the block width);
        `total` = {column key: "SUM" | "MAX" | "MIN" | "AVERAGE" | "=formula"}. Text columns
        (fmt "@") are left aligned, numbers right aligned. Returns the first and last data row.
        """
        if title:
            self.section(title, at=at)
        r, c0, c1 = self._at(at)
        width = c1 - c0 + 1
        if spans is None:
            base = width // len(cols)
            spans = [base + (width - base * len(cols) if j == 0 else 0) for j in range(len(cols))]
        if len(spans) != len(cols) or sum(spans) != width:
            raise ValueError(f"table spans {list(spans)} must give {len(cols)} columns summing to {width}")
        starts = list(accumulate([c0, *spans[:-1]]))

        def put(row: int, j: int, value: Scalar, fmt: str) -> None:
            text = fmt == "@"
            cell = self.ws.cell(row, starts[j] if text else starts[j] + spans[j] - 1, _val(value))
            if not text:
                cell.number_format = fmt
            cell.alignment = Alignment(horizontal="left" if text else "right", vertical="center", indent=1)

        for c in range(c0, c1 + 1):
            self.ws.cell(r, c).style = "ec_rep_th"
        for j, col in enumerate(cols):
            self.ws.cell(r, starts[j], col.header)
        self.ws.row_dimensions[r].height = 18
        r += 1
        first = r
        for i, row in enumerate(rows):
            if len(row) != len(cols):
                raise ValueError(f"table row {i + 1}: {len(row)} values for {len(cols)} columns")
            for c in range(c0, c1 + 1):
                self.ws.cell(r, c).style = "ec_rep_td"
                if i % 2:
                    self.ws.cell(r, c).fill = _fill(C.BLUE_XLT)
            for j, (v, col) in enumerate(zip(row, cols)):
                put(r, j, v, col.fmt)
            r += 1
        last = r - 1
        if total:
            for c in range(c0, c1 + 1):
                self.ws.cell(r, c).style = "ec_rep_total"
            lab = self.ws.cell(r, c0, total_label)
            lab.alignment = Alignment(horizontal="left", vertical="center")
            for j, col in enumerate(cols):
                agg = total.get(col.key)
                if agg:
                    letter = get_column_letter(starts[j] + spans[j] - 1)
                    put(r, j, agg if agg.startswith("=") else f"={agg}({letter}{first}:{letter}{last})", col.fmt)
            r += 1
        self._done(at, r)
        return first, last

    def step(self, key: str, label: str, symbol: str, relation: str, unit: str, *, values: str = "",
             fmt: str = "0.00", dec: int = 2, latex: str = "", source: str = "") -> None:
        """One step of the calculation procedure, as written in a report:

            n.m  Label                                                   source
                 [rendered equation, when latex is given]
                 symbol = relation = substituted values =            value  unit

        `key` names an existing quantity (calc sheet); `values` is a `subst` template.
        """
        if key not in self.book.names:
            raise KeyError(f"step {key!r}: name not defined yet — build the calc sheet first")
        r, c0, c1 = self._at("full")
        self._item += 1
        self.ws.cell(r, c0, f"{self._sec}.{self._item}").style = "ec_unit"
        self.ws.cell(r, c0 + 1, label).style = "ec_rep_step"
        if source:
            src = self.ws.cell(r, c1, source)
            src.style = "ec_source"
            src.alignment = Alignment(horizontal="right", vertical="center")
        r += 1
        if latex:
            r += self._image(_mathtext_png(latex, fontsize=12), r, c0 + 1, None)
        lead = f"{symbol} = " if latex else f"{symbol} = {relation} = "
        lead = '"' + lead.replace('"', '""') + '"'
        line = f"={lead}&{subst(values, dec)}&\" =\"" if values else f"={lead}"
        self.ws.cell(r, c0 + 1, fx(line)).style = "ec_rep_formula"
        res = self.ws.cell(r, c1 - 1, f"={key}")
        res.style = "ec_rep_res"
        res.number_format = fmt
        self.ws.cell(r, c1, unit).style = "ec_unit"
        self._done("full", r + 1, gap=0)

    def check_step(self, key: str, label: str, relation: str = "") -> None:
        """A check or condition as a report step: inequality with numbers, η (or YES / NO), status."""
        rec = self.book.check_keys.get(key)
        if rec is None:
            raise KeyError(f"check_step {key!r}: no check or condition of that name")
        q = quote_sheetname(rec.sheet)
        r, c0, c1 = self._at("full")
        self._item += 1
        self.ws.cell(r, c0, f"{self._sec}.{self._item}").style = "ec_unit"
        self.ws.cell(r, c0 + 1, label).style = "ec_rep_step"
        for c in (c1 - 1, c1):
            self.ws.cell(r, c).style = "ec_rep_status"
        self.ws.cell(r, c1 - 1, f"={q}!$I${rec.row}")
        a, b = get_column_letter(c1 - 1), get_column_letter(c1)
        _status_rules(self.ws, f"{a}{r}:{b}{r}", f"${a}${r}")
        r += 1
        rel = relation.replace('"', '""')
        text = f'="{rel}   →   "&{q}!$G${rec.row}' if relation else f'={q}!$G${rec.row}&""'
        self.ws.cell(r, c0 + 1, text).style = "ec_rep_formula"
        sym = self.ws.cell(r, c1 - 2, f"{rec.symbol or 'η'} =" if rec.numeric else "")
        sym.style = "ec_symbol"
        sym.border = Border()
        res = self.ws.cell(r, c1 - 1, f"={key}" if rec.numeric else f"={q}!$E${rec.row}")
        res.style = "ec_rep_res"
        res.number_format = "0.00"
        self._done("full", r + 1, gap=0)

    def checks(self, *, title: str = "Summary of checks") -> tuple[int, int]:
        """Full-width table of every check and condition defined so far, with η and status."""
        rows = []
        for i, rec in enumerate(self.book.checks, 1):
            q = quote_sheetname(rec.sheet)
            rows.append((i, rec.label, rec.symbol, f'={q}!$G${rec.row}&""',
                         f"={q}!$E${rec.row}" if rec.numeric else f'="{NA}"', f"={q}!$I${rec.row}"))
        first, last = self.table([Col("n", "#", "0"), Col("label", "Check / condition", "@"), Col("sym", "Symbol", "@"),
                                  Col("rel", "Effect vs resistance", "@"), Col("eta", "η [–]", "0.00"),
                                  Col("st", "Status", "@")], rows, spans=(1, 4, 1, 3, 1, 2), title=title)
        a, b = get_column_letter(self.NCOLS), get_column_letter(self.NCOLS + 1)
        _status_rules(self.ws, f"{a}{first}:{b}{last}", f"${a}{first}")
        return first, last

    def equation(self, latex: str, *, at: Place = "full") -> None:
        r, c0, _ = self._at(at)
        self._done(at, r + self._image(_mathtext_png(latex, fontsize=12), r, c0 + 1, None), gap=0)

    def figure(self, png: bytes | str | Path, *, at: Place = "right", width_px: int | None = None,
               caption: str = "") -> None:
        """Small static sketch / drawing (PNG), scaled to the block width unless width_px is given."""
        data = png if isinstance(png, bytes) else Path(png).read_bytes()
        r, c0, c1 = self._at(at)
        r += self._image(data, r, c0, width_px or (c1 - c0 + 1) * self.COL_PX - 8)
        if caption:
            self.ws.cell(r, c0, caption).style = "ec_comment"
            r += 1
        self._done(at, r)

    def chart(self, chart: ScatterChart | BarChart | LineChart, *, at: Place = "right") -> None:
        """Live chart in a block; size it to the block (half width ≈ 9.5 cm, full ≈ 19 cm)."""
        r, c0, _ = self._at(at)
        self.ws.add_chart(chart, f"{get_column_letter(c0)}{r}")
        self._done(at, r + int(chart.height / 0.53) + 1)

    def notes(self, items: Sequence[str], *, title: str = "Assumptions", at: Place = "full") -> None:
        """Lettered notes a) b) … in dark blue italics, wrapped to the block width."""
        r, c0, c1 = self._at(at)
        for c in range(c0, c1 + 1):
            self.ws.cell(r, c).style = "ec_h2"
        self.ws.cell(r, c0, title)
        r += 1
        width = int((c1 - c0) * self.COL_W * 1.25)
        for k, item in enumerate(items):
            letter = self.ws.cell(r, c0, f"{chr(ord('a') + k)})")
            letter.font = _font("C00000", size=9, bold=True)
            letter.alignment = Alignment(horizontal="right", vertical="top")
            for line in textwrap.wrap(item, width) or [""]:
                self.ws.cell(r, c0 + 1, line).style = "ec_rep_note"
                r += 1
        self._done(at, r)

    def signatures(self, roles: Sequence[tuple[str, str]] = (
            ("Prepared by", '=meta_author&""'), ("Checked by", '=meta_checker&""'), ("Approved by", ""))) -> None:
        """Signature boxes across the page: (role, name or formula) — name, line, 'signature · date'."""
        r, c0, c1 = self._at("full")
        w = (c1 - c0 + 1) // len(roles)
        for k, (role, name) in enumerate(roles):
            a = c0 + k * w
            self.ws.cell(r, a, role).style = "ec_meta_label"
            self.ws.cell(r + 1, a, _val(name)).style = "ec_meta"
            for c in range(a, a + w - 1):  # last column of each box is a gap
                self.ws.cell(r + 2, c).border = Border(bottom=_side(C.TEXT))
            self.ws.cell(r + 3, a, "signature · date").style = "ec_comment"
        self.ws.row_dimensions[r + 2].height = 30
        self._done("full", r + 4)

    def close(self) -> None:
        """Call after the last block: print area, A4 portrait, header rows repeated on every page."""
        last = max(self._next.values())
        _page_setup(self.ws, f"A1:{get_column_letter(self.NCOLS + 2)}{last}", title_rows="1:2")


class ScreenSheet(ReportSheet):
    """One-screen calculator (layout S): inputs, sketch, diagrams, status and checks on one page.

    Three zones on an 18-column landscape grid — `left` B–G (inputs), `mid` H–M (sketch,
    charts), `right` N–S (key results, checks) — plus `wide` (H–S) and `full`. The inputs live
    here (yellow, validated, ✔ / ✘ next to each) and the status banner is row 2, so a wrong
    value shows its consequence on the same screen. The logic stays on a calc pad that reads
    the in_* names; this sheet shows results by reference.
    """

    NCOLS, COL_W, COL_PX = 18, 7.0, 50
    SPANS = {"left": (2, 7), "mid": (8, 13), "right": (14, 19), "wide": (8, 19), "full": (2, 19)}
    ZONES = {"left": ("left",), "mid": ("mid",), "right": ("right",), "wide": ("mid", "right"),
             "full": ("left", "mid", "right")}

    def _header(self, title: str, subtitle: str) -> None:
        ws = self.ws
        self._inputs: dict[str, list[int]] = {}  # status column -> input rows
        ws.cell(1, 2, title.upper()).style = "ec_rep_title"
        ident = ws.cell(1, 8, subtitle or '=meta_project&" · "&meta_title&" · rev. "&meta_rev&" · "&meta_author')
        ident.style = "ec_comment"
        org = ws.cell(1, self.NCOLS + 1, '=meta_org&""')
        org.font = _font(DOMAIN_ACCENT[self.book.meta.domain], size=11, bold=True)
        org.alignment = Alignment(horizontal="right", vertical="center")
        ws.row_dimensions[1].height = 30
        for c in range(2, self.NCOLS + 2):
            ws.cell(2, c).style = "ec_banner"
        ws.cell(2, 2, _banner_formula())
        _status_rules(ws, f"B2:{get_column_letter(self.NCOLS + 1)}2", "$B$2")
        ws.row_dimensions[2].height = 24
        ws.freeze_panes = "A3"

    def input(self, key: str, label: str, value: Scalar, unit: str, *, lo: float | None = None,
              hi: float | None = None, choices: str | None = None, fmt: str = "0.00", at: Place = "left") -> Cell:
        """Compact input row: label (with symbol) | yellow value | unit | ✔ / ✘. Bounded like CalcSheet.input."""
        r, c0, c1 = self._at(at)
        ws = self.ws
        for c in range(c0, c1 + 1):
            ws.cell(r, c).style = "ec_rep_label"
        ws.cell(r, c0, label)
        cell = ws.cell(r, c0 + 3, value)
        cell.style = "ec_select" if choices else "ec_input"
        cell.number_format = "@" if choices else fmt
        ref = f"${get_column_letter(c0 + 3)}{r}"
        dv, status, _ = _bounded(self.book, key, label, unit, lo=lo, hi=hi, choices=choices, ref=ref, short=True)
        ws.add_data_validation(dv)
        dv.add(cell.coordinate)
        ws.cell(r, c0 + 4, unit).style = "ec_unit"
        ws.cell(r, c1, status).style = "ec_status"
        stat = get_column_letter(c1)
        _status_rules(ws, f"{stat}{r}", f"${stat}{r}")
        ws.conditional_formatting.add(cell.coordinate, FormulaRule(
            formula=[f'LEFT(${stat}{r},1)="{FAIL}"'], fill=_fill(C.FAIL_FILL), font=Font(color=C.FAIL_FONT, bold=True)))
        self.book.define(key, ws, cell.coordinate)
        self._inputs.setdefault(stat, []).append(r)
        self._done(at, r + 1, gap=0)
        return cell

    def checks(self, *, at: Place = "right", title: str = "Checks") -> tuple[int, int]:  # type: ignore[override]
        """Compact check list: label | η with a data bar | ✔ / ▲ / ✘ (read from the calc sheets)."""
        if title:
            self.section(title, at=at)
        r, c0, c1 = self._at(at)
        first = r
        ws = self.ws
        for rec in self.book.checks:
            q = quote_sheetname(rec.sheet)
            for c in range(c0, c1 + 1):
                ws.cell(r, c).style = "ec_rep_td"
            ws.cell(r, c0, rec.label).alignment = Alignment(horizontal="left", vertical="center")
            ws.cell(r, c1 - 1, f"={q}!$E${rec.row}" if rec.numeric else f'="{NA}"').number_format = "0.00"
            ws.cell(r, c1, f"=LEFT({q}!$I${rec.row},1)").style = "ec_status"
            r += 1
        last = max(r - 1, first)
        e, st = get_column_letter(c1 - 1), get_column_letter(c1)
        _status_rules(ws, f"{st}{first}:{st}{last}", f"${st}{first}")
        ws.conditional_formatting.add(f"{e}{first}:{e}{last}", DataBarRule(
            start_type="num", start_value=0, end_type="num", end_value=1.2, color=C.BLUE, showValue=True))
        self._done(at, r)
        return first, last

    def close(self) -> None:
        """Landscape, the whole calculator on one printed page; registers the input status cells."""
        for col, rows in self._inputs.items():
            self.book.input_spans.append((self.ws.title, min(rows), max(rows), col))
        last = max(self._next.values())
        _page_setup(self.ws, f"A1:{get_column_letter(self.NCOLS + 2)}{last}", title_rows=None, landscape=True)
        self.ws.page_setup.fitToHeight = 1


# --------------------------------------------------------------------------- #
# Charts
# --------------------------------------------------------------------------- #


def xy_chart(title: str, x_title: str, y_title: str,
             series: Sequence[tuple[Block, str, str, str]], *, width: float = 12.0, height: float = 7.0,
             smooth: bool = False, markers: bool = False) -> ScatterChart:
    """Engineering x–y plot. series = (block, x_col, y_col, legend label)."""
    ch = ScatterChart()
    ch.title = title
    ch.style = 13
    ch.x_axis.title = x_title
    ch.y_axis.title = y_title
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.width, ch.height = width, height
    for k, (blk, xc, yc, label) in enumerate(series):
        s = Series(blk.ref(yc), blk.ref(xc), title=label)
        color = C.SERIES[k % len(C.SERIES)]
        s.graphicalProperties.line.solidFill = color
        s.graphicalProperties.line.width = 22000
        s.smooth = smooth
        s.marker.symbol = "circle" if markers else "none"
        ch.series.append(s)
    if len(series) == 1:
        ch.legend = None
    return ch


def sketch_chart(block: Block, x: str, y: str, *, half_range: float, size_cm: float = 6.5,
                 title: str | None = None, color: str = C.NAVY) -> ScatterChart:
    """Parametric drawing: polyline from formula-driven coordinates, equal axes, no axes shown.

    The geometry follows the inputs live (dropdown → new outline), like a CAD sketch.
    """
    ch = ScatterChart()
    ch.title = title
    ch.style = 13
    s = Series(block.ref(y), block.ref(x), title=None)
    s.graphicalProperties.line.solidFill = color
    s.graphicalProperties.line.width = 28000
    s.marker.symbol = "none"
    s.smooth = False
    ch.series.append(s)
    for ax in (ch.x_axis, ch.y_axis):
        ax.scaling.min = -half_range
        ax.scaling.max = half_range
        ax.delete = True
        ax.majorGridlines = None
    ch.legend = None
    ch.width = ch.height = size_cm
    ch.layout = Layout(manualLayout=ManualLayout(x=0.05, y=0.05, w=0.9, h=0.9))
    return ch


LineKind = Literal["outline", "hidden", "axis", "hatch", "dim", "ext", "thin"]

# ISO 128 line types: (colour, width in pt, dash, arrows on both ends)
_LINE: dict[str, tuple[str, float, str | None, bool]] = {
    "outline": (C.NAVY, 2.0, None, False),
    "hidden": (C.NAVY, 0.75, "dash", False),
    "axis": ("C00000", 0.75, "lgDashDot", False),
    "hatch": ("595959", 0.5, None, False),
    "dim": ("262626", 0.75, None, True),
    "ext": ("262626", 0.5, None, False),
    "thin": (C.NAVY, 0.75, None, False),
}


@dataclass(frozen=True)
class DrawSeries:
    """One polyline of a drawing. `label` = cell holding the text shown at point `label_at`."""

    block: Block
    x: str
    y: str
    kind: LineKind = "outline"
    label: str | None = None  # absolute cell reference, e.g. "'92_DrawingData'!$C$5"
    label_at: int = 1
    label_pos: Literal["t", "b", "l", "r", "ctr"] = "t"
    vertical: bool = False


def drawing_chart(items: Sequence[DrawSeries], *, x_range: tuple[float, float], y_range: tuple[float, float],
                  width_cm: float = 16.0, title: str | None = None) -> ScatterChart:
    """Technical drawing as an XY chart: equal scale (height follows the ranges), no axes,
    ISO 128 line types, arrowed dimension lines and dimension texts linked to cells
    (series name shown as a data label — works in Excel and LibreOffice).

    Coordinates are drawing units (paper mm after applying the drawing scale); keep the
    ranges fixed and scale the geometry in the sheet, so the picture never distorts.
    """
    ch = ScatterChart()
    ch.title = title
    ch.style = 13
    ch.legend = None
    for it in items:
        color, width, dash, arrows = _LINE[it.kind]
        s = Series(it.block.ref(it.y), it.block.ref(it.x))
        ln = s.graphicalProperties.line
        ln.solidFill = color
        ln.width = int(width * 12700)
        if dash:
            ln.prstDash = dash
        if arrows:
            ln.headEnd = LineEndProperties(type="triangle", w="sm", len="med")
            ln.tailEnd = LineEndProperties(type="triangle", w="sm", len="med")
        s.marker.symbol = "none"
        s.smooth = False  # LibreOffice smooths the whole chart once any series is smooth
        if it.label:
            s.tx = SeriesLabel(strRef=StrRef(it.label))
            props = RichTextProperties(rot=-5400000 if it.vertical else 0, vert="horz")
            text = RichText(bodyPr=props, p=[Paragraph(
                pPr=ParagraphProperties(defRPr=CharacterProperties(sz=900, b=False, solidFill=C.NAVY)),
                endParaRPr=CharacterProperties())])
            s.dLbls = DataLabelList(dLbl=[DataLabel(idx=it.label_at, showSerName=True, showVal=False,
                                                     showCatName=False, showLegendKey=False, showPercent=False,
                                                     dLblPos=it.label_pos, txPr=text)],
                                    showVal=False, showSerName=False, showCatName=False,
                                    showLegendKey=False, showPercent=False)
        ch.series.append(s)
    for ax, (lo, hi) in ((ch.x_axis, x_range), (ch.y_axis, y_range)):
        ax.scaling.min, ax.scaling.max = lo, hi
        ax.delete = True
        ax.majorGridlines = None
    ch.width = width_cm
    ch.height = width_cm * (y_range[1] - y_range[0]) / (x_range[1] - x_range[0])
    ch.layout = Layout(manualLayout=ManualLayout(layoutTarget="inner", xMode="edge", yMode="edge",
                                                 x=0.0, y=0.0, w=1.0, h=1.0))
    return ch


def _mathtext_png(latex: str, *, fontsize: int = 13, dpi: int = 200) -> bytes:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex}$", fontsize=fontsize, color="#" + C.NAVY)
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def png_from_figure(fig: object, *, dpi: int = 150) -> bytes:
    """matplotlib Figure → PNG bytes for CalcSheet.figure / Dashboard.figure."""
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, bbox_inches="tight", facecolor="white")  # type: ignore[attr-defined]
    return buf.getvalue()


__all__ = [
    "C", "Col", "Meta", "EngWorkbook", "CalcSheet", "DataSheet", "Dashboard", "DrawingSheet", "Block",
    "ReportSheet", "ScreenSheet", "DrawSeries", "fx", "let", "index_match", "interval_lookup", "tol_text", "subst", "xy_chart",
    "sketch_chart", "drawing_chart", "png_from_figure",
]
