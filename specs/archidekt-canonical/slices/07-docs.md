# 07 — Docs, LICENSE, workflow

**Contract:** a stranger can understand and run the repo; agents follow the new workflow.

- `LICENSE`: MIT, copyright holder "basmith7" (GitHub account; Brian can change it), 2026.
- `README.md`: 3–5 line intro for strangers above the current content: what it is; bring your own
  Archidekt account (`.env.example`); Archidekt/Moxfield clients use private, reverse-engineered
  APIs, use at your own risk and gently (rate limits). State that decks live on Archidekt and
  `decks/` is a local, gitignored working copy (`pull_deck.py` to fill it). Drop the Ravnica
  `--primers` example; update the scripts list (`pull_deck.py`, `verify_decks.py`).
- `AGENTS.md`: decks aren't committed; pull before tuning; `.env` keys.
- `.claude/skills/commander-deck/SKILL.md`: before tuning an existing deck, `pull_deck.py` it.
  New deck: draft locally, upload. Finishing: sync to Archidekt (guarded), report the link; commit
  only code/docs/PLAYLOG/RULES changes. Remove "commit the deck files on a branch and open a PR".
- `docs/apis.md`: pull, the timestamp field, `.env` keys.
- Run `write-docs` over README.

**Verify:** `git grep` for the ids → none; README links resolve.

**Delegated:** wording.
