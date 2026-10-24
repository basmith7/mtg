# 04 Hidden gems

**Contract:** `edhrec_recs.py "<Commander>" --gems` lists cards that fit the commander unusually well but
few decks play.

**Seam:**
- `edhrec._cards` also keeps `lift` and `trend_zscore` (both present on commander pages, probed).
- `scores.gems(cards, max_inclusion=15, min_decks=20, exclude=()) -> list` ranked by `lift`, ties by
  `synergy`. `min_decks` keeps noise out on small commanders.
- `scripts/edhrec_recs.py`: `--gems`; with `--deck` it excludes cards already in the list.

**Run:**
```
== Hidden gems (inclusion under 15%, by lift) ==
  lift 3.4  inc  6.1%  trend +1.8  Sigil of the Empty Throne
```

**Tests:** fixture `tests/fixtures/edhrec_commander_zur.json` (trimmed real page) through a faked
`edhrec._fetch`: order, inclusion cap, `min_decks` cut, exclusion of deck cards.
**Delegated:** column layout, the default thresholds (record what you picked and why).

## Done (2026-10-24)

`scripts/edhrec_recs.py "Zedruu the Greathearted" --gems --deck decks/commander/zedruu.txt --top 8`:
```
== Hidden gems (inclusion under 15%, by lift) ==
  lift 32.6  inc 12.4%  trend +15.0  Dack Fayden, Helping Hand
  lift 28.2  inc  9.5%  trend -0.2  Jinxed Ring
  lift 27.8  inc  6.5%  trend +0.0  Embargo
  ...
```
Tests: `tests/test_gems.py` (6, on the trimmed Zur fixture). Choices: [choices.md](../choices.md).
