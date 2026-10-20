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

## Slices 05 and 07
- **The live Ravnica decks hold the power lists**, and `primers_core.py` held the power primers (named
  for the file, not the version). Core primers were written fresh from each Core list (a subagent,
  oracle text checked; one mana-cost slip fixed) because mechanically dropping lines that named
  missing cards left empty sections.
- **Core decks are named "<Name> (Core)"** in the header, so `sync` keeps that name.
- **`upload_decks.py` skips a name that already exists** (idempotent re-runs) and resolves every card
  before creating the deck (the other session's fix, adopted here).
- **README sheds the script/flag roster:** each script's docstring is its usage. Price-cache note
  moved into `check_decks.py`'s docstring.
- **LICENSE holder "basmith7"** (the GitHub account), MIT, 2026.

## Slices 06 and 09, and the roulette session's lessons
- **`decks/` is ignored wholesale** (PLAYLOG and RULES moved out), and `/cache` without a trailing
  slash so a worktree's `cache` symlink to the main checkout's cache is ignored too.
- **Profiles are named for `MTG_PLAYER`** (`players/brian.md`); "Universes Beyond: ask first" and
  "plays online" moved from the house rules into Brian's profile.
- **Folder ids are `.env` settings**, not docs; `upload_decks.py` and `pull_deck.py` default to
  `ARCHIDEKT_DECKS_FOLDER`.
- **The checker flags non-canonical names** (`use the full name: A -> A // B`): the old per-name card
  lookup couldn't find a double-faced card by its front face. Bulk resolve now can, but full names keep
  lists matching the site's export, so `verify` and `compare` don't report false differences.
- **PR #14's primer-audience rule ported** (primers never mention our tools); its deck files are
  redundant with Archidekt, so it can close unmerged.
- **Not built (noted in docs instead):** a `--primer-only` sync (pull-first plus "primer written only if
  changed" covers it), a cap on `check_commander.py --near` output, and deck_stats role-tag noise.
- **Tahngarth:** Tear Asunder (black kicker in an RG deck) swapped for Return to Nature before upload.
- **Anzrag** had an empty archived twin on Archidekt; the local file now carries the real deck's
  `# source:` line.
- **Card ids resolve through Archidekt's import parser** (`massDeckEdit`, what the editor's "Import
  cards" box calls): one ~1 s request per deck instead of ~1 req/s per card, the same printing the site
  picks, front-face names accepted, every missing card named in one error. Rejected: `cards/v2/?uids=`
  (needs a Scryfall round trip first, and picked a different printing for 18 of 83 cards) and a local
  card database such as MTGJSON or Scryfall bulk data (has no Archidekt ids, so it can't replace this
  call; our Scryfall use is a few cached requests per deck). The `archidekt_card_ids.json` cache goes.

## Start-over review (2026-10-20)

Brian: "is this how we would build everything if we started over? nothing is important so don't keep
it for tradition ... does everything earn its place?"
- **Stale guard moved into the file** (`# updated: <site updatedAt>`), replacing the per-machine
  `~/.cache/mtg/archidekt-seen.json`. The seen file tracked what the *machine* last saw, not what the
  *file* was based on: pull in two worktrees, push from one, and the other's older copy would push
  over it unrefused, which is the parallel-agent setup AGENTS.md recommends.
- **One push command.** `sync_deck.py`, `upload_decks.py` and `verify_decks.py` became `push.py`: a
  list with a `# source:` line updates its deck, one without creates the deck (refusing if the name is
  already on the account), `--dry-run` over many lists replaces verify. `pull_deck.py` became `pull.py`.
  `archidekt.compare` went (a second diff that had to agree with `sync`'s). Dropped flags with no use:
  `--primer <path>`, `--no-rename`, `--deck`. Pull no longer matches local files by name (migration-era).
- **Deleted, recoverable from git:** `sim_q.py` (352 lines hard-coded to one deck), the Ravnica paper
  tooling (`check_decks.py` pricing/proxy lists, `build_pool.py`, `scryfall.set_pool`/`cheapest_usd`),
  unused client functions (Archidekt collection, folder tree/create, tags; Moxfield collection;
  `scryfall.named`) and the settings only they read (`ARCHIDEKT_USER_ID`, `ARCHIDEKT_IDEAS_FOLDER`,
  `MOXFIELD_*`).
- **One cache dir**, `~/.cache/mtg` (EDHREC pages, role tags, deck backups), so worktrees share it
  without the repo `cache/` symlink.
- **Kept on purpose:** stdlib-only scripts with a `sys.path` line (zero install for friends beats a
  packaged CLI), the `| COLOURS` header (useful at a glance; dropping it would mean re-pulling every
  copy), the Instagram importer (works, isolated), deck_stats' 60-card mode (a few lines, Ravnica decks
  still exist).
