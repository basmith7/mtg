# 02 Bracket check

**Contract:** `check_commander.py` prints the official bracket, Spellbook's tag and the house verdict.

**Seam:**
- `spellbook.estimate_bracket(commanders, cards) -> {'tag': 'P', 'name': 'Powerful', 'cards': [{'name',
  'game_changer', 'mass_land_denial', 'extra_turn', 'banned'}], 'combos': [{'id', 'two_card', 'speed',
  'lock', 'tag'}]}`. `POST /estimate-bracket` with the same body shape as `find_combos`. Response shape
  probed 2026-10-24 (README Decisions). `two_card` = `definitelyTwoCard`.
- `patterns.classify(card) -> frozenset` gains `mld`, `extra-turn` from oracle text (fallback when
  Spellbook is down; Spellbook's flags win when present).
- `brackets.official(gcs, flags, combos) -> (int, [reasons])`, WotC criteria as of 2026-02-09:
  B4 if more than 3 Game Changers, any mass land denial, chained extra turns, or a two-card infinite
  combo that is FAST; B3 if 1–3 Game Changers or any (late) two-card infinite combo; else B2. Re-read
  the WotC 2026-02-09 page at the start of the slice and correct these edges if they differ. B5 is never inferred
  (it is intent, "cEDH"); B1 is not inferred either (theme intent). Reasons are short phrases.
- `brackets.house(gcs, flags, combos, max_gc) -> (ok, [reasons])`: RULES.md — Game Changers ≤ `max_gc`
  (existing `--max-gc`, default 4), no MLD, no extra-turn *chains* (more than one extra-turn card),
  no fast infinite combo (existing `!!`).
- `brackets.line(official, spellbook, house) -> str`.

**Run:** `scripts/check_commander.py decks/commander/<deck>.txt` adds after the Game Changers line:
```
   bracket: Official B4 (4 Game Changers) · Spellbook R (Ruthless) · House 3.75 ✓
```
House ✗ reasons become `!!` lines. Official B4 alone is not a problem (exit code unchanged).
`--no-combos` skips the Spellbook call; Spellbook failure prints `Spellbook unavailable` and never crashes.

**Tests:** `tests/test_brackets.py` (pure): 3 GC → B3; 4 GC → B4 and house ✓ at max 4; one MLD → B4
and house ✗; one fast two-card infinite → B4; two extra-turn cards → house ✗. `tests/test_spellbook.py`:
fixture `tests/fixtures/spellbook_estimate_thoracle.json` (trimmed real reply) parses; HTTP error →
caller sees None.

**Docs:** `docs/apis.md` Spellbook section: the endpoint, its tag scale and the probe results.
**Checkpoint:** show the bracket line for three of Brian's decks.
**Delegated:** reason wording; whether to list Spellbook's per-card flags under `--verbose`.
**Feedback that changes this slice:** Brian answering the Game Changer cap question (changes `--max-gc`
default and RULES.md, nothing else).
