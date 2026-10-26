# Calculation specification — what the engineer must tell you

SKILL.md §1 lists the items of the specification. This file covers the items that decide
whether the result is **right**, not how it looks: where the limits come from, which edition
of which standard, the safety concept, the cases, the conventions, how trustworthy the inputs
are, and how measured data are judged. They apply to every field. A workbook built without
them can be internally consistent and still wrong.

## How to ask

- Ask in the groups below, not item by item. With `AskUserQuestion`: one group per call, up to
  4 questions, your proposed default first and marked *(Recommended)*.
- **M** = mandatory (nothing is built without an answer), **O** = optional (ask only when it
  applies, otherwise write the default into the README).
- What the user cannot answer now becomes an **assumption to confirm** (§6), never a silent
  default.
- Every answer has a home in the workbook (column "Lives in"). An answer that only lives in the
  chat is lost.

| § | Group | M / O | Lives in |
|---|---|---|---|
| 1 | Requirements and their origin | M | `00_README` → Requirements; IDs in check labels |
| 2 | Normative basis | M | `00_README` → Normative basis; NDPs as `const` rows |
| 3 | Safety concept | M | `00_README` → Safety concept; factors as `const` rows; `cfg_eta_warn` |
| 4 | Cases and the governing case | M (a single case is an answer too) | case table, envelope check rows |
| 5 | Sign convention and coordinate system | M where signs or directions matter | `00_README` → Conventions; axis arrows on the sketch |
| 6 | Status of input data | M | col. H of every input; assumption register |
| 7 | Uncertainty and tolerances of inputs | O | tolerance rows, extra cases |
| 8 | Test / measurement report | O (when measured data are judged) | instrument table, decision rule, acceptance rows |

Done when every **M** group has an answer or an assumption to confirm, and each answer has its
place in the workbook.

## 1. Requirements and their origin

A check has two sides, and the limit side does not always come from a standard. It can come
from a contract, the client's technical specification, an internal company rule, a regulation
or a product datasheet, and that limit is often stricter than the standard.

Ask: *Which requirements must the result satisfy, and who sets each one?* Collect them as a
table on `00_README`:

| ID | Requirement | Origin | Limit | Checked by |
|---|---|---|---|---|
| R01 | the requirement in words | standard + clause / contract no. / client spec rev. / internal rule | value + unit, or the rule | name of the check (`chk_…`) |

Rules:

- A project limit stricter than the standard wins. Cite **both** in col. H of the check:
  `R03 · client spec TS-12 §4.2 (EN … §6.2.5 allows more)`.
- The limit is an `input` (project value) or a `const` (from a standard), never a number inside
  the check formula.
- Put the requirement ID in brackets at the end of the check label, e.g. `Deflection (R03)`.
  The register then carries the ID with no extra column.
- **Coverage**: in the requirement table, column "Checked by" gets a status:
  `=IF(COUNTIF(<register Check column>,"*("&B12&")*")>0,"✔ checked","✘ no check")`.
  Name the status range `req_status` and add one row to the register: condition
  `COUNTIF(req_status,"✘*")=0`, ok `all requirements checked`, fail `requirements without a check`.
  An uncovered requirement then switches the banner to ✘.
- A check with no requirement is allowed (a check the method itself needs), but mark it
  `method` in col. H so the reader sees that nobody asked for it.

## 2. Normative basis

"EN 1993-1-1" alone is not a source. Editions differ, the national annex changes values, and
many clauses offer alternatives.

Ask: *Which standards, which edition, with which national annex, and which of the offered
options?* Table on `00_README`:

| Standard | Edition (year, amendments) | National annex | Options chosen (NDPs, method alternatives) | Used for |
|---|---|---|---|---|

Rules:

- Never assume the newest edition silently. If the user does not know, record the edition as an
  assumption to confirm (§6).
- Every nationally determined parameter is a `const` row with its source,
  e.g. `ČSN EN 1993-1-1 NA.2.15`, never only the value from the main text.
- One edition per standard in the whole workbook. Mixing clauses from two editions is a finding.
- `meta_std` (title block) holds the short form: the main standard + edition + "NA".
- Standards for the method itself (table values, formulas) and standards for the requirement
  (§1) both belong in the table.

## 3. Safety concept

The safety concept decides what η means. Ask which format applies:

| Format | What η compares | Factors | Typical field |
|---|---|---|---|
| **a) Limit states, partial factors** | design effect E_d / design resistance R_d | γ on actions and materials, combination rules; ULS and SLS separately | structures, foundations, much of mechanical design |
| **b) Allowable stress / global safety factor** | effect / (resistance / k) | one factor k (or allowable value) | pressure parts, machine elements, older rules |
| **c) Rating and derating** | operating value / (rated value × derating factors) | correction factors for temperature, grouping, altitude, duty | electrical equipment, components |
| **d) Acceptance criterion** | measured or computed value / acceptance limit | none, or the measurement uncertainty (§8) | tests, commissioning, quality checks |

Also ask:

- Consequence / reliability class, or the client's extra factor, if any.
- The warning threshold `cfg_eta_warn` (default 0.90). Some clients want more reserve.
- Whether serviceability, fatigue or accidental situations are in scope. Each is its own group
  of checks, or an explicit "out of scope" in the README.

Rules:

- Every factor is a `const` (or `input` if the project sets it) with a source.
- The factor appears in the written relation in col. G (`M_Ed = γ_G·g_k·L²/8 + …`), so the
  reader sees where it is applied.
- Apply each factor **once**, on one side. A factor on both the effect and the resistance, or a
  factored effect compared with an allowable stress that already contains a safety factor, is a
  critical finding.
- One format per check. When the workbook mixes formats (ULS with factors, SLS without), the
  section heading says which one.
- Write the chosen format, the class and `cfg_eta_warn` into `00_README` → Safety concept.

## 4. Cases and the governing case

Almost no design has one set of inputs: there are load cases, operating states (start-up,
rated, overload, fault), scenarios (summer / winter, empty / full) or combinations of them.

Ask: *Which cases have to be checked, how are they formed (combination rule, factors), and are
any left out on purpose?* A single case is a valid answer; write it into the README as
"single case: …".

Build:

1. **Case table** (on the calculation sheet or `9x_Cases`): one row per input that varies,
   one column per case (`LC1`, `LC2`, …, or names). Values are `input` cells with validation;
   case names are named `lst_case`.
2. **Calculation per case**: variant columns (pattern P18). The same formula across the row,
   one column per case, so every case is visible and checkable. No hidden recalculation of one
   column with a switch.
3. **Envelope**: each check row takes the worst case, `η = MAX(<row of η over the cases>)`, and
   the **governing case** next to it:
   `=INDEX(lst_case,MATCH(MAX(<η row>),<η row>,0))`. Col. G says
   `=FIXED(…)&" ≤ "&FIXED(…)&" kNm  ("&<governing case>&" governs)"`.
4. Conditional formatting highlights the governing column of each check.
5. The register holds the envelope row of every check (one η per check). Per-case rows only
   when the user wants them.
6. The sketch, report and one-screen calculator show a **selected** case (`in_case`, select from
   `lst_case`), defaulting to the governing one.

Rules:

- The governing case is found by formula, never chosen by hand. A case removed from the
  table is removed with a reason in the README.
- Different checks may be governed by different cases; that is expected and must be visible.
- A combination rule (factors, which actions combine with which) belongs in a `const` table
  with its source, not in the case values.

Done when every check row names its governing case.

## 5. Sign convention and coordinate system

A wrong sign gives a plausible number. Define once, for the whole workbook:

- **Axes and origin**: which point is the origin, positive directions of x / y / z. The live
  sketch draws axis arrows with labels.
- **Positive directions** of forces, moments, rotations and displacements; whether tension or
  compression is positive.
- **Electrical**: consumer (load) or generator reference system; reference direction of current
  and power flow; which phasor is the reference (angle 0).
- **Angles and time**: degrees or radians in formulas (Excel trigonometry uses radians, convert
  in a visible row); time origin of a transient.

Rules:

- One convention for the whole workbook, written into `00_README` → Conventions with a small
  sketch.
- Data that arrive in another convention (a load from another calculation, measurements) are
  converted in a visible `calc` row ("sign changed: their tension +, ours compression +").
- A result whose sign carries meaning gets a remark: `=IF(out_N<0,"compression","tension")`.
- Checks use the magnitude only when the standard says so, and the relation in col. G shows
  `|N_Ed|`.

## 6. Status of input data

A source alone does not say how far the number can be trusted. Every input gets a source
**and** a status in col. H:

| Status | Meaning | Col. H example |
|---|---|---|
| **confirmed** | taken from a released document | `drawing 1234 rev. C` / `client data 2026-10-12` |
| **measured** | from a measurement, with uncertainty (§7, §8) | `protocol P-17, U = ±0.5 %` |
| **standard / catalogue** | a value from a standard or datasheet (usually `const`) | `EN … Tab. 3.1` |
| **assumed** | the engineer's or agent's assumption | `A02 – assumed, to confirm` |

**Assumption register** on `00_README`:

| ID | Quantity (name) | Assumed value | Basis of the assumption | Status | Confirmed by / date |
|---|---|---|---|---|---|

Status is a select `TO CONFIRM; CONFIRMED` (range `asm_status`).

One row in the register makes the banner react:

- Path A: condition row with the status
  `=IF(COUNTIF(asm_status,"TO CONFIRM")=0,"✔ all assumptions confirmed","▲ result conditional on "&COUNTIF(asm_status,"TO CONFIRM")&" unconfirmed assumption(s)")`.
  The ▲ counts into `chk_warn`, so the banner reads "OK WITH LOW RESERVE" and the count.
- Path B: `s.condition("chk_asm", "Assumptions confirmed", 'COUNTIF(asm_status,"TO CONFIRM")=0',
  ok="all assumptions confirmed", warn="result conditional on unconfirmed assumptions")`.
  With `warn` instead of `fail`, an unmet condition gives ▲, not ✘.

Rules:

- An agent-made assumption is **always** `TO CONFIRM` and is named in your answer.
- A workbook with unconfirmed assumptions may be handed over, but the README and the report
  title say **PRELIMINARY**.
- An assumption that changes the result decisively (the check is ✘ or ▲ when it moves within a
  sensible range) is pointed out to the user explicitly.

## 7. Uncertainty and tolerances of inputs

Ask: *Do we calculate with nominal values, or with the unfavourable limit? Are tolerances of the
inputs known?* Default: nominal values plus the safety concept (§3); tolerances only where the
user gives them or a standard requires them.

Build when tolerances apply:

- Two input rows: nominal value and tolerance (or `x_min` / `x_max`), each with a source.
- A design value `calc` row takes the unfavourable bound with a remark saying why it is
  unfavourable for this check.
- When the unfavourable direction differs between checks, or is not obvious, compute **both
  bounds as cases** (§4) and let the envelope find the governing one. Do not guess the
  direction.
- Worst case (sum of tolerances) is the default. A statistical combination (RSS) only with a
  stated distribution and a `condition` recording it.
- A measured input carries its expanded uncertainty `U` (k = 2) with the source (calibration
  certificate, protocol).

## 8. Test / measurement report

When the workbook judges measured data (a test, commissioning, an acceptance check), the checks
compare measurements with acceptance criteria and the measurement must be traceable.

Sheets and blocks:

1. **Test identification** (`00_README` or the report): test object and serial number, test
   specification or standard, date (`meta_test_date`), place, operator, witness.
2. **Test conditions** as `input` rows (ambient temperature, humidity, supply voltage, …). Each
   has a `condition` for the range the test standard requires.
3. **Instruments** (Excel table `tbl_instr`): instrument, ID / serial no., range, accuracy,
   calibration certificate, valid until. One condition per instrument, or one for the table:
   `=IF(COUNTIF(db_instr_valid,"<"&meta_test_date)=0,"✔ all calibrations valid","✘ calibration expired")`.
4. **Measured data**: an Excel table (import through Power Query, excel-toolbox §6). Raw values
   are never edited; derived values come from formulas next to them.
5. **Acceptance rows**: one per criterion, linked to a requirement ID (§1). Measured value x,
   uncertainty U, limit, decision.

**Decision rule** (ISO 14253-1, ILAC-G8). Agree it with the user and write it into the README:

| Rule | Pass | Fail | Otherwise |
|---|---|---|---|
| simple acceptance (U not considered, stated as such) | x ≤ limit | x > limit | — |
| guarded acceptance | x + U ≤ limit | x − U > limit | ▲ inconclusive |

Status for an upper limit under guarded acceptance:

```
=IF(NOT(ISNUMBER(x)),"✘ CANNOT EVALUATE",
 IF(x+U<=lim,"✔ PASS",IF(x-U>lim,"✘ FAIL","▲ INCONCLUSIVE – within U")))
```

η = x / limit is still computed for the utilisation chart. The status comes from the decision
rule, not from η. For a lower limit swap the signs of U.

The banner then states the test result: ✘ when a criterion fails, ▲ when one is inconclusive or
an assumption is unconfirmed.

Done when every acceptance criterion has a requirement ID, every measured value an instrument
with a valid calibration, and the decision rule is written down.
