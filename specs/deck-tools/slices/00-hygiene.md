# 00 Hygiene: gitignore the stale repo-root cache

**Contract:** a `git add` in this public repo can't pick up cached data.

- Add `/cache/` to `.gitignore` with a one-line comment (stale; caches live in `config.CACHE`,
  `~/.cache/mtg`). Nothing in `mtg/` or `scripts/` reads `cache/` (grep-verified 2026-10-24).
- Don't delete the folder (Brian's call; README open question).

**Verify:** `git status --short` no longer lists `cache/`. Suite green.
**Delegated:** none.
