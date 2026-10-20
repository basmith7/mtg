# 06 — Audit, backup, cutover

**Contract:** git tracks no deck files; nothing was lost doing it.

**Steps:**
1. **Audit (read-only):** for every ref from `git for-each-ref refs/heads refs/remotes refs/tags`
   (never `refs/t3`), confirm `.env` is in no reachable commit (`git log <refs> -- .env` empty), and
   grep `git log -p <refs>` for credential-shaped assignments (`password|token|secret|api_key` with
   a literal value). Don't read `.env` to get the real value (AGENTS.md); print commit + path only. A hit → stop and tell Brian (it would reopen the
   no-history-rewrite decision).
2. **Gate:** `verify_decks.py` over every `decks/**/*.txt` in the main checkout: all OK.
3. **Backup:** `tar czf ~/.cache/mtg-backups/decks-<stamp>.tgz -C ~/Projects/mtg decks`; list it
   back (`tar tzf | wc -l`).
4. **Gitignore:**
   ```
   decks/*
   !decks/PLAYLOG.md
   !decks/commander/
   decks/commander/*
   !decks/commander/RULES.md
   ```
   Check with `git check-ignore -v` on a list, a primer, `decks/ravnica/BUY_ALL.txt`, PLAYLOG, RULES.
5. `git rm -r --cached` every other path under `decks/`. One commit.

**Verify:** `git ls-files decks` prints exactly `decks/PLAYLOG.md` and `decks/commander/RULES.md`;
the main checkout still has every deck file after merging (untracking doesn't delete them in a
checkout that already has them — but **merging into a checkout deletes tracked files that the
merge removes**: before merging this PR in `~/Projects/mtg`, copy `decks/` aside or restore from
the tarball afterward, and check).

**Stays green:** `scripts/check_commander.py decks/commander/q.txt`, `deck_stats.py` on a local file.
