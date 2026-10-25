"""verify — recalculate, lint and (optionally) render an engineering calc workbook.

    python verify.py book.xlsx [--render out_dir] [--json]

Exit codes: 0 clean · 1 lint warnings only · 2 formula errors or unreadable file.
Engineering check results (✘ FAILS) are reported, not treated as lint failures.
Needs LibreOffice (soffice) on PATH for recalculation / rendering.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import warnings

from openpyxl import load_workbook

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

ERRORS = ("#DIV/0!", "#NAME?", "#REF!", "#VALUE!", "#N/A", "#NUM!", "#NULL!", "Err:")
VOLATILE = re.compile(r"(?<![\w.])(INDIRECT|OFFSET|NOW|TODAY|RAND|RANDBETWEEN|CELL|INFO)\s*\(", re.I)
FOREIGN_ADDR = re.compile(r"(?:'[^']+'|[A-Za-z0-9_]+)!\$?[A-Z]{1,3}\$?\d+")
NUMBER = re.compile(r"(?<![A-Za-z_$\d.])(\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)(?![\d.])")
SCIENTIFIC = re.compile(r"(?<![A-Za-z_$\d.])\d+(?:\.\d+)?[eE][-+]?\d+(?![\d.])")
ALLOWED_LITERALS = {"0", "1", "2", "3", "4", "10", "100", "1000", "0.5", "1e3", "1e6", "1e-3", "1e-6", "1E3", "1E6", "1E-6"}
CALC_STYLES = {"ec_calc", "ec_result", "ec_link", "ec_aux"}
INPUT_STYLES = {"ec_input", "ec_select"}
TEXT_COL = 7
GENERATED_SHEETS = {"00_README", "80_Checks"}  # built by engcalc itself; column G "Relation / condition" documents coefficients


@dataclass
class Finding:
    level: str  # error | warn | info
    where: str
    what: str


def recalc(src: Path, workdir: Path) -> Path:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("LibreOffice (soffice) not found on PATH")
    profile = workdir / "lo_profile"
    cmd = [soffice, f"-env:UserInstallation={profile.as_uri()}", "--headless", "--calc",
           "--convert-to", "xlsx", "--outdir", str(workdir / "recalc"), str(src)]
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    out = workdir / "recalc" / src.name
    if not out.exists():
        raise RuntimeError(f"recalculation produced no file: {cmd}")
    return out


def render(src: Path, out_dir: Path, workdir: Path) -> list[Path]:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice or not shutil.which("pdftoppm"):
        raise RuntimeError("render needs soffice and pdftoppm")
    out_dir.mkdir(parents=True, exist_ok=True)
    profile = workdir / "lo_profile"
    subprocess.run([soffice, f"-env:UserInstallation={profile.as_uri()}", "--headless", "--convert-to", "pdf",
                    "--outdir", str(out_dir), str(src)], check=True, capture_output=True, timeout=180)
    pdf = out_dir / (src.stem + ".pdf")
    subprocess.run(["pdftoppm", "-png", "-r", "70", str(pdf), str(out_dir / src.stem)], check=True, timeout=180)
    return sorted(out_dir.glob(f"{src.stem}*.png"))


def lint(path: Path) -> list[Finding]:
    wb = load_workbook(path)
    out: list[Finding] = []
    for ws in wb.worksheets:
        generated = ws.title in GENERATED_SHEETS
        sheet_doc = " ".join(str(c.value) for row in ws.iter_rows() for c in row
                             if c.style in ("ec_source", "ec_comment") and isinstance(c.value, str))
        if ws.sheet_state != "visible":
            out.append(Finding("warn", ws.title, "hidden sheet — nobody reviews what is hidden"))
        validated: set[str] = set()
        for dv in ws.data_validations.dataValidation:
            for rng in dv.sqref.ranges:
                for row in ws.iter_rows(min_row=rng.min_row, max_row=rng.max_row,
                                        min_col=rng.min_col, max_col=rng.max_col):
                    validated.update(c.coordinate for c in row)
        for row in ws.iter_rows():
            for c in row:
                style = c.style
                where = f"{ws.title}!{c.coordinate}"
                if generated:
                    continue
                if style in INPUT_STYLES and c.coordinate not in validated:
                    out.append(Finding("warn", where, "input without data validation"))
                if not (isinstance(c.value, str) and c.value.startswith("=")):
                    if style in CALC_STYLES and c.value not in (None, ""):
                        out.append(Finding("warn", where, f"hard-coded value in a calculation cell: {c.value!r}"))
                    continue
                f = c.value
                if VOLATILE.search(f) and ws.title != "00_README":
                    out.append(Finding("warn", where, "volatile function"))
                if style in CALC_STYLES:
                    if FOREIGN_ADDR.search(f):
                        out.append(Finding("warn", where, "reference to a cell on another sheet — use a named range"))
                    doc = str(ws.cell(c.row, TEXT_COL).value or "") + " " + sheet_doc
                    body = re.sub(r'"[^"]*"', "", f)
                    sci = SCIENTIFIC.findall(body)  # 1e-6 before names are stripped (the e would go)
                    body = SCIENTIFIC.sub("", body)
                    body = re.sub(r"[A-Za-z_][A-Za-z0-9_.]*\d*", "", body)
                    for lit in sci + NUMBER.findall(body):
                        if lit not in ALLOWED_LITERALS and lit not in doc:
                            out.append(Finding("warn", where, f"magic number {lit} (not documented in the Relation column)"))
        for rng in ws.merged_cells.ranges:
            out.append(Finding("info", f"{ws.title}!{rng}", "merged cells"))
    return out


def scan(path: Path) -> tuple[list[Finding], list[tuple[str, str, str]], str]:
    wb = load_workbook(path, data_only=True)
    errs: list[Finding] = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith(ERRORS):
                    errs.append(Finding("error", f"{ws.title}!{c.coordinate}", c.value))
    checks: list[tuple[str, str, str]] = []
    banner = ""
    if "80_Checks" in wb.sheetnames:
        ws = wb["80_Checks"]
        banner = str(ws["B5"].value or "")
        for r in range(11, ws.max_row + 1):
            label, status = ws.cell(r, 3).value, ws.cell(r, 6).value
            if label and status:
                eta = ws.cell(r, 5).value
                checks.append((str(label), f"{eta:.2f}" if isinstance(eta, (int, float)) else str(eta), str(status)))
    return errs, checks, banner


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workbook", type=Path)
    ap.add_argument("--render", type=Path, help="directory for PDF + PNG pages")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.workbook.exists():
        print(f"not found: {args.workbook}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        findings = lint(args.workbook)
        try:
            calc = recalc(args.workbook, work)
        except (RuntimeError, subprocess.SubprocessError) as exc:
            print(f"recalc failed: {exc}", file=sys.stderr)
            return 2
        errs, checks, banner = scan(calc)
        pages = render(calc, args.render, work) if args.render else []
    findings = errs + findings
    if args.json:
        print(json.dumps({"banner": banner, "checks": checks, "findings": [asdict(f) for f in findings],
                          "pages": [str(p) for p in pages]}, ensure_ascii=False, indent=2))
    else:
        print(f"BANNER: {banner}")
        for label, eta, status in checks:
            print(f"  {eta:>6}  {status:<34} {label}")
        for f in findings:
            print(f"[{f.level}] {f.where}: {f.what}")
        for p in pages:
            print(f"page: {p}")
        n = {lvl: sum(f.level == lvl for f in findings) for lvl in ("error", "warn", "info")}
        print(f"errors={n['error']} warnings={n['warn']} info={n['info']}")
    if any(f.level == "error" for f in findings):
        return 2
    return 1 if any(f.level == "warn" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
