# 04 — Don't push over newer site edits

**Contract:** `sync` refuses to overwrite a deck Brian changed on archidekt.com since the local copy
was pulled or last pushed.

**Seam:** first check a real `deck()` JSON for the modification timestamp field (likely
`updatedAt`) and record it in `docs/apis.md`. Store `{deck_id: timestamp}` in
`cache/archidekt_seen.json` (gitignored), written by `pull_deck.py` and after a successful
`sync`. `archidekt.sync(..., force=False)` raises before any write if the site timestamp is newer
than the stored one; a deck with no stored stamp is treated as stale (pull first).
`sync_deck.py --force` overrides. `upload_decks.py` records the stamp of decks it creates.

Decide: whether `sync_deck.py` takes the id from the `# archidekt: <id>` header (slice 03) when no
id is given. Recommended yes; one less thing to get wrong.

**Verify:** `tests/test_sync_guard.py` with `archidekt.call` faked: stale → raises, nothing
written; fresh → proceeds; `force` → proceeds. Live: pull a deck, `sync --dry-run` passes the guard.

**Delegated:** cache file shape; error wording.

**Stays green:** `sync` backups and post-write verification.
