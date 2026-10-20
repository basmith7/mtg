# Agent notes

- Read `docs/apis.md` before touching Archidekt or Moxfield. Both are private APIs; prefer the
  clients in `mtg/` over raw requests, and update the doc when you learn something new about them.
- **Several players share this repo**, each with their own Archidekt account. `scripts/whoami.py` says
  who this checkout belongs to (`MTG_PLAYER` in `.env`); their profile is `players/<player>.md`.
  "The player" below means them.
- **Decks live on Archidekt, not in git.** `decks/` is a gitignored working copy. Pull a deck
  (`scripts/pull_deck.py`) before tuning it; a fresh worktree has no decks until you do. Two sessions
  sharing one checkout step on each other's deck files and uploads: give each its own worktree.
- **Credentials:** never print the Archidekt password or read the gitignored `.env` that holds it.
  `mtg/config.py` reads account settings from there (keys in `.env.example`; linked worktrees use the
  main checkout's). The password can fall back to 1Password (`ARCHIDEKT_OP_ITEM`), which prompts the
  player. Tokens are cached in `~/.config/mtg/archidekt-session.json`.
- **Rate limits:** Archidekt's card lookup returns 429 quickly (keep ~1 req/s, use the id cache);
  Scryfall wants ~10 req/s max and an `Accept` header.
- **Before writing to Archidekt**, back up what you'll change (`sync_deck.py` does this), and confirm
  deletes with the player. Archive rather than delete (`archidekt.archive`). If `sync_deck.py`
  refuses because the site deck changed, pull and redo the change on top; don't `--force` over the
  player's site edits.
- House rules for Commander decks live in `RULES.md`; each player's taste and preferences in their
  profile, which wins where they differ.
- Card text you put in primers or recommendations: check it against Scryfall oracle text, don't
  rely on memory.
- The play log in the player's profile records how their decks actually played. Read it before
  building or tuning a deck, and whenever the player mentions how a game went, add an entry (and
  update the "enjoys" summary).
