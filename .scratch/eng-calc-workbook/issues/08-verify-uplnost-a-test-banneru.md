# 08 — verify: úplnost řádků a automatický test banneru

**Co dodá:** `verify.py --stress` — kontrola, že každý řádek calc padu má symbol, jednotku a (u const/check) zdroj; automaticky přepne každý číselný vstup za horní mez, přepočítá a ověří, že banner skončí ✘; nahlásí vstupy, které banner nepřepnou.

**Blokováno:** Nic — lze začít hned.

**Status:** ready-for-agent

- [ ] Nové lint pravidlo „neúplný řádek“ s místem a chybějícím polem
- [ ] Stress test nad referenčním buildem projde (všechny vstupy přepnou banner)
- [ ] Doba běhu < 2 min pro referenční build
