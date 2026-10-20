# 00 — Gate: every local deck is on Archidekt

**Contract:** a read-only answer to "is every local deck on Archidekt, card for card?" It gates
slice 06 (untracking) and settles which Ravnica version is live.

**Seam:**
- `mtg/archidekt.py`: rename `_main` → `main_cards` (public; `sync` uses it). Add
  `compare(local_path, deck_json) -> dict` with keys `missing_on_site`, `extra_on_site`,
  `qty_diffs` (cards), `commander_diff`, and `primer` (`'same' | 'differs' | 'none_local' | 'none_site'`,
  compared after normalising whitespace; full primer equality waits for slice 02's `from_delta`,
  so until then report only presence).
- `scripts/verify_decks.py [paths...] [--folder ID ...]`: default paths `decks/**/*.txt`. Matches
  each file to a site deck by the `# Name` header among `my_decks()`. Prints one line per deck:
  `OK`, `MISSING`, `DIFFERS (+n −m)`, `AMBIGUOUS` (two site decks share the name). Exit 1 on
  anything but OK. Read-only: `my_decks()` and `deck()` only, ~1 req/s.

**Gate steps (no code):**
1. The other session (thread "Commander Deck Around Attached Leader") reports the roulette batch
   uploaded and `deck/roulette-batch` merged to master. Rebase this branch onto master.
2. Run `verify_decks.py` from the main checkout's `decks/` (pass paths; the worktree has the same
   files until slice 06). All Commander decks must be OK.
3. Run it on `decks/ravnica/core/*.txt` and `decks/ravnica/power/*.txt`: one set should be OK
   and the other DIFFERS. Record which in the README "Known unknowns".

**Brian sees:** the verify table.

**Verify:** unit test `compare` with a fixture deck JSON (save one real `deck()` response, trimmed,
under `tests/fixtures/`) against a matching and a perturbed decklist.

**Delegated:** output formatting; fixture trimming.

**Stays green:** `sync_deck.py --dry-run` on any deck gives the same result as before the rename.
