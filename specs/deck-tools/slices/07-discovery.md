# 07 Discovery and challenge decks

**Contract:** the agent can find underplayed commanders matching the player's taste and roll a challenge
deck brief.

**Seam:**
- `mtg/discovery.py`:
  - `MECHANICS = {name: scryfall_query}` for `control-swap` (`o:"target opponent gains control" or
    o:"target player gains control" or o:"exchange control"`), `goad`, `vote` (`o:"will of the council"
    or o:vote`), `coin` (`o:"flip a coin"`), `monarch` (`o:monarch`; **not** `kw:monarch`, which
    matched 3803 commanders), `each-player`, `chaos` (`o:random or o:"at random"`). All with
    `is:commander f:commander`. Probed counts: goad 33, control-swap 5, coin 7.
  - `profile.enjoys(player) -> [str]` (in `mtg/profile.py`) reads the "What … enjoys" bullets;
    `discovery.mechanics_for(enjoys) -> [name]` by keyword.
  - `discovery.candidates(mechanics, exclude=set(), colours=None) -> [(name, mechanics, rank)]`
    ordered by Scryfall `edhrec_rank` descending (no EDHREC calls); `--counts` fetches EDHREC
    `num_decks` for the top 15 only.
  - `discovery.challenge(rng, kinds=None) -> {'text', 'query'}`: one of underplayed commander from
    `candidates`, art tag (`atag:<tag>` from a curated list of ~30 tags, e.g. dragon, cat, moon), flavour
    word (`ft:<word>`), or one year's sets (`year:<y>`). The query bounds the card pool.
- `scripts/discover.py [--mechanic m ...] [--colours BR] [--avoid file] [--counts] [--challenge
  [--seed n]]`. Commanders already in `decks/` are skipped.
- `check_commander.py --pool "<query>"` flags cards outside a challenge's pool (one Scryfall search).
- `.claude/skills/commander-deck/SKILL.md`: a "Finding a commander" section and the description gains
  "find me a commander", "something weird", "challenge deck".

**Run:**
```
scripts/discover.py
from Brian's profile: control-swap
  control-swap  rank 9120  WUR  Zedruu the Greathearted
scripts/discover.py --challenge --seed 3
Challenge: build Gyruda with only cards showing dragons (atag:dragon f:commander, 1109 cards)
```

**Tests:** `tests/test_discovery.py`: faked `scryfall.search` → ordering and exclusion; enjoys parse on
an inline profile; same seed → same challenge; query strings. `tests/test_profile.py` for `enjoys`.
**Delegated:** the art-tag list, the keyword map, output layout.

## Done (2026-10-24)

Probed live (Scryfall `total_cards`, `is:commander f:commander`): control-swap 9 (spec's three phrases 7;
Zedruu matches), goad 30, vote 7, coin 7, monarch 15 (`kw:monarch` 3497), each-player 86, chaos
(`o:"at random"`) 28. Art tags 111-2240 each, flavour words 132-831 (choices/07.md).
`scripts/discover.py` from Brian's profile (main checkout's decks, so Zedruu, Xantcha, Jon Irenicus skipped):
```
from Brian's profile: control-swap
  control-swap   rank 15543  RG    Abby, Merciless Soldier  18 decks
  control-swap   rank 10487  U     Bilbo, Luckwearer // Burglar's Plot  253 decks
  ...
Challenge: build Sally Pride, Lioness Leader with only cards whose art shows a frog   (--seed 3)
Challenge: build The Peregrine Dynamo with only cards printed in 2022's sets          (--seed 11)
```
`check_commander.py --no-combos --pool "atag:dragon f:commander" zedruu.txt`: 74 cards outside, exit 1.
