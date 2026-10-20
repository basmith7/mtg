# mtg

Python tools for building and tuning Magic: The Gathering decks, mostly Commander, around an
[Archidekt](https://archidekt.com) account. The tools pull decks down, check legality, combos and
mana, pull recommendations from EDHREC and Commander Spellbook, and push the changes back up. Standard
library only.

**Use at your own risk.** The Archidekt and Moxfield clients use private, reverse-engineered APIs (see
[docs/apis.md](docs/apis.md)). Those APIs can change without notice, and both sites rate-limit
quickly, so keep requests slow.

## Setup

Copy [.env.example](.env.example) to `.env` (gitignored) and fill in your own Archidekt account.
Linked git worktrees read the main checkout's `.env`. Card data comes from Scryfall and needs no
account.

## How decks are kept

Archidekt is where the decks live; this repo holds the tools. `decks/` is a local, gitignored working
copy:

1. **Pull** a deck, or a whole folder, with `scripts/pull_deck.py`. Each deck becomes a decklist
   `.txt` with its primer `.md` beside it. The `# source:` line in the list links it back to its deck.
2. **Tune** it locally with the checkers in `scripts/`.
3. **Push** it with `scripts/sync_deck.py`, or create a new deck with `scripts/upload_decks.py`.
   Sync backs up first, and it refuses to overwrite a deck that changed on the site since it was last
   pulled.

`scripts/verify_decks.py` compares local lists with the site, card for card.

What stays in git besides code: [decks/commander/RULES.md](decks/commander/RULES.md) (deck-building
rules) and [decks/PLAYLOG.md](decks/PLAYLOG.md) (how decks actually played).

## Layout

- **`mtg/`**: clients and formats. `archidekt`, `moxfield`, `scryfall`, `edhrec` and `spellbook`
  wrap one site each. `decklist` owns the decklist text format, `quill` owns primer markdown ↔
  Archidekt's rich text, and `config` reads account settings.
- **`scripts/`**: command-line tools. Each one's docstring is its usage (`--help`).
- **`docs/apis.md`**: what we know about each site's API. Read it before changing a client.
- **`.claude/skills/commander-deck`**: the agent workflow for building, tuning and uploading decks.
- **`tests/`**: offline tests. Run them with `python3 -m unittest discover tests`.

## License

[MIT](LICENSE).
