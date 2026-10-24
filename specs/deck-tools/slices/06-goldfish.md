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
