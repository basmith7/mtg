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
