# Archidekt holds the decks

Shipped 2026-10-20 (PR #15), then the repo went public for Brian's playgroup.

## What it is

Decks live on Archidekt, the copy players share and edit on the site. This repo holds the tools,
the house rules (`RULES.md`) and one profile per player (`players/`). `decks/` is a gitignored local
working copy: `scripts/pull.py` brings decks down as a decklist `.txt` plus a primer `.md`, the
checkers in `scripts/` run on those files, and `scripts/push.py` sends them back up (creating the deck
for a new list). Each player's account and folders come from their own `.env` (`.env.example`,
checked by `scripts/whoami.py`).

## Why this shape

- **Archidekt is canonical, files are a working copy.** Git as the deck database meant two copies
  drifting, and Brian edits decks on the site. Rejected: tools that edit decks purely through API
  calls (a whole draft can't be checked before it goes live) and pull-edit-push on scratch files only
  (the checkers and agents want stable paths).
- **Hard cutover.** No compatibility shims; old deck files stay in git history unrewritten (nothing
  sensitive in them).
- **Shared rules, personal profiles.** House rules apply to everyone; taste, preferences and the
  play log are per player and win where they differ.
- **A start-over pass** cut what didn't earn its place (a one-deck simulator, paper pricing tools,
  unused client code); see "Start-over review" in [choices.md](choices.md).

## Invariants

- **A push never overwrites site edits it hasn't seen.** Each list records the site version it
  came from (`# updated:`); `archidekt.sync` refuses when the site's `updatedAt` differs, checked at
  push time before any write (`--force` overrides). The version lives in the file, not on the machine, so two worktrees can't push over each
  other. Pinned by `tests/test_sync.py`.
- **Nothing half-written.** Every new card id resolves (`archidekt.resolve`) before the first write;
  the deck JSON is backed up to `~/.cache/mtg/backups/` first; the deck is re-read afterwards and
  `match` says whether the card quantities agree.
- **Push leaves the site's own structure alone:** Maybeboard, Sideboard and not-in-deck categories
  are skipped (`archidekt.main_cards`), existing cards keep their categories (except a card split across
  several entries, which is rebuilt as one), and only Commander membership is enforced. A primer is written only when it differs, and refused if it would drop
  site formatting the light markdown can't hold (`quill.from_delta` reports it).
- **One owner each:** `mtg/config.py` reads settings and `.env` (never printing values; linked
  worktrees read the main checkout's); `mtg/decklist.py` the list format, both directions;
  `mtg/quill.py` primer markdown ↔ Quill delta; `mtg/archidekt.py` deck JSON ↔ list (`export` for
  pull, `sync` for push).
- **Credentials never in git:** `.env` is ignored; local `refs/t3/*` checkpoints contain it, so never
  `git push --all` or `--mirror`.

## Dead ends

- **Per-machine "seen" stamps** for the stale guard: a pull in one worktree made another worktree's
  older copy look fresh.
- **Per-name card id lookup** (~1 request/s, 429s, no front-face names) and the `uids=` bulk route
  (a Scryfall round trip, different printings): replaced by the site's own import parser.
- **A local card database** (MTGJSON, Scryfall bulk): has no Archidekt ids.
- **Matching local files to decks by name:** ambiguous with archived twins; the `# source:` line is
  the only link.

Every decision made along the way, with verdicts from the pre-merge audit, is in
[choices.md](choices.md).
