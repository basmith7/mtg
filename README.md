# mtg

A playgroup's Python tools for building and tuning Magic: The Gathering decks, mostly Commander, each
player working with their own [Archidekt](https://archidekt.com) account. The tools pull decks down,
check legality, combos and mana, pull recommendations from EDHREC and Commander Spellbook, and push the
changes back up.

**Use at your own risk.** The Archidekt and Moxfield clients use private, reverse-engineered APIs (see
[docs/apis.md](docs/apis.md)). Those APIs can change without notice, and both sites rate-limit
quickly, so keep requests slow.

## Setup

1. Copy [.env.example](.env.example) to `.env` (gitignored) and fill in your player name, Archidekt
   account and folder ids. Linked git worktrees read the main checkout's `.env`.
2. Add your profile, `players/<your name>.md` (see [players/](players/README.md)).
3. Run `scripts/whoami.py`: it checks the login and prints your folders.

Python 3 (developed on 3.14), standard library only; card data comes from Scryfall and needs no account. The tools are
built to be driven by an AI agent ([AGENTS.md](AGENTS.md) and the `commander-deck` skill), but every
script also runs by hand.

## How decks are kept

Archidekt is where the decks live; this repo holds the tools. `decks/` is a local, gitignored working
copy:

1. **Pull** a deck, or a whole folder, with `scripts/pull.py`. Each deck becomes a decklist `.txt`
   with its primer `.md` beside it. The list's `# source:` line links it to its deck, and `# updated:`
   records which version of the deck it is.
2. **Tune** it locally with the checkers in `scripts/`.
3. **Push** it with `scripts/push.py`, which also creates the deck for a new list. Push backs up
   first, and refuses to overwrite a deck that changed on the site since the list's version.
   `--dry-run` shows what differs, for one list or all of them.

What stays in git besides code: [RULES.md](RULES.md), the playgroup's house rules for Commander decks,
and [players/](players/README.md), one profile per player with their taste and play log.

## Layout

[ARCHITECTURE.md](ARCHITECTURE.md) is the map: how the parts fit and what must stay true.

- **`mtg/`**: clients and formats. `archidekt`, `moxfield`, `scryfall`, `edhrec` and `spellbook`
  wrap one site each. `decklist` owns the decklist text format, `quill` owns primer markdown ↔
  Archidekt's rich text, and `config` reads account settings.
- **`scripts/`**: command-line tools. Each one's docstring is its usage (`--help`).
- **`docs/apis.md`**: what we know about each site's API. Read it before changing a client.
- **`.claude/skills/commander-deck`**: the agent workflow for building, tuning and uploading decks.
- **`tests/`**: offline tests. Run them with `python3 -m unittest discover tests`.

## License

[MIT](LICENSE).
