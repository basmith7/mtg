# mtg

Tools and notes for Brian's Magic: The Gathering stuff: Archidekt deck management, Moxfield reads,
Scryfall card data and pricing, and deck projects.

- **[docs/apis.md](docs/apis.md)** — how each site's API works (Archidekt and Moxfield are private,
  reverse-engineered APIs). Start here.
- **`mtg/`** — small Python clients, standard library only:
  `archidekt.py` (login/refresh, decks, folders, tags, collection, card ids, writes),
  `moxfield.py` (public decks, shared collection), `scryfall.py` (search, cheapest price, set pools),
  `quill.py` (markdown → Archidekt primer format), `decklist.py` (decklist files).
- **`scripts/`**
  - `build_pool.py [sets...]` — every card from some sets into `cache/pool.json` (default: Ravnica).
  - `check_decks.py` — validate decklists (60 cards, 4-of, colors, in pool) and price them, with an
    optional buy/proxy split and owned-card allocation.
  - `check_commander.py` — validate Commander lists: 100 singleton cards, colour identity, legality,
    Game Changer count (`--max-gc`, default 4) and no Universes Beyond (`--allow-ub` to permit).
  - `upload_decks.py` — create decks on Archidekt in a folder, file cards by type (commanders under
    Commander), attach primers (`--primers` file, or a `deck.md` beside `deck.txt`).
- **`decks/`** — deck projects. `decks/ravnica/`: the 22 Ravnica-sets-only decks from 2026-10-03
  (`power/` = the 10 guild decks, `extra/` = 12 themed decks, `core/` = cheaper beginner versions of the
  guild decks), their primers, `BUY_ALL.txt` / `PROXY_ALL.txt`, and `spare_cards.json` (owned cards not
  in a paper deck at the time).

`cache/` (git-ignored) holds the card pool, a price cache and Archidekt card ids. Delete `prices.json` to
re-price. The Archidekt login lives outside the repo in `~/.config/mtg/archidekt-session.json`.

## Quick start

```sh
scripts/build_pool.py                       # once, or with other set codes
scripts/check_decks.py --pool cache/pool.json decks/ravnica/power/*.txt
scripts/check_decks.py --pool cache/pool.json --owned decks/ravnica/spare_cards.json \
    --proxy-at 1 --lists out/ decks/ravnica/power/*.txt
scripts/upload_decks.py --folder <archidekt folder id> --primers decks/ravnica/primers_core.py deck.txt
```

```python
from mtg import archidekt, moxfield, scryfall
archidekt.folder_tree()
moxfield.public_decks()
scryfall.cheapest_usd('Lightning Helix')
```

## Decklist format

```
# Boros Legion | RW
4 Legion Warboss
4 Sacred Foundry
8 Mountain
```

The header's color letters (WUBRG) drive the color check. Commander lists add a
`Commander: Card Name` line and list the commander as `1 Card Name` too, so they total 100;
`decks/commander/` holds them, with `BRIEF.md` describing the power target and house rules.
