# 05 Originality and synergy density

**Contract:** `scripts/originality.py <list>` says how much of the deck is the same 99 everyone runs,
how much it repeats the player's other decks, how tightly its cards work together, and offers odd
same-job swaps.

**Seam:**
- `scores.staple_share(deck_names, edhrec_cards, threshold=40) -> (share, [staples])` over the 99,
  lands and the commander excluded.
- `scores.overlap(deck_names, others: {path: set}) -> [(path, shared, jaccard)]`, basics excluded.
  `others` = every other list in `decks/` (player's working copy).
- `scores.density(names, data) -> float`: mean pairwise interaction over nonland cards. Two cards
  interact if one's oracle text names a type, subtype, counter, keyword or token the other has or
  makes, or both share a `patterns` tag. Idea from dreliq9/urza (MIT); reimplemented, not copied.
  Print it with urza's rough bands as context (goodstuff ~0.1, tribal ~0.5), calibrated on 3 of
  Brian's decks and recorded here.
- `roles.alternatives(card, identity, n=3) -> [names]`: Scryfall search for cards sharing the staple's
  role otag, within colour identity, Commander-legal, ordered by `edhrec_rank` descending (least
  played first), excluding Game Changers and cards already in the deck.

**Run:**
```
staples: 38% of the 99 (34 cards at 40%+ inclusion) · closest own deck: thantis.txt, 11 shared
synergy density: 0.31 (goodstuff ~0.1, tribal ~0.5)
odd swaps: Swords to Plowshares (removal) -> Chaos Warp?, Generous Gift?, ...
```

**Tests:** `tests/test_scores.py`: staple share on a fixture page; Jaccard on two temp decks; density on
a tiny synthetic set (two Elves + an elf lord interact; Sol Ring + Island don't). `alternatives` with
faked `scryfall.search`.
**Delegated:** the interaction rules' details, thresholds, how many swaps to show.

## Done (2026-10-24)

Density calibration (nonland cards, commander included):

| Deck | Style | Density |
|---|---|---|
| zedruu.txt | group hug / donate | 0.17 |
| ayula.txt | bear tribal | 0.21 |
| breya.txt | artifacts | 0.59 |

`scripts/originality.py decks/commander/zedruu.txt`:
```
staples: 34% of the nonland 99 (22 cards at 40%+ inclusion) · closest own deck: oloro.txt, 29 shared (Jaccard 0.20)
synergy density: 0.17 (own decks: Zedruu group hug 0.17, Ayula bears 0.21, Breya artifacts 0.59)
odd swaps:
  Sol Ring (ramp) -> Mind Stone?, Solemn Simulacrum?, Commander's Sphere?
  Arcane Signet (ramp) -> Chromatic Lantern?, Mana Drain?, Lotus Petal?
  Humble Defector (draw) -> Skullclamp?, Brainstorm?, Esper Sentinel?
```
Tests in `tests/test_originality.py` (not `test_scores.py`, which the salt slice owns). Deviations
(no `patterns` clause, most-played-first swaps, own-deck bands): [choices.md](../choices.md).
