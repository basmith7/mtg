# 06 Goldfish and mana

**Contract:** the goldfish knows colours and commander tax, and the colour-source check rests on numbers
we can cite.

**Seam:**
- `goldfish.simulate` library entries gain colours: lands produce their `produced_mana`, rocks and dorks
  their colours; a spell is castable when generic + coloured pips can be paid. Returns a dict:
  `keep7` (share of opening 7s kept without a mulligan), `cast_by[t]` (commander castable, colours
  respected), `recast_by[t]` (second cast at MV+2 after one removal on the turn it lands), `mulls`,
  plus the existing lands-by-4 and ramp-by-2.
- `goldfish.sources_needed(pips, mv)`: replace `KARSTEN_99` with a table computed in the module by a
  stdlib hypergeometric (99-card deck, 7-card hand, on the draw, castable on curve with ≥90%
  probability, conditional on having enough lands — Karsten's model). Compare with the old table and
  with Karsten's published Commander numbers if the article text can be had (TCGplayer renders with
  JS; ask Brian to paste it only if computed and old numbers disagree by more than 2). The docstring
  states which it is. Never claim "Karsten" for numbers not checked against him.
- `scripts/deck_stats.py` prints the new lines in `-- Goldfish` and the source check in `-- Mana`.

**Run:**
```
keepable 7: 84% · commander {3}{B}{R}{R} castable by T5 64%, T6 82% · recast by T8 51%
R: 22 sources; heaviest RR at MV 3 wants 21: ok
```

**Tests:** `tests/test_goldfish.py`: seeded; a deck with no red sources never casts an RR commander;
more sources never lowers `cast_by`; recast is never earlier than first cast + 1; table monotonic in
pips. Replace slice 01's golden values where behaviour intentionally changed (say so in the commit).
**Checkpoint:** the table's provenance.
**Delegated:** mulligan heuristics' details beyond "2–5 lands and a source for a 2-drop".

## Source-count table: provenance (checkpoint)

`goldfish.sources_needed` is **computed**, not copied: a stdlib multivariate hypergeometric over a
99-card deck with 41 lands (Karsten's 2022 assumption), 7-card hand plus a draw every turn including
turn 1, conditional on at least MV lands seen, target 89 + MV percent (Karsten's per-MV consistency
rule), **no mulligans**. Karsten's numbers below are from his article "How Many Sources Do You Need to
Consistently Cast Your Spells? A 2022 Update" (TCGplayer, 2022-08-02, 99-card column), read on
2026-10-24 through TCGplayer's content API (`infinite-api.tcgplayer.com/content/article/dc23a7d2-…`).
His model adds a London mulligan with Commander's free mulligan; that is why his 1-3 drops need fewer
sources (his article says the free mulligan lowered them by up to 3-4). From MV 4 up the two agree
within 1. The old `KARSTEN_99` table was from memory and ran 3-9 sources low throughout.

| Cost | Computed | Karsten 2022 (99) | Old table |
|---|---|---|---|
| C (MV 1) | 24 | 19 | 19 |
| 1C | 21 | 19 | 16 |
| CC | 33 | 30 | 24 |
| 2C | 19 | 18 | 14 |
| 1CC | 29 | 28 | 21 |
| CCC | 37 | 36 | 28 |
| 3C | 17 | 16 | 13 |
| 2CC | 26 | 26 | 19 |
| 1CCC | 33 | 33 | 25 |
| 4C | 15 | 15 | 12 |
| 3CC | 24 | 23 | 17 |
| 2CCC | 30 | 30 | 22 |
| 1CCCC | 36 | 36 | - |
| 5C | 14 | 14 | 12 |
| 4CC | 22 | 22 | 17 |
| 3CCC | 28 | 28 | 22 |
| 5CC | 20 | 20 | 17 |
| 4CCC | 26 | 26 | 22 |

We keep the computed numbers: the playgroup's free mulligan isn't recorded in `RULES.md`, so the stricter
no-mulligan figures are the honest default for cheap spells. If the table plays the free mulligan, Karsten's
column is the one to use for MV 1-3.

## Done

- `mtg/goldfish.py`: `Card`/`Cost` entries with colours; `can_pay` (Hall's condition) and `pay`; mulligan
  `keepable`; `simulate` returns `keep7`, `cast_by`, `recast_by`, `mulls`, `lands4`, `drops4`, `ramp2`;
  `sources_needed` computed by `p_on_curve`.
- `scripts/deck_stats.py`: the Mana check judges each colour by the card needing the most sources
  (not just the most pips); Goldfish prints the keepable/cast/recast line.
- Tests re-pinned (golden values changed with the model) plus the slice's properties and a check against
  Karsten's MV 4+ numbers. Evidence: Breya (WUBR) commander castable by T4 went from 87% (colours ignored)
  to 35%; Anzrag (RG) stays at 91%.
