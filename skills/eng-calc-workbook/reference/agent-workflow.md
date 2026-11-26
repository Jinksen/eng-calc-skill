# Agent workflow — designer, calculator, checker

Use this when you can start subagents (Claude Code `Agent` tool, an SDK orchestrator) and the
workbook is bigger than one quick sheet (path D, a working sheet with several bands, or ≥ 2
catalogues to transcribe). Claude in Excel and plain chat have no subagents: do the same steps
yourself, in the same order, one role at a time.

The idea: **design and calculation are separate jobs with a contract between them, and the
check is done by someone who wrote neither.** Judgement stays on the strong model, typing goes
to cheaper ones, anything a script can decide costs no tokens. Agents never talk to each
other — they hand over **files**, and every hand-over is checked by a script or by the lead.

## The team

| Role | Model tier | Does | Never does |
|---|---|---|---|
| **Lead** (you) | strongest (Opus) | talks to the user, specification §1, layout choice, method and list of checks, tickets, reviews every hand-over, final answer with the hand check | types cells, transcribes tables |
| **1 Designer** | mid (Sonnet) | the sheet's **form**: tabs (3–6), bands and blocks on one column grid using the width, title block, section bars, cell styles, input cells with validation, spare styled rows, tables for registers and lists, CF ranges per block, print setup, instruction panel, sketch / chart placeholders — per [dense-editable-sheet.md](dense-editable-sheet.md) and [visual-language.md](visual-language.md); writes `layout.md` | writes calculation formulas, chooses methods or values |
| **2 Calculator** | mid (Sonnet); strongest for a hard method | the **content**: every formula, name (`in_*`, `calc_*`, `chk_*`, `k_*`), constant with source, check rows in the register, chart data — only into the cells `layout.md` assigns; runs `verify.py` until exit 0 | changes the layout, styles or the spec; adds checks the spec does not have; invents inputs |
| **3 Checker** | mid (Sonnet) with vision, **fresh context** | (a) numbers: computes the reference case from `spec.md` alone and compares η of each check with `verify.json`; (b) form: rendered PNGs against the hard layout rules and Restraint; (c) editability test from [dense-editable-sheet.md](dense-editable-sheet.md) on a copy of the file; writes `review/NN-check.md` | reads the build script or the other agents' notes; fixes anything |
| **Extractor** (optional) | cheapest (Haiku) | one catalogue table from a PDF / web page / old workbook → CSV in a fixed schema, a source per row | chooses values, interpolates, fills gaps |
| **Scripts** | no model | recalculation, error values, lint, render, catalogue integrity | — |

Why three: a model that designs and calculates in one pass sacrifices one for the other — either
the sheet is a long column of formulas or the formulas are bent to fit the look. Separate roles
with a fixed contract give both. The checker gets a fresh context on purpose: a check done by
the context that wrote the formula repeats its mistake.

## The contract between designer and calculator: `layout.md`

```
| Block            | Band | Range     | Names / cells the calculator fills    | Spare rows |
|------------------|------|-----------|----------------------------------------|------------|
| INPUTS geometry  | 1    | B9:H18    | in_L, in_b, in_h  (value col F)        | 16–18      |
| MATERIALS        | 1    | J9:P18    | in_fck, in_fyk                         | 17–18      |
| SKETCH           | 1    | R9:AB18   | chart reads tbl_Sketch                 | —          |
| CALCULATION      | 2    | B21:P45   | label B, symbol E, relation G (FORMULATEXT), value K, unit L, ref N | 42–45 |
| CHECKS           | 3    | B48:P60   | tbl_Checks rows                        | table      |
```

The designer delivers the skeleton with this table; the calculator may only write into the
listed ranges. Needs more space → it asks the lead, who asks the designer (the spare rows are
for small additions only).

## Files are the contract

```
.scratch/<slug>/
  spec.md            approved specification (§1) — only the lead edits it
  layout.md          block map — only the designer edits it
  data/<table>.csv   one file per catalogue, last column "source"
  issues/NN-*.md     tickets (tickets.md), status ready-for-agent → done
  build_<slug>.py    path B: designer writes the layout part, calculator the formula part
  out/verify.json    python scripts/verify.py out/<file>.xlsx --json --render out/render
  out/render/*.png   pages for the checker
  review/NN-*.md     checker findings
```

A subagent starts cold. Its brief is: the role (one line), the paths it reads, the path it
writes, the done criterion, and "stop and report if anything is missing — do not guess". Never
paste the conversation; never ask it to read the whole skill — name the reference files it needs
(designer: `dense-editable-sheet.md`, `visual-language.md`, `layouts.md`; calculator:
`python-engcalc.md` or `excel-in-place.md`, `conditions.md`; checker: `spec.md`,
`dense-editable-sheet.md` "Editability test", the Restraint list; extractor: `databases.md` §1 and §5).

## Flow

1. **Lead** — specification with the user, layout choice, list of checks, tickets. Strong model,
   because a wrong method or a missing check is the expensive error.
2. **Extractors in parallel** (if there are catalogues), one per table; a script runs the
   integrity conditions; the lead spot-checks 3 rows against the source.
3. **Designer** — skeleton workbook + `layout.md`. While it works, the **calculator may start in
   parallel** on what does not touch the file: the formula list per check, names, the constants
   table with sources (`calc_plan.md`). The lead reviews the skeleton render (bands, width,
   grid) before step 4.
4. **Calculator** — fills the ranges from `layout.md`. Loop: build → `verify.py --json` → fix,
   **at most 3 rounds**; still failing → it reports and the lead takes over.
5. **Checker** — numbers, form, editability. Findings go back to the role that owns them
   (layout → designer, values / formulas → calculator), one round; repeated failure → the lead.
6. **Lead** — reads `verify.json`, the review file and the PNGs of the working sheet and report;
   does §6 of SKILL.md; answers the user.

Designer and calculator write the **same file one after another**, never at once. Independent
workbooks or tickets may run in parallel teams.

## Cost rules

- **Script before model.** Values, error counts, statuses and lint come from `verify.py --json`
  — no agent reads an `.xlsx` cell by cell.
- **Smallest input.** Pass paths and line ranges, not file contents; the calculator does not need
  the PDF of the standard, only `spec.md`, `layout.md` and the CSVs.
- **Cheap output is always checked** — by a script or by the lead on a sample.
- **Escalate, don't retry.** Two failures of the same kind on a cheaper tier → the next tier up.
- **No team for small things**: one sheet, a single fix, a table of 10 rows — the lead does it
  directly in the three roles' order; starting subagents costs more than the work.
- **Stable prefixes**: keep SKILL.md and the reference files unchanged during a build so their
  prompt cache stays warm across subagent calls.

## Path A (Claude in Excel) and plain chat

No subagents: the same order, done by one model — spec → design pass (bands, styles, spare
rows, tables; nothing calculated yet) → calculation pass into the prepared cells →
independent hand check (compute it *before* reading the workbook's value) → visual pass and
editability test. `spec` and the block map live in `00_README`, data in `9x_` tables.
