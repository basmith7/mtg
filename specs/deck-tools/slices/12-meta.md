# 12 Playgroup meta (mtg-table, private)

**Contract:** before building a deck, the agent can see what the playgroup plays, so a new deck neither
duplicates nor quietly hard-counters a friend's.

**Seam:** `mtg-table/meta.py`: `commanders(replays, me) -> Counter` of opponents' `commanderName`;
`themes(replays, me)` using public `mtg.patterns` over their `deckSnapshots`; `--names` prints one
commander per line (for `scripts/discover.py --avoid -`). Output is printed, never written into the
public repo.
- `mtg-table/README.md` documents both tools; the public skill does not name mtg-table (agents learn of
  it from that README and the memory notes).

**Tests:** synthetic replays: counts exclude the player's own seat; `--names` format.
**Delegated:** how many games back to look by default.

## Done (2026-10-24)

`mtg-table/meta.py` (commanders, themes, `--names`) with synthetic-replay tests; mtg-table's README
documents both tools. Themes use `mtg.patterns` once slice 02 lands (tested against that module) and fall
back to the site's tags before then. Choices: [choices.md](../choices.md).
