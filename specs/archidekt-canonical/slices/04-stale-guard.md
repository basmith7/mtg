# 04 — Don't push over newer site edits

**Contract:** `sync` refuses to overwrite a deck Brian changed on archidekt.com since the local copy
was pulled or last pushed.

**Seam:** first check a real `deck()` JSON for the modification timestamp field (likely
`updatedAt`) and record it in `docs/apis.md`. Store `{deck_id: timestamp}` in
`cache/archidekt_seen.json` (gitignored), written by `pull_deck.py` and after a successful
`sync`. `archidekt.sync(..., force=False)` raises before any write if the site timestamp is newer
than the stored one; a deck with no stored stamp is treated as stale (pull first).
`sync_deck.py --force` overrides. `upload_decks.py` records the stamp of decks it creates.

Also: `sync` writes the primer only when it differs from the site's (compare `to_delta` of both
after `from_delta`); 14 site primers carry formatting markdown can't hold and must not be flattened
by an unchanged push. When the primer did change and the site's has dropped formatting, refuse unless
`--force`, naming what would be lost. `sync_deck.py` takes the deck from the file's `# source:` URL
when no id is given.

**Verify:** `tests/test_sync_guard.py` with `archidekt.call` faked: stale → raises, nothing
written; fresh → proceeds; `force` → proceeds. Live: pull a deck, `sync --dry-run` passes the guard.

**Delegated:** cache file shape; error wording.

**Stays green:** `sync` backups and post-write verification.
