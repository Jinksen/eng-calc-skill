# Path D — splitting a workbook into tickets

A large calculation workbook is built as **tracer bullets**: each ticket pulls a narrow but
**complete** slice through all layers — input → calculation → check in the register →
banner → row on the overview — and when done it can be verified on its own (verify exit 0,
hand check of a number). Not "all inputs first, then all formulas": a horizontal layer cannot
be verified.

## 1. Context

From the specification (SKILL.md §1) or the conversation, list the checks and validity
conditions — they are the natural slice boundaries. Read an existing workbook first (sheets,
names, inputs).

## 2. Slices

- **01 Skeleton** (always first, blocked by nothing): README identification, `80_Checks` with
  `cfg_eta_warn`, an empty calc sheet with title block and banner, one input and one check
  through the whole path. Done = the banner reacts to an input beyond its limit.
- **Database** as its own ticket only if several slices need it; otherwise it belongs to the
  first slice that uses it.
- **One check (or a narrow group with shared intermediate results) = one ticket**: its inputs,
  constants with sources, steps, check / condition, register row, reference value.
- **Graphics** (live sketch, drawing, diagrams, overview) after the checks it shows.
- **Handover** last: complete README, protection, printing, checklist, revision.
- A ticket fits into one session. A shared intermediate result → the ticket that introduces
  it blocks the others.

**Rebuilding an old workbook** (a broad change, e.g. renaming to the standard): expand–contract
— first the new structure next to the old one (results are compared), then conversion sheet by
sheet (one ticket per sheet, blocked by the expand), finally removal of the old version
(blocked by all conversions).

## 3. Quiz

Present a numbered list: **Title** · **Blocked by** · **Delivers** (the check that starts
working end to end). Ask: is the granularity right? are the blocking edges right? merge /
split? Iterate until approved.

## 4. Publishing

One file per ticket, numbered in dependency order (blockers first):
`.scratch/<workbook-slug>/issues/<NN>-<slug>.md` (in the user's project / repository; in
Claude in Excel present them in the answer as a list to copy).

```markdown
# <NN> — <Title>

**Delivers:** the check / feature that works end to end after the ticket, from the workbook user's view.

**Blocked by:** <NN — title>, or "Nothing — can start now".

**Status:** ready-for-agent

**Reference:** source of the method (standard, clause), reference case with the expected value.

- [ ] Inputs with range / list and status in col. I
- [ ] Constants with a source
- [ ] Check(s) in the register, η and status correct
- [ ] Reference case: <quantity> = <value> ± <tolerance>
- [ ] verify exit 0 (path B) / excel-in-place checklist (path A)
```

Work as a **queue**: a ticket whose blockers are done. No concrete cell addresses in a ticket
— they go stale; names (`out_MEd`) are fine.
