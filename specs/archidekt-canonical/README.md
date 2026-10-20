# Archidekt as the deck store, then go public

## Next Agent Prompt

_Last updated 2026-10-20._ Status: 01–04 done; 00's code done (gate waits on the roulette
session). Live Ravnica decks are the **power** versions (verified). Next: slice 00's gate, then 05.

You are implementing this spec in the worktree `~/Projects/mtg-public` (branch
`chore/public-archidekt`, from master). The main checkout `~/Projects/mtg` is shared with another
agent session that is uploading the roulette batch; don't edit files there until slice 00 passes.
Start at slice 00. Before ending a pass, tick the TODO below and rewrite this section with the next
pickup point.

- [ ] 00 Gate: roulette batch merged, `verify_decks.py` shows every local deck on Archidekt — [slices/00-gate-verify.md](slices/00-gate-verify.md)
- [x] 01 Config seam: account details out of code — [slices/01-config.md](slices/01-config.md)
- [x] 02 Decklist + primer round-trip, offline — [slices/02-roundtrip.md](slices/02-roundtrip.md)
- [x] 03 `pull_deck.py` (one deck or a whole folder) — [slices/03-pull.md](slices/03-pull.md)
- [x] 04 Stale-push guard on `sync` — [slices/04-stale-guard.md](slices/04-stale-guard.md)
- [ ] 05 Ravnica: primers to `.md`, upload Core decks — [slices/05-ravnica.md](slices/05-ravnica.md)
- [ ] 06 Audit, backup, cutover (gitignore + untrack) — [slices/06-cutover.md](slices/06-cutover.md)
- [ ] 07 Docs, LICENSE, skill workflow — [slices/07-docs.md](slices/07-docs.md)
- [ ] 08 Delete merged branches; flip public (gated) — [slices/08-publish.md](slices/08-publish.md)

Warnings: never print or `cat` `.env`; never `git push --all`/`--mirror` (local `refs/t3/*`
checkpoints contain `.env`); Archidekt writes only where a slice says so, back up first, never delete.

## Goal

Make `basmith7/mtg` public, and stop using git as the deck database. Decks live on Archidekt (the
copy Brian shares and may edit on the site). Local `decks/**` files remain the agents' working copy
but are gitignored. Code, docs, `decks/PLAYLOG.md` and `decks/commander/RULES.md` stay committed.

## Decisions (Brian, 2026-10-20)

- **Workflow:** local files are a gitignored working copy; Archidekt is canonical. Rejected: tools
  reading Archidekt ids directly with scratch files ("pull, edit, push" as the only path), and
  editing decks purely via API calls (hard to check a whole draft before it goes live).
- **Roulette batch** goes to the Commander folder (1914431); another session is uploading it now.
- **Ravnica Core** decks get uploaded as separate decks, "<Name> (Core)", folder 1914718.
- **PLAYLOG.md and RULES.md** stay committed and become public.
- **Hard cutover:** no compat shims, no migrations. Old decks stay in git history (no rewrite;
  they aren't sensitive).
- **Merged-branch deletion** approved ("Let's do all that"). **Flipping visibility** is not yet
  approved: ask Brian at slice 08.
- **LICENSE:** MIT.

## Synthesis notes (from three drafts: fewest slices, risk first, seam quality)

All three agreed: verify before untracking, a read-only compare script as the gate, pull as a new
script (not bolted onto `import_deck.py`'s foreign-site path), `.env.example`, named branch deletes.
Splits resolved:
- **1Password fallback:** keep it (Brian added it deliberately in PR #13), but the item id comes from
  `ARCHIDEKT_OP_ITEM` in `.env`; no item id in code or docs. Alternative (drop it) recorded, not taken.
- **Unsupported Quill ops on pull:** keep the text, drop the formatting, and print one warning per
  deck naming what was dropped. Failing hard would block pulling any deck Brian formatted on the
  site; silently degrading would hide it.
- **Stale-push guard:** included (risk-first draft) as its own slice; cheap and it protects
  Brian's site edits, which are the point of making Archidekt canonical.
- **Python-dict primers** (`decks/ravnica/primers_*.py`) convert to `.md` beside each list; one
  primer format. `upload_decks.py --primers` goes away.
- **Audit before cutover**, not after: a secret in history would change the no-rewrite decision.
- **Fresh worktrees have no decks** (gitignored files don't follow `git worktree add`), so pull
  must handle a whole folder, and `.env` must be found from a linked worktree.

## Single-owner invariants

- `mtg/config.py` is the only reader of `.env` / environment for account settings.
- `mtg/decklist.py` owns the decklist text format, both `parse` and `render`.
- `mtg/quill.py` owns markdown ↔ Quill delta, both directions.
- `mtg/archidekt.py` owns Archidekt deck JSON ↔ (name, commanders, cards, primer) mapping: `sync`
  (push), `export` (pull) and `compare`.

## Firewalls

- Main checkout files during slice 00; `refs/t3/*`; `.env` contents; git history (no rewrite, no
  force push); existing Archidekt decks except where slice 05 names them.

## Known unknowns

- The Archidekt field that marks last modification (`updatedAt`?) — slice 04 checks real JSON.

## Tests

The repo has no tests. Slices add `tests/` using stdlib `unittest`, offline, faking at
`archidekt.call` and `scryfall.collection`. Run: `python3 -m unittest discover tests`.
