# Agent notes

- Read `docs/apis.md` before touching Archidekt or Moxfield. Both are private APIs; prefer the
  clients in `mtg/` over raw requests, and update the doc when you learn something new about them.
- **Several players share this repo**, each with their own Archidekt account. `scripts/whoami.py` says
  who this checkout belongs to (`MTG_PLAYER` in `.env`); their profile is `players/<player>.md`.
  "The player" below means them.
- **Decks live on Archidekt, not in git.** `decks/` is a gitignored working copy. Pull a deck
  (`scripts/pull.py`) before tuning it; a fresh worktree has no decks until you do. Two sessions
  sharing one checkout step on each other's deck files and uploads: give each its own worktree.
- **Credentials:** never print the Archidekt password or read the gitignored `.env` that holds it.
  `mtg/config.py` reads account settings from there (keys in `.env.example`; linked worktrees use the
  main checkout's). The password can fall back to 1Password (`ARCHIDEKT_OP_ITEM`), which prompts the
  player. Tokens are cached in `~/.config/mtg/archidekt-session.json`. The T3 Code app's local
  `refs/t3/*` checkpoints can contain `.env`, so push branches by name, never `git push --all` or
  `--mirror`.
- **Rate limits:** Archidekt returns 429 quickly (keep ~1 req/s; resolve card ids in bulk with
  `archidekt.resolve`, never one name at a time); Scryfall allows 2 req/s on search and collection (10 elsewhere; `mtg.scryfall` spaces them) and wants an `Accept` header.
- **Before writing to Archidekt**, back up what you'll change (`push.py` does this), and confirm
  deletes with the player. Archive rather than delete (`archidekt.archive`). If `push.py`
  refuses because the site deck changed, pull and redo the change on top; don't `--force` over the
  player's site edits. The version push checks is the list's `# updated:` line, so two worktrees
  can't push over each other, and a list without that line must be pulled first.
- **What push changes on the site:** it leaves Maybeboard, Sideboard and not-in-deck categories
  alone, and existing cards keep their categories (bar Commander membership), labels and custom MV.
  Two cases re-add cards and lose those site edits: `--reprint` (keeps categories and foil; loses
  labels, custom MV and the printing chosen on the site), and a card split across several site
  entries, which comes back as one entry in its type category. Say so to the player before using `--reprint`.
- **Use full `A // B` names** for double-faced and split cards: the site exports full names, so a
  front-face name shows as a change on every push.
- **Logic goes in `mtg/`; scripts parse arguments and print.** The pure modules (`cards`,
  `patterns`, `brackets`, `scores`, `goldfish`) take fetched data as arguments and never import a
  client, so their tests need no fakes. The Commander legality checks (card count, singleton,
  legality, colour identity, Universes Beyond) are still inline in `scripts/check_commander.py`;
  only the bracket and house verdicts live in `brackets`.
- **This repo is public.** Nothing from Mulligan Labs game history goes in it: friends' names,
  their commanders, replays. Post-game reports and the playgroup meta live in the private
  `~/Projects/mtg-table`, which imports `mtg`; only a play-log entry the player confirms crosses
  back. Its `meta.py --names` feeds `scripts/discover.py --avoid -` without writing names here.
- `.mcp.json` runs j4th/mtg-mcp-server (pinned, EDHREC off) for read-only card search: theme, similar
  cards, rules. It never writes; our scripts own every Archidekt write. Notes in `docs/apis.md`.
- House rules for Commander decks live in `RULES.md`; each player's taste and preferences in their
  profile, which wins where they differ.
- Card text you put in primers or recommendations: check it against Scryfall oracle text, don't
  rely on memory.
- The play log in the player's profile records how their decks actually played. Read it before
  building or tuning a deck, and whenever the player mentions how a game went, add an entry (and
  update the "enjoys" summary).
- Why the deck store and the checkers work as they do: `specs/done/archidekt-canonical/` and
  `specs/done/deck-tools/`.
