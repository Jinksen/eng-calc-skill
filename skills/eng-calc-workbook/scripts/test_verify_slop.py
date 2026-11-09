"""Self-check for the Restraint lint in verify.py: a sloppy sheet must raise every sign, a plain one none.

    python test_verify_slop.py
"""
import sys
import tempfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, GradientFill, PatternFill

sys.path.insert(0, str(Path(__file__).parent))
import verify  # noqa: E402

wb = Workbook()
ws = wb.active
ws.title = "Calc 📊"
ws.sheet_properties.tabColor = "4472C4"
ws["B2"] = "Smart Beam Calculator ✨"
ws["B3"] = "Check passed!"
ws["B4"] = "12.5 kN"
ws["B5"].fill = PatternFill("solid", fgColor="ED7D31")
ws["B6"].font = Font(color="A5A5A5")
ws["B7"].fill = GradientFill(stop=("FFFFFF", "1F3864"))
ws["B8"] = 1.5
ws["B8"].number_format = "0.000000"
for r in range(10, 70):
    ws.cell(r, 2, r).fill = PatternFill("solid", fgColor="FFF2CC")
bar = BarChart()
bar.add_data(Reference(ws, min_col=2, min_row=10, max_row=20))
bar.series[0].graphicalProperties.solidFill = "ED7D31"
ws.add_chart(bar, "D2")
clean = wb.create_sheet("Clean")
clean["B2"] = "BENDING CHECK"
clean["C2"] = "✔ OK"
clean["D2"] = 12.5
clean["E2"] = "kN"
clean["F2"] = "Sheet protection: inputs unlocked"
clean["B3"].fill = PatternFill("solid", fgColor="FFF2CC")

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "slop.xlsx"
    wb.save(path)
    found = verify.lint(path)

slop = [f.what for f in found if f.where.startswith("Calc")]
expected = ["emoji in sheet name", "tab colour 4472C4", "emoji in text", "marketing word 'Smart'",
            "exclamation mark", "number typed as text", "fill colour ED7D31", "font colour A5A5A5", "gradient fill",
            "decimals", "of cells filled", "legend on a single series", "series colour ED7D31"]
missing = [e for e in expected if not any(e in w for w in slop)]
noise = [f"{f.where}: {f.what}" for f in found if f.where.startswith("Clean")]
assert not missing, f"not flagged: {missing}"
assert not noise, f"false positives: {noise}"
print(f"ok — {len(slop)} slop findings, clean sheet quiet")
