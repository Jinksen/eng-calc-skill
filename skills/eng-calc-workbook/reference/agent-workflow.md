# Agent workflow — who does what, on which model

Use this when you can start subagents (Claude Code `Agent` tool, an SDK orchestrator) and the
workbook is bigger than one quick sheet (path D, or ≥ 2 catalogues to transcribe). Claude in
Excel and plain chat have no subagents: do the same steps yourself, in the same order.

The idea: **judgement stays on the strong model, typing goes to cheaper ones, and anything a
script can decide costs no tokens at all.** Agents never talk to each other — they hand over
**files**, and every hand-over is checked by a script or by the lead.

## Roles

| Role | Model tier | Does | Never does |
|---|---|---|---|
| **Lead** (you) | strongest (Opus) | talks to the user, specification §1, layout, method and checks, ticket split, reviews every hand-over, final answer with the hand check | types cells, transcribes tables, fixes lint |
| **Extractor** | cheapest (Haiku) | one catalogue table from a PDF / web page / old workbook → CSV in a fixed schema, with a source per row | chooses values, interpolates, fills gaps |
| **Builder** | mid (Sonnet) | one ticket: edits `build_<name>.py` from the approved spec, runs `verify.py` until exit 0 | changes the spec, adds checks, invents inputs |
| **Checker** | mid (Sonnet), **fresh context** | computes the reference case from the spec alone and compares its η with the register in `verify.py --json` | reads the build script or the builder's notes |
| **Visual reviewer** | cheapest with vision (Haiku) | looks at the rendered PNGs against the Restraint list in [visual-language.md](visual-language.md), returns findings | edits anything |
| **Scripts** | no model | recalculation, error values, lint, render, catalogue integrity (`unique_keys`, `ascending`, `refs_ok`) | — |

The checker gets a fresh context on purpose: a check done by the same context that wrote the
formula repeats its mistake. That independence is worth more than the cost of a mid model.

## Files are the contract

```
.scratch/<slug>/
  spec.md            approved specification (§1) — only the lead edits it
  data/<table>.csv   one file per catalogue, last column "source"
  issues/NN-*.md     tickets (tickets.md), status ready-for-agent → done
  build_<slug>.py    the only place workbook content is written (path B)
  out/verify.json    python scripts/verify.py out/<file>.xlsx --json --render out/render
  out/render/*.png   pages for the visual reviewer
  review/NN-*.md     checker / reviewer findings
```

A subagent starts cold. Its brief is: the role (one line), the paths it reads, the path it
writes, the done criterion, and "stop and report if anything is missing — do not guess". Never
paste the conversation; never ask it to read the whole skill — name the one or two reference
files it needs (builder: `python-engcalc.md`, `visual-language.md`; extractor: `databases.md` §1 and §5).

## Flow

1. **Lead** — specification with the user, layout choice, tickets (`tickets.md`). Strong model,
   because a wrong method or a missing check is the expensive error; everything later only
   implements it.
2. **Extractors in parallel**, one per catalogue table. Schema in the brief (`key,Iz,…,source`).
   Then a script loads every CSV and runs the integrity conditions; the lead spot-checks 3
   random rows against the source. A failing table goes back once, then the lead does it.
3. **Builder** on ticket 01 (skeleton). Its loop is script-driven: build → `verify.py --json`
   → fix → repeat, **at most 3 rounds**; still failing → it reports and the lead takes over
   (a cheap model looping on a hard error costs more than one strong pass).
4. **Further tickets**: one builder per ticket whose blockers are done. Tickets that touch the
   same build script run **one after another**; independent workbooks or data sheets may run in
   parallel.
5. **Checker** per ticket with a reference case: reads `spec.md` + `verify.json`, computes the
   reference case by hand / with a few lines of Python and compares **η of each check** (the
   JSON carries the register: label, η, status), writes `review/NN-check.md` (expected,
   workbook, deviation, verdict). Intermediate values the JSON does not carry are read by the
   lead in the rendered pages, not by opening the `.xlsx`.
6. **Visual reviewer** once at the end (and after the first ticket that adds a drawing or
   dashboard): PNGs + the Restraint table → list of findings. The builder fixes them.
7. **Lead** — reads `verify.json` (exit code, statuses), the review files and the PNGs of
   the overview and report pages; does §6 of SKILL.md; answers the user.

## Cost rules

- **Script before model.** Values, error counts, statuses and lint come from `verify.py --json`
  — no agent reads an `.xlsx` cell by cell or "looks whether the formulas are right".
- **Smallest input.** Pass paths and line ranges, not files' contents; a builder of ticket 05
  does not need the PDF of the standard, only `spec.md` and the CSVs.
- **Cheap output is always checked** — by a script (schema, integrity, verify) or by the lead
  on a sample. Unchecked output of a cheap model is a guess.
- **Escalate, don't retry.** Two failures of the same kind on a cheaper tier → the next tier up.
- **Parallel only what is independent**: extraction per table, checkers per ticket, separate
  workbooks. One writer per file at a time.
- **No agent for small things**: one sheet, one table of 10 rows, a single fix — the lead does
  it directly; starting a subagent costs more than the work.
- **Stable prefixes**: keep SKILL.md and the reference files unchanged during a build so their
  prompt cache stays warm across subagent calls.

## Path A (Claude in Excel) and plain chat

No subagents: the same order, done by one model — spec → data → slice by slice → independent
hand check (compute it *before* reading the workbook's value) → visual pass against Restraint.
The file layout above is replaced by sheets: `spec` lives in `00_README`, data in `9x_` tables.
