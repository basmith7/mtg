# 03 — Pull a deck (or a folder) from Archidekt

**Contract:** a working copy can be (re)created from Archidekt, including in a fresh worktree.

**Seam:**
- `mtg/archidekt.py: export(deck_json) -> dict(name, colors, commanders, cards, primer_md,
  dropped, deck_id)` using `main_cards`, `decklist`, `quill.from_delta`, `scryfall.color_identity`.
  Maybeboard/sideboard/not-in-deck categories are left out (as `sync` ignores them).
- `scripts/pull_deck.py <id|url> [-o path]` writes `path` (`.txt`) and the `.md` beside it
  (no `.md` if the deck has no primer). Default path: `decks/commander/<slug>.txt` for
  format=commander, else `decks/<folder-slug>/<slug>.txt`. Overwrites without asking: Archidekt is
  canonical. Prints `dropped` formatting as a warning.
- `--folder ID` pulls every deck in that folder (`archidekt.folder(id)`), ~1 req/s.
- Header line: `# <site name> | <colors>`, then `# archidekt: <deck id>` (comment line; slice 04
  and `sync_deck.py` can use it to find the deck without an id argument — decide in slice 04).

**Brian sees:** `scripts/pull_deck.py https://archidekt.com/decks/27632721` → `decks/commander/q.txt`
+ `.md`; `git diff --no-index` against the old file shows header-only changes.

**Verify (live, read-only):**
- For every deck in Commander folder 1914431: pull to a temp dir, then
  `sync_deck.py <id> <tmp file> --dry-run` reports no removed/added/changed. Paste the table.
- Report every deck whose primer had `dropped` formatting.

**Delegated:** slug rules; the default path for non-Commander folders.

**Stays green:** `import_deck.py` with an Archidekt URL (it may delegate to `export`; one owner).
