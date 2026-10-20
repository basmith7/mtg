# 09 — A playgroup, not one player

Added 2026-10-20 after Brian set the audience: friends building decks the same way, each with their
own Archidekt account. Decision (Brian): shared house rules plus a committed profile per player.
Rejected: personal files gitignored (nothing shared or backed up), and "keep it Brian's, friends fork".

**Contract:** a friend can clone, fill `.env`, add `players/<name>.md`, and use every tool and the skill
without anything pointing at Brian's account.

**Seam:**
- `RULES.md` (repo root): the playgroup's house rules. `players/<MTG_PLAYER>.md`: taste, preferences
  beyond the rules, "enjoys" summary and play log; the profile wins where they differ.
  `players/README.md` says what a profile holds.
- `.env`: `MTG_PLAYER`, `ARCHIDEKT_DECKS_FOLDER` (default for upload and pull), `ARCHIDEKT_IDEAS_FOLDER`,
  `ARCHIDEKT_ARCHIVE_FOLDER` (`archidekt.archive`).
- `scripts/whoami.py`: player, profile present, account, folder names (proves login). Agents can't read
  `.env`, so this is how the skill learns who it's working for.

**Verify:** `scripts/whoami.py` exits 0 with Brian's `.env`; `git grep -n Brian -- ':!specs' ':!players'`
returns nothing.
