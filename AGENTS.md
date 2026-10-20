# Agent notes

- Read `docs/apis.md` before touching Archidekt or Moxfield. Both are private APIs; prefer the
  clients in `mtg/` over raw requests, and update the doc when you learn something new about them.
- **Decks live on Archidekt, not in git.** `decks/` is a gitignored working copy (only
  `decks/PLAYLOG.md` and `decks/commander/RULES.md` are committed). Pull a deck
  (`scripts/pull_deck.py`) before tuning it; a fresh worktree has no decks until you do.
- **Credentials:** never print the Archidekt password or read the gitignored `.env` that holds it.
  `mtg/config.py` reads account settings from there (keys in `.env.example`; linked worktrees use the
  main checkout's). The password falls back to 1Password, which prompts Brian. Tokens are cached in
  `~/.config/mtg/archidekt-session.json`.
- **Rate limits:** Archidekt's card lookup returns 429 quickly (keep ~1 req/s, use the id cache);
  Scryfall wants ~10 req/s max and an `Accept` header.
- **Before writing to Archidekt**, back up what you'll change (`sync_deck.py` does this), and confirm
  deletes with Brian. Archive rather than delete. If `sync_deck.py` refuses because the site deck
  changed, pull and redo the change on top; don't `--force` over Brian's site edits.
- Deck-building rules live in `decks/commander/RULES.md`. Brian plays Commander online; paper decks
  are rare and get their own rules when they come up.
- Card text you put in primers or recommendations: check it against Scryfall oracle text, don't
  rely on memory.
- `decks/PLAYLOG.md` records how decks actually played. Read it before building or tuning a deck,
  and whenever Brian mentions how a game went, add an entry (and update the "enjoys" summary).
