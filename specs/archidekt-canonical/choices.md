# Choices made where the spec was silent

## Slices 01–02
- **`.env` location from a linked worktree:** `config.env_file()` asks git for the common dir and
  uses its parent; cached per process. Fallback: the package's repo root. Sound: worktrees then
  need no setup.
- **Missing key error type:** `KeyError` naming the key and `.env.example`, never the value.
- **`color_identity` placement:** `mtg/scryfall.py` (it's a Scryfall lookup), not `decklist`.
- **Dropped-formatting names:** attribute names as Quill spells them, with values for line formats
  (`header:4`, `list:ordered`), and `embed` for non-text inserts.
- **Round-trip contract is delta-level:** `to_delta(from_delta(to_delta(md))) == to_delta(md)`.
  Site-written primers can gain blank lines on their first pull and push (our markdown has no single
  line break); verified stable after that on deck 25855165.
- **Tests read the local working copy's primers when present** (32 today); after the cutover a fresh
  clone tests only the built-in sample.

## Slices 00 (code) and 03
- **One owner for deck JSON → decklist:** `archidekt.main_cards` / `export` replace both `_main` and
  `importdeck.from_archidekt`'s own filter. The merged filter skips deleted entries and compares
  category names case-insensitively, as `from_archidekt` did; `sync` now ignores deleted entries too.
- **Deck link in the file:** the existing `# source: <archidekt url>` line, not a new `# archidekt:` line.
  `pull_deck.py` writes it; `verify_decks.py` (and slice 04's `sync_deck.py`) read it.
- **Pull target without `-o`:** the local file whose source URL, then `# Name` header, matches; else
  `decks/commander/<commander>.txt` (name before " – ") or `decks/<name>.txt`. Pull sorts cards
  alphabetically, so a hand-ordered list loses its order on first pull.
- **Pull removes a stale `.md`** when the site deck has no primer (Archidekt is canonical).
- **`archidekt.folder` pages** through `next`; the Commander folder already holds 62 decks.
- **`archidekt.deck_id(ref)` / `url(id)`** replace three hand-built URL strings and `sync_deck.py`'s regex.

## Slice 04
- **Seen-stamps live in `~/.cache/mtg/archidekt-seen.json`**, not repo `cache/`: per machine, so a
  pull in the main checkout covers a sync from a worktree.
- **No stamp counts as stale.** The first sync of any deck after this lands needs a pull (or `--force`).
- **Dry runs never refuse;** they report `stale` and `primer_loses` as warnings.
- **`sync_deck.py` takes the decklist first and the deck as `--deck`**, defaulting to the file's
  `# source:` URL (hard cutover of the old `<deck> <decklist>` order).
- **`upload_decks.py` writes `# source:` into the uploaded file** so sync finds the new deck.
- **The stamp is recorded only when the post-sync re-read matches**; a mismatch leaves the deck stale.
