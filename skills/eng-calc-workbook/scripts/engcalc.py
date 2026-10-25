"""engcalc — openpyxl builder for engineering calculation workbooks.

One visual language for electrical / mechanical / civil calc sheets:
title block -> status banner -> inputs -> calculation steps -> limit checks
-> results, plus an auto-generated check register (80_Kontroly), README with
colour legend, named ranges for every quantity and print-ready A4 setup.

Requires: openpyxl>=3.1, Pillow; matplotlib only for equation()/figure().
"""
from __future__ import annotations

import datetime as dt
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Sequence, Union

from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.drawing.image import Image as XLImage
from openpyxl.formatting.rule import DataBarRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, NamedStyle, PatternFill, Protection, Side
from openpyxl.utils import absolute_coordinate, get_column_letter, quote_sheetname
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

Scalar = Union[int, float, str, dt.date, None]
Domain = Literal["electrical", "mechanical", "civil", "general"]
CheckKind = Literal["le", "ge"]

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
    CHECKS = "80_Kontroly"
    README = "00_README"

    def __init__(self, meta: Meta) -> None:
        self.meta = meta
        self.wb = Workbook()
        for st in _style_defs():
            self.wb.add_named_style(st)
        self.names: dict[str, str] = {}  # name -> sheet title
        self.checks: list[CheckRecord] = []
        self.input_spans: dict[str, tuple[int, int]] = {}
        self.sheet_purpose: dict[str, str] = {}
        self._util_chart_requests: list[tuple[Worksheet, str, float, float]] = []
        self._readme = self.wb.active
        self._readme.title = self.README
        self._readme.sheet_properties.tabColor = TAB["readme"]
        self._checks_ws = self.wb.create_sheet(self.CHECKS)
        self._checks_ws.sheet_properties.tabColor = TAB["checks"]
        self.sheet_purpose[self.CHECKS] = "Registr všech posudků a podmínek, souhrnný stav, mez varování η"
        self._init_readme_meta()
        self._init_checks_config()

    # -- names ------------------------------------------------------------- #
    def define(self, name: str, ws: Worksheet, coord: str) -> None:
        _check_name(name)
        if name in self.names:
            raise ValueError(f"duplicate defined name {name!r}")
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

    # -- README ------------------------------------------------------------ #
    _META_ROWS = (
        ("meta_project", "Projekt", "project"),
        ("meta_title", "Výpočet", "title"),
        ("meta_subject", "Předmět", "subject"),
        ("meta_org", "Organizace", "organisation"),
        ("meta_std", "Norma / metodika", "standard"),
        ("meta_author", "Zpracoval", "author"),
        ("meta_checker", "Kontroloval", "checker"),
        ("meta_rev", "Revize", "revision"),
        ("meta_date", "Datum", "date"),
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
        ws["B2"] = "README · popis sešitu, rozsah platnosti, legenda, revize"
        ws["B2"].style = "ec_comment"
        self._section(ws, 4, "Identifikace výpočtu")
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

        para("Účel", [purpose], bullet="")
        para("Rozsah platnosti", scope)
        para("Předpoklady a omezení (mimo rozsah = nepoužívat)", assumptions)
        para("Postup práce", [f"{i}. {s}" for i, s in enumerate(workflow, 1)], bullet="")

        self._section(ws, r, "Legenda buněk")
        r += 1
        legend = (
            ("ec_input", 12.5, "Ruční vstup — jediné buňky, do kterých se zapisuje (odemčené)"),
            ("ec_select", "S235", "Výběr ze seznamu (ověření dat → číselník)"),
            ("ec_const", 1.35, "Konstanta / hodnota z normy — neměnit bez revize"),
            ("ec_calc", 42.0, "Vzorec na tomtéž listu"),
            ("ec_link", 42.0, "Vzorec čerpající z jiného listu (pojmenovaná oblast)"),
            ("ec_aux", 0.25, "Pomocný mezivýpočet"),
            ("ec_result", 99.9, "Klíčový výsledek"),
        )
        for style, sample, text in legend:
            ws.cell(r, 2).value = sample
            ws.cell(r, 2).style = style
            ws.cell(r, 3, text).style = "ec_label"
            r += 1
        for status, text in (
            (f"{OK} VYHOVUJE", "Podmínka splněna, η ≤ mez varování"),
            (f"{WARN} VYHOVUJE – malá rezerva", "mez varování < η ≤ 1,00"),
            (f"{FAIL} NEVYHOVUJE", "η > 1,00, nesplněná podmínka nebo vstup mimo rozsah"),
        ):
            c = ws.cell(r, 2, status)
            c.style = "ec_status"
            _status_rules(ws, c.coordinate, f"${get_column_letter(2)}{r}")
            ws.cell(r, 3, text).style = "ec_label"
            r += 1
        r += 1

        self._section(ws, r, "Obsah sešitu")
        r += 1
        for ws_ in self.wb.worksheets:
            if ws_.title == self.README:
                continue
            c = ws.cell(r, 2, f'=HYPERLINK("#{quote_sheetname(ws_.title)}!A1","{ws_.title}")')
            c.font = _font(C.BLUE, bold=True)
            ws.cell(r, 3, self.sheet_purpose.get(ws_.title, "")).style = "ec_label"
            r += 1
        r += 1
        para("Zdroje", sources)

        self._section(ws, r, "Revizní log")
        r += 1
        heads = ("Datum", "Revize", "Změna", "Zpracoval", "Kontroloval")
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
        _scaffold(self, ws, "Registr posudků", columns=False)
        ws.cell(8, COL["label"], "Mez varování η (nad ní ▲ malá rezerva)").style = "ec_label"
        ws.cell(8, COL["sym"], "η_warn =").style = "ec_symbol"
        c = ws.cell(8, COL["val"], 0.9)
        c.style = "ec_input"
        c.number_format = "0.00"
        dv = DataValidation(type="decimal", operator="between", formula1="0.5", formula2="1",
                            showErrorMessage=True, errorTitle="Mimo rozsah",
                            error="Zadej 0,50 … 1,00", promptTitle="η_warn", prompt="0,50 … 1,00")
        ws.add_data_validation(dv)
        dv.add(c.coordinate)
        ws.cell(8, COL["unit"], "–").style = "ec_unit"
        self.define("cfg_eta_warn", ws, c.coordinate)

    def _build_checks(self) -> None:
        ws = self._checks_ws
        heads = ("#", "Posudek / podmínka", "Symbol", "η [–]", "Stav", "List", "Odkaz", "fail", "warn")
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
        for sheet, (a, b) in self.input_spans.items():
            q = quote_sheetname(sheet)
            status = (f'=IF(COUNTIF({q}!$I${a}:$I${b},"{FAIL}*")=0,"{OK} všechny vstupy v mezích",'
                      f'"{FAIL} vstupy mimo rozsah: "&COUNTIF({q}!$I${a}:$I${b},"{FAIL}*"))')
            rows.append((f"Vstupy listu {sheet} v povolených mezích", "", f'="{NA}"', status, f"{sheet}|{a}"))
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
            ws.cell(r, 8, f'=HYPERLINK("#{quote_sheetname(sheet)}!C{row}","→ ř. {row}")').font = _font(C.BLUE)
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
        ws.cell(r + 1, 3, "η = využití (poměr účinek / odolnost); fail/warn = příznaky pro souhrnný stav").style = "ec_comment"
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
        ws.cell(10, lim_col, "mez").style = "ec_colhead"
        for r in range(first, first + n_numeric):
            ws.cell(r, lim_col, 1).style = "ec_const"
        for target, anchor, w, h in self._util_chart_requests:
            bar = BarChart()
            bar.type = "bar"
            bar.style = 2
            bar.title = "Využití posudků η"
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
    ws.cell(2, b, "Inženýrský výpočet").font = _font("FFFFFF", size=9)
    ws.cell(3, b, "=meta_std&\"\"").font = _font("FFFFFF", size=8, italic=True)
    ws.cell(4, b, '="Revize "&meta_rev').font = _font("FFFFFF", size=8)
    meta(1, d, "Projekt", e, "=meta_project&\"\"", g)
    meta(2, d, "Výpočet", e, "=meta_title&\"\"", g)
    ws.cell(2, e).font = _font(C.NAVY, size=12, bold=True)
    meta(3, d, "List", e, f'="{title}"', g)
    meta(4, d, "Předmět", e, "=meta_subject&\"\"", g)
    meta(1, h, "List č.", i, fx('=SHEET()&" / "&SHEETS()'), i)
    meta(2, h, "Datum", i, "=meta_date", i)
    ws.cell(2, i).number_format = "yyyy-mm-dd"
    meta(3, h, "Zpracoval", i, "=meta_author&\"\"", i)
    meta(4, h, "Kontroloval", i, "=meta_checker&\"\"", i)
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
    banner = ws.cell(5, b, (
        f'=IF(SUM(chk_fail)>0,"{FAIL} NEVYHOVUJE – počet nesplněných podmínek: "&SUM(chk_fail),'
        f'IF(SUM(chk_warn)>0,"{WARN} VYHOVUJE S MALOU REZERVOU – posudků: "&SUM(chk_warn),'
        f'"{OK} VŠECHNY POSUDKY A PODMÍNKY VYHOVUJÍ"))'
        f'&"     η max = "&IF(COUNT(chk_eta)>0,FIXED(MAX(chk_eta),2),"{NA}")'
    ))
    for col in range(b, i + 1):
        ws.cell(5, col).style = "ec_banner"
    _status_rules(ws, f"{get_column_letter(b)}5:{get_column_letter(i)}5", f"${get_column_letter(b)}$5")
    del banner
    ws.cell(6, b, (
        "Zadávej jen do žlutých buněk (modré písmo) · modrozelené = výběr ze seznamu · fialové = hodnota z normy · "
        f"{OK} vyhovuje  {WARN} malá rezerva  {FAIL} nevyhovuje"
    )).style = "ec_comment"
    if columns:
        for key, text in (("id", "#"), ("label", "Veličina"), ("sym", "Symbol"), ("val", "Hodnota"),
                          ("unit", "Jedn."), ("text", "Vztah / podmínka"), ("src", "Zdroj / norma"),
                          ("stat", "Mez / stav")):
            ws.cell(HEADER_ROWS, COL[key], text).style = "ec_colhead"
        ws.freeze_panes = ws.cell(HEADER_ROWS + 1, 1)


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
    ws.oddFooter.right.text = "&8Strana &P / &N"
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
              fmt: str = "0.00", source: str = "zadání") -> Cell:
        """Manual input. Numeric inputs need lo/hi; selection inputs need a list name (lst_*)."""
        self._row_frame(label, symbol, unit, source)
        cell = self._cell("val", value, "ec_select" if choices else "ec_input")
        cell.number_format = fmt if not choices else "@"
        ref = f"${get_column_letter(COL['val'])}{self.r}"
        if choices:
            if choices not in self.book.names:
                raise KeyError(f"list name {choices!r} not defined yet (DataSheet.table first)")
            dv = DataValidation(type="list", formula1=f"={choices}", allow_blank=False, showErrorMessage=True,
                                errorTitle="Neplatná volba", error="Vyber hodnotu ze seznamu",
                                promptTitle=symbol or label[:30], prompt="Výběr ze seznamu", showInputMessage=True)
            self._cell("text", "výběr ze seznamu", "ec_comment")
            status = f'=IF(ISNUMBER(MATCH({ref},{choices},0)),"{OK} ze seznamu","{FAIL} není v seznamu")'
        elif lo is not None and hi is not None:
            if lo > hi:
                raise ValueError(f"{key}: lo > hi")
            dv = DataValidation(type="decimal", operator="between", formula1=repr(float(lo)), formula2=repr(float(hi)),
                                showErrorMessage=True, errorTitle="Mimo rozsah platnosti",
                                error=f"{symbol or label}: povoleno {lo:g} … {hi:g} {unit}",
                                promptTitle=(symbol or label)[:32], prompt=f"{lo:g} … {hi:g} {unit}",
                                showInputMessage=True)
            self._cell("text", f"⟨{lo:g} ; {hi:g}⟩ {unit}", "ec_comment")
            status = (f'=IF(AND(ISNUMBER({ref}),{ref}>={lo!r},{ref}<={hi!r}),'
                      f'"{OK} v mezích","{FAIL} mimo rozsah")')
        else:
            raise ValueError(f"input {key!r} needs lo/hi or choices — every input must be bounded")
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
            f'=IF(NOT(ISNUMBER({e})),"{FAIL} NELZE VYHODNOTIT",IF({e}>1,"{FAIL} NEVYHOVUJE",'
            f'IF({e}>cfg_eta_warn,"{WARN} VYHOVUJE – malá rezerva","{OK} VYHOVUJE")))'
        ), "ec_status")
        self.book.define(key, self.ws, cell.coordinate)
        self.book.checks.append(CheckRecord(self.ws.title, self.r, label, symbol, True))
        self.r += 1
        return cell

    def condition(self, key: str, label: str, condition: str, *, ok: str, fail: str,
                  text: str = "", source: str = "") -> Cell:
        """Boolean validity condition (scope of the method, regime, required assumption)."""
        cond = fx(condition)[1:]
        self._row_frame(label, "", "", source)
        self._cell("val", f'=IF({cond},"ANO","NE")', "ec_calc")
        if text:
            self.ws.cell(self.r, COL["text"], text)
        cell = self._cell("stat", f'=IF({cond},"{OK} {ok}","{FAIL} {fail}")', "ec_status")
        self.book.define(key, self.ws, cell.coordinate)
        self.book.checks.append(CheckRecord(self.ws.title, self.r, label, "", False))
        self.r += 1
        return cell

    def remark(self, label: str, formula: str) -> Cell:
        """Dynamic engineering remark (regime / interpretation), e.g. IF(Re>4000,"turbulentní",…)."""
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
            self.book.input_spans[self.ws.title] = (self._in_first, self._in_last)
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
        ws.cell(self.r + 1, 2, f"Zdroj: {source}").style = "ec_source"
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
    "C", "Col", "Meta", "EngWorkbook", "CalcSheet", "DataSheet", "Dashboard", "Block",
    "fx", "let", "index_match", "xy_chart", "sketch_chart", "png_from_figure",
]
