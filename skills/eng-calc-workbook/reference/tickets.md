# Cesta D — rozpad sešitu na tickety

Velký výpočtový sešit se staví jako **tracer bullets**: každý ticket protáhne úzký, ale
**úplný** řez všemi vrstvami — vstup → výpočet → posudek v registru → banner → řádek na
přehledu — a po dokončení je ověřitelný sám o sobě (verify exit 0, ruční kontrola čísla).
Ne „nejdřív všechny vstupy, pak všechny vzorce“: horizontální vrstva nejde ověřit.

## 1. Kontext

Ze specifikace (SKILL.md §1) nebo konverzace vypiš posudky a podmínky platnosti — to jsou
přirozené hranice řezů. Existující sešit nejdřív projdi (listy, názvy, vstupy).

## 2. Řezy

- **01 Kostra** (vždy první, nic ji neblokuje): README identifikace, `80_Kontroly` s
  `cfg_eta_warn`, prázdný calc list s hlavičkou a bannerem, jeden vstup a jeden posudek
  napříč celou cestou. Hotovo = banner reaguje na vstup za mezí.
- **Databáze** jako vlastní ticket jen pokud ji potřebuje víc řezů; jinak patří do prvního řezu, který ji používá.
- **Jeden posudek (nebo úzká skupina se sdílenými mezivýsledky) = jeden ticket**: jeho vstupy,
  konstanty se zdroji, kroky, check/condition, řádek registru, referenční hodnota.
- **Grafika** (živá skica, průběhy, přehled) po posudcích, které zobrazuje.
- **Předávka** poslední: README úplné, zámek, tisk, checklist, revize.
- Ticket se vejde do jedné session. Sdílený mezivýsledek → ticket, který ho zavádí, blokuje ostatní.

**Přestavba starého sešitu** (široká změna, např. přejmenování na standard): expand–contract —
nejdřív nová struktura vedle staré (výsledky se porovnávají), pak převod list po listu
(ticket na list, blokovaný expand), nakonec odstranění staré verze (blokované všemi převody).

## 3. Kvíz

Předlož číslovaný seznam: **Název** · **Blokováno** · **Co dodá** (posudek, který začne
fungovat end-to-end). Zeptej se: sedí granularita? sedí blokující hrany? sloučit/rozdělit?
Iteruj do schválení.

## 4. Publikace

Jeden soubor na ticket, číslováno v pořadí závislostí (blokující první):
`.scratch/<sesit-slug>/issues/<NN>-<slug>.md` (v projektu / repozitáři uživatele;
v Claude in Excel je předlož v odpovědi jako seznam ke zkopírování).

```markdown
# <NN> — <Název>

**Co dodá:** posudek / funkce, která po ticketu funguje end-to-end, z pohledu uživatele sešitu.

**Blokováno:** <NN — název>, nebo „Nic — lze začít hned“.

**Status:** ready-for-agent

**Reference:** zdroj metodiky (norma, článek), referenční případ s očekávanou hodnotou.

- [ ] Vstupy s rozsahem/seznamem a stavem ve sl. I
- [ ] Konstanty se zdrojem
- [ ] Posudek(y) v registru, η a stav správně
- [ ] Referenční případ: <veličina> = <hodnota> ± <tolerance>
- [ ] verify exit 0 (cesta B) / checklist excel-in-place (cesta A)
```

Pracuj na **frontě**: ticket, jehož blokující jsou hotové. Bez konkrétních adres buněk v
ticketu — stárnou; jména (`out_MEd`) ano.
