# 01 — Config seam: account details out of code

**Contract:** no personal ids in tracked files; one module reads account settings.

**Seam:** new `mtg/config.py`, `get(key, required=True) -> str | None`. Order: `os.environ`, then
`.env` at the root of the **main** checkout (resolve via `git rev-parse --git-common-dir` so linked
worktrees find it; fall back to the repo root of the package). Missing required key raises
`KeyError`-style error naming the key and pointing at `.env.example`; never includes values.
Keys:
- `ARCHIDEKT_USERNAME`, `ARCHIDEKT_USER_ID`, `ARCHIDEKT_PASSWORD`
- `ARCHIDEKT_OP_ITEM` (optional; 1Password fallback for the password, as today)
- `MOXFIELD_USERNAME`, `MOXFIELD_COLLECTION_ID` (optional)

`mtg/archidekt.py` drops `USERNAME`, `USER_ID`, `OP_ITEM`, `ENV_FILE` and reads `config.get` inside
functions (not at import, so `import mtg.archidekt` works without `.env`). `mtg/moxfield.py` drops
`USERNAME`, `COLLECTION_ID`; `public_decks(username=None)` defaults from config.

**Brian's `.env`:** append the new keys without reading the file:
`printf` the five `KEY=value` lines `>> .env` in the main checkout
(values from the current code before deleting it). Confirm with `grep -c '^ARCHIDEKT_USERNAME=' .env`
(prints a count, not a value). Commit `.env.example` with key names and placeholder values.

**Docs:** `docs/apis.md` loses the username, user id and both 1Password item ids; it names the
`.env` keys instead. (Slice 07 does the rest of the docs.)

**Verify:**
- `tests/test_config.py`: env wins over file; file parsed with quotes; missing key error has no value.
- `git grep` for the old username, user id and item ids on tracked files: no hits.
- Live read probe from the worktree: `python3 -c "from mtg import archidekt; print(len(archidekt.my_decks()))"`.

**Delegated:** hand-rolled `.env` parser (no new dependencies); function names inside `config`.

**Stays green:** login, refresh, `my_decks`, `moxfield.public_decks()`.
