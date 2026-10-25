# eng-calc-workbook

Agent skill pro **inženýrské výpočtové sešity v Excelu** — elektro, strojní, stavební.
Sešit se čte jako ruční výpočet ve zprávě: hlavička → banner stavu → vstupy → kroky →
posudky s využitím η a stavem ✔ / ▲ / ✘ → výsledek, plus registr posudků, README
s legendou, živé skici z grafů a ověření.

| Prostředí | Jak skill pracuje |
|---|---|
| **Claude in Excel** | živě v otevřeném sešitu, jen nativní Excel (vzorce, styly, CF, ověření dat, názvy) |
| **claude.ai / Claude Code** | generuje `.xlsx` knihovnou `engcalc.py`, ověří přes LibreOffice |
| Revize | tabulka nálezů podle závažnosti |
| Velký sešit | rozpad na tracer-bullet tickety s blokujícími hranami |

## Struktura

```
.claude-plugin/plugin.json
skills/eng-calc-workbook/
  SKILL.md                    postup (specifikace → kostra → calc pad → podmínky → grafika → ověření)
  agents/openai.yaml
  reference/
    sheet-styles.md           styl K (kompaktní posudkový list, TCC) a styl P (calc pad)
    visual-language.md        barvy, mřížka, hlavička, styly (jediný zdroj pravdy)
    conditions.md             vzorce stavů, registr, banner, podmíněné formátování
    excel-toolbox.md          úkol → funkce → verze (komplexní čísla, matice, statistika, LET/LAMBDA, Power Query…)
    excel-in-place.md         cesta A — Claude in Excel / ruční stavba
    python-engcalc.md         cesta B — API knihovny, úskalí openpyxl
    tickets.md                cesta D — rozpad na tickety
    review.md                 cesta C — revize
    domains.md                typické posudky elektro / strojní / stavební
    patterns.md               katalog vzorů z referenčních sešitů
    part-drawing.md           parametrický výkres dílu: kóty, tolerance, GD&T, razítko
    dashboard-widgets.md      posuvníky, přepínače, ukazatele, tvary, vývojové diagramy
    vba.md                    makra (jen desktop)
  scripts/
    engcalc.py                builder (openpyxl)
    example_ipe_beam.py       referenční build: posudek nosníku IPE dle ČSN EN 1993-1-1
    verify.py                 přepočet LibreOffice + lint + render PNG
.scratch/eng-calc-workbook/issues/   backlog vylepšení skillu (tickety)
.github/workflows/verify.yml          CI: build všech example_*.py + verify
```

## Instalace

- **claude.ai / Claude in Excel**: zabal složku `skills/eng-calc-workbook` do ZIP a nahraj v
  Nastavení → Schopnosti → Skills; zapni ho. Claude in Excel aplikuje zapnuté skills automaticky.
- **Claude Code**: `/plugin marketplace add Jinksen/eng-calc-workbook` a nainstaluj,
  nebo zkopíruj složku skillu do `~/.claude/skills/`.

## Referenční build

```bash
pip install openpyxl pillow matplotlib
python skills/eng-calc-workbook/scripts/example_ipe_beam.py out/posudek_IPE_v1.0.xlsx
python skills/eng-calc-workbook/scripts/verify.py out/posudek_IPE_v1.0.xlsx --render out/render
```

## Vývoj

Vylepšení se plánují jako tickety v `.scratch/eng-calc-workbook/issues/` (formát
Matt Pocock `to-tickets`: jeden soubor na ticket, `Blokováno`, akceptační kritéria).
Pracuje se na frontě — tickety, jejichž blokující jsou hotové. Každá nová schopnost
knihovny musí mít referenční použití v buildu a projít `verify.py`.

Licence MIT.
