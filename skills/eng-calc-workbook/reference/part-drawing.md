# Parametric part drawing in Excel

Goal: a section / view of a part (flange, shaft, bush, beam section, plate with holes) that
**redraws when the dimensions change** and carries tolerances, GD&T and a title block. The
drawing complements the calculation; it does not replace CAD. Values on the drawing are always
linked to cells: dimension = `in_*`, tolerance = `calc_T_*` / `tol_*`, limits = `calc_*`.

Reference build: `scripts/example_flange.py` (flange with hub — section A–A with hatching,
view B with the bolt pattern, ISO 286 fit, ISO 2768, tolerance chain, GD&T, title block,
automatic scale).

## 1. Drawing data (`92_DrawingData`)

| Block | Content | How |
|---|---|---|
| outline polygons | each closed outline as a list of (x, y) in paper mm; last point = first | points computed from the dimensions: `=calc_ox+(in_t)*calc_sc`… |
| hatching | 45° lines clipped to rectangles | `DataSheet.hatch()` (§3) |
| centre lines | part axis, hole axes, pitch circle | 2 points overshooting the outline by `c_ov` |
| dimensions | extension lines (4 points) + dimension line (3 points, middle one carries the text) | offsets from the outline in paper mm `c_off` |
| circles, holes | `x = xc + r·cos a`, `y = yc + r·sin a`, angles as constants (72 segments) | straight segments — LibreOffice smooths **every** series of a chart once one series is smooth, which rounds the outline corners |
| texts | dimension texts and view titles as formulas | `="Ø"&FIXED(in_D,0)&" ±"&FIXED(calc_T_D,1)` |

**Coordinates**: model mm → paper mm with `x_p = calc_ox + x·calc_sc`, `y_p = y·calc_sc`.
The chart axes stay **fixed** (the drawing area, e.g. 200 × 150 mm) and the geometry is scaled
in the sheet — so the picture never distorts and the scale is real.

**Automatic scale** (ISO 5455): `calc_sc_need = MIN((W − 6a)/(L + D); (H − 4a)/D)` (the space
for the views plus dimension rows), then the largest standard scale ≤ need:
`INDEX(db_scale_f; MATCH(MAX(need; MIN(db_scale_f)); db_scale_f; 1))` with factors ascending
(1:10 … 5:1). The scale text goes into the view title and the title block; a `condition` reports
when even 1:10 does not fit.

**Rotationally symmetric part**: draw the upper half and mirror it (`y → −y`) into separate
series. A section through holes: the hole splits the flange into a web and a rim — two polygons
per half. For an odd number of holes the lower hole is rotated into the cutting plane
(ISO 128-44 convention, note it in the README).

**Names are case-insensitive**: `in_D` and `in_d` are the same name in Excel — use
`in_D` / `in_dbore` / `in_dhole`. `engcalc.define()` refuses such collisions, also for
generated `gd_*` names (block keys `od`, `bore`, not `D`, `d`).

## 2. Drawing chart (`drawing_chart`)

- **XY scatter with straight lines, no markers**, one series per polyline. No gaps inside a
  series: Excel connects across `#N/A` in scatter charts, so every separate line is its own series.
- **Equal scale**: fixed axis limits, chart height = width × (y range / x range), plot area
  fills the chart (manual inner layout), axes, gridlines and legend hidden.
- Line types per ISO 128 (`_LINE` in `engcalc.py`): outline solid 2 pt NAVY, centre lines
  long dash-dot red, hatching 0.5 pt grey, dimension lines 0.75 pt with arrows at both ends,
  extension lines 0.5 pt.
- **Dimension texts**: the dimension series takes its **name from a cell**
  (`DrawSeries(label="'92_DrawingData'!$B$40")`) and shows it as a data label at the middle
  point — position `l`/`r` and rotation 90° for vertical dimensions, `t`/`b` for horizontal
  ones. Works in Excel and LibreOffice (openpyxl cannot write *Value From Cells*).
- View titles ("SECTION A–A 1:1", "VIEW B") = a one-point series with a label.
- Section fill: the chart cannot fill a polygon → hatching (§3), or in path A a *Freeform*
  shape below the chart.
- Live highlight: a check ✘ can colour the dimension text (prefix "✘ " in the text formula) or
  add a series "dimensions out of tolerance" with points `=IF(status="✘";x;NA())`.

## 3. Hatching (`DataSheet.hatch`)

The section is split into rectangles; each rectangle is one series. Lines `y = x + k` for
`k` from `kmin = y0 − x1` to `kmax = y1 − x0`, step `s = MAX(c_hatch; (kmax − kmin)/n)`.
Each line is clipped (`xl = MAX(x0; y0 − k)`, `xu = MIN(x1; y1 − k)`), drawn there and back,
and the move to the next line runs **along two edges of the rectangle**:

- `side="lower"` — along the bottom and left edges (corner point = min x, min y),
- `side="upper"` — along the top and right edges (corner point = max x, max y).

Choose the side whose edges are **visible outline**, not an edge shared with the neighbouring
rectangle — the moves then hide under the thick outline. Flange example (upper half): hub strip
`x 0…L, y d/2…D_h/2` → `lower` (bore + left face), web `x 0…t, y D_h/2…(D_k−d_h)/2` → `upper`
(hole edge + right face), rim → either. Lower half mirrored: hub `upper`, web `lower`.
Same hatch direction in all rectangles of one part.

## 4. Dimensions and tolerances

| Row | Content | Formula / source |
|---|---|---|
| nominal size | input | `in_dbore` |
| ISO 286 | IT grade by size range | `interval_lookup("db_iso286_IT7";"db_iso286_key";"in_dbore")` |
| hole H | `EI = 0`, `ES = EI + IT` | const + calc |
| shaft field | fundamental deviation from the table column of the field; f, g, h give `es`, k, p give `ei`; the other one ± IT | `INDEX(CHOOSE(col;db_f;db_g;…);row)` |
| ISO 2768 (general) | untoleranced sizes by class `f/m/c` | `interval_lookup(CHOOSE(calc_gcol;db_gen_f;db_gen_m;db_gen_c); db_gen_key; x)` |
| limits | max / min | `=in_dbore+calc_ES_hole/1000` |
| dimension text | `40.5 ±0.1` / `+0.021/0` | `tol_text(upper; lower; dec)` |
| fit | clearance min / max, type | `s_max = ES − ei`, `s_min = EI − es`; `condition` s_min ≥ required, `check` s_max ≤ allowed |

Size ranges in ISO tables are "over a up to b": a size exactly on a bound belongs to the lower
range — `MATCH(x;bounds;1)` gets that wrong, `COUNTIF(bounds;"<"&x)+1` gets it right.

**Tolerance chain** (stack-up) as checks: closing dimension `A0 = Σ increasing − Σ decreasing`;
**worst case** `T0 = ΣT_i`, **statistical** `T0 = √(ΣT_i²)` (RSS, assumes a normal distribution
→ remark / `condition`). Checks `A0 − T0 ≥ A0,min` (`ge` with `MAX(x;1e-6)`) and
`A0 + T0 ≤ A0,max`.

The drawing shows both deviations; the manufacturing min / max belong to the results.

## 5. Geometrical tolerances (GD&T, ISO 1101)

Feature control frame = 3 boxed cells (`DrawingSheet.gdt_frame`): `symbol | value | datum`,
value as a formula from an input (`=FIXED(in_gt_perp,2)`). Unicode symbols:

| Characteristic | Sign | Characteristic | Sign |
|---|---|---|---|
| straightness | ⏤ | parallelism | ∥ |
| flatness | ⏥ | perpendicularity | ⊥ |
| roundness | ○ | angularity | ∠ |
| cylindricity | ⌭ | position | ⌖ |
| profile of a line / surface | ⌒ / ⌓ | concentricity | ◎ |
| run-out / total | ↗ / ⌰ | symmetry | ⌯ |

Datum letters (`A`) in the dimension text of the datum feature or as a framed letter. A
position tolerance of a hole pattern can be checked against the clearance of the fastener
(floating fastener `T = H − F`, ISO 2692) — `check`.

## 6. Title block (ISO 7200)

Block of cells below the drawing (`DrawingSheet.title_block`), no merging: part name, drawing
number, material, scale, general tolerances (ISO 2768-mK), edges (ISO 13715), projection method,
mass, drawn / checked with date, revision. All values from `meta_*`, `in_*`, `out_*` — the title
block is never filled in by hand. Dates as text `YEAR()&"-"&RIGHT("0"&MONTH(),2)…` (locale-safe).

## 7. Typical checks for a part

`check`: minimum wall thickness ≥ t_min; edge distance and ligament between holes ≥ k·d_h;
room for the washer; clearance of the fit within limits; tolerance chain; mass ≤ m_max
(volume of a rotational part from cylinders, or Pappus `V = 2π·x̄·A`); position tolerance ≤
fastener clearance.
`condition`: size within the ISO 286 / ISO 2768 table; geometry consistent (holes do not cut the
hub or the rim); a standard scale fits.

## 8. Paths

| | Path A (Claude in Excel / manual) | Path B (`engcalc.py`) |
|---|---|---|
| outline, dimensions, centre lines, hatching | XY chart (all of it) | `gd.block()` polygons, `gd.hatch()`, `drawing_chart()` |
| section fill, GD&T frames, datum triangles | shapes (Insert → Shapes), text linked to a cell | openpyxl **cannot create shapes** → cell frames (`gdt_frame`) + hatching |
| title block | cells | `title_block()` |

Done when changing any dimension redraws the outline, hatching, texts and scale, the dimension
texts show the deviations, and a check out of tolerance turns the banner red.
