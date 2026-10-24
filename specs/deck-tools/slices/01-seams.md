# 01 Seams: move logic out of deck_stats.py and check_commander.py, no behaviour change

**Contract:** pure, importable modules that later slices extend and tests call directly.

**Moves (behaviour identical):**
- `mtg/roles.py`: `ROLES`, `TARGETS`, `TARGETS_60`, `SHOW`, the role cache path and
  `role_hits(names) -> {role: set(names)}` from `scripts/deck_stats.py`.
- `mtg/goldfish.py`: `KARSTEN_99`, `need`, `mana_producer`, `pips`, `faces`, `is_land`, `front`,
  `simulate` from `scripts/deck_stats.py`.
- `mtg/brackets.py`: `FAST_MV` and `is_fast(combo, mv) -> bool` (the nested `fast()` in
  `check_commander.show_combos`; `mv` is a callable name -> MV or None; unknown counts as fast).
- `mtg/patterns.py`: created empty but for its docstring and `classify(card) -> frozenset[str]`
  returning `frozenset()`; slice 02 fills it.

`scripts/deck_stats.py` and `scripts/check_commander.py` import from these; their output is unchanged.

**Tests (new):**
- `tests/test_goldfish.py`: golden values for `simulate` on a synthetic library with a fixed seed,
  captured *before* the move (cast-turn list summary, mulligan counter).
- `tests/test_brackets.py`: `is_fast` — unknown MV → fast; Ruthless → fast; 7 total MV, Powerful → not.

**Verify:** pull one deck (`scripts/pull.py` on any deck in the player's folder), run `deck_stats.py`
and `check_commander.py --no-combos` on it before and after with the same `--seed`; outputs diff empty.
Paste the diff command and result in the commit message body.

**Delegated:** module docstrings and private helper names.
**Feedback that changes this slice:** none expected.
