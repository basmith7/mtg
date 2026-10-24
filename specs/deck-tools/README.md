# deck-tools: tools that make Commander decks more fun and better

Goal: twelve additions, picked from research on 2026-10-23 and approved by Brian with "do it all":
a bracket check, a table-feel (salt) check, hidden-gem ranking, commander discovery, an originality
score, a better goldfish and mana check, primer extras, challenge decks, a Mulligan Labs post-game
report, a playgroup meta, the j4th/mtg-mcp-server, and Forge AI-vs-AI pods of the player's own decks.

## Next Agent Prompt

Status 2026-10-24: spec written; no slice implemented. Branch `feat/deck-tools` (off
`docs/mulligan-labs`, whose Mulligan Labs API doc this spec relies on).

You are implementing this spec with the `implement-spec` skill. Start at the first unchecked slice
below; each slice file is self-contained. Run `python3 -m unittest discover tests` before and after
every slice. Commit per slice, staging only your own files (never `git add -A`). Before ending a pass,
tick the boxes below, update this status paragraph and the next pickup point.

Warnings:
- The repo is **public**. Read "Firewalls" before slices 11–12.
- `cache/` at the repo root is a stale pre-`config.CACHE` leftover (17 MB, untracked). Slice 00
  gitignores it; deleting it is Brian's call.

- [x] [00 hygiene](slices/00-hygiene.md)
- [x] [01 seams](slices/01-seams.md)
- [ ] [02 bracket check](slices/02-bracket.md)
- [ ] [03 table feel](slices/03-table-feel.md)
- [ ] [04 hidden gems](slices/04-gems.md)
- [ ] [05 originality and synergy density](slices/05-originality.md)
- [ ] [06 goldfish and mana](slices/06-goldfish.md)
- [ ] [07 discovery and challenges](slices/07-discovery.md)
- [ ] [08 primer extras and challenger review](slices/08-primer.md)
- [ ] [09 MCP server](slices/09-mcp.md)
- [ ] [10 Forge pods](slices/10-forge.md)
- [ ] [11 post-game report (mtg-table)](slices/11-postgame.md)
- [ ] [12 playgroup meta (mtg-table)](slices/12-meta.md)

## Slice graph

```
00 ── 01 ─┬─ 02 ── 03 ──┐
          ├─ 04 ── 05   ├─ 08
          ├─ 06 ────────┘
          └─ 10
07 (needs 01: mtg/patterns)        09 (independent)
11 ── 12 ── (12 feeds 07's --avoid)
```

Slices 09, 10 and 11 each start with a spike and a kill criterion; a killed slice is recorded here
with its evidence, not forced.

## Decisions (with the alternative that lost)

- **Two bracket labels.** Official Bracket 3 allows at most 3 Game Changers, so RULES.md's "around 4"
  is officially B4. Tools print the official bracket, Spellbook's tag and the house verdict side by
  side. RULES.md is unchanged until Brian answers the open question below.
- **Spellbook's tag is information, not a verdict.** Probed 2026-10-24: `/estimate-bracket` uses its own
  scale (`E C O P S R B`, names in `spellbook.BRACKET_TAGS`); 4 Game Changers → `R`, Winter Orb alone →
  `R`, Time Warp alone → `C`. Its per-card (`gameChanger`, `massLandDenial`, `extraTurn`) and per-combo
  (`definitelyTwoCard`, `speed`, `lock`) flags feed our official count instead.
- **Table feel is its own script** (`scripts/table_feel.py`), not a `check_commander` flag:
  `check_commander` stays a rules checker whose `!!` lines mean "breaks the house rules". (Lost: one
  combined check, drafter A.)
- **Discovery is a section of the `commander-deck` skill**, not a new skill: one skill owns the
  deckbuilding workflow, and its description gains "find me a commander". (Lost: a separate
  `commander-discovery` skill, drafter B.)
- **Challenges live in `mtg/discovery.py`** (`discover.py --challenge`): both pick a starting point
  for a new deck from Scryfall queries.
- **Logic lives in `mtg/`, scripts parse arguments and print.** New pure modules never import `http`.
- **Mulligan Labs tooling lives in `~/Projects/mtg-table`** (local git, no remote). The public repo
  never imports it or names it; mtg-table imports `mtg` the way `look` does.
- **Forge and the MCP server are experiments** with kill criteria (slices 09, 10). Neither is a system
  package: Forge unpacks under `~/.local/share/forge`, the MCP server runs through `uvx`.
- **No backward compatibility, no migrations.** `deck_stats.py` output may change shape in slice 06.

## Single-owner invariants

| Concept | Owner |
|---|---|
| Oracle-text patterns (MLD, extra turns, stax, theft, donate, goad, vote, coin, monarch, "each opponent") | `mtg/patterns.py` (pure) |
| Scryfall otag roles and their cache | `mtg/roles.py` |
| Official bracket criteria, house verdict, the FAST-combo rule | `mtg/brackets.py` (pure) |
| Spellbook HTTP | `mtg/spellbook.py` |
| EDHREC HTTP and page fields (`lift`, `trend_zscore`, salt) | `mtg/edhrec.py` |
| Scores derived from EDHREC data (gems, staple share, salt summary, overlap, density) | `mtg/scores.py` (pure) |
| Goldfish simulation and source-count table | `mtg/goldfish.py` (pure, seeded rng) |
| Player profile format (enjoys lines, play-log entry) | `mtg/profile.py` |
| Discovery mechanics queries and challenge rolls | `mtg/discovery.py` |
| Our list → Forge `.dck` and Forge output parsing | `mtg/forge.py` |
| Replay fetch, cache and parsing; playgroup meta | `mtg-table/replays.py`, `mtg-table/meta.py` |

## Firewalls

1. Nothing derived from Mulligan Labs game history (replays, other players' names or commanders, the
   meta) is written under `~/Projects/mtg` or committed anywhere. Replays cache in
   `mtg-table/replays/` (gitignored). Tests use invented seats ("Seat A").
2. The only crossing into the public repo is a play-log entry for the player's own deck, which the
   player confirms and which names no other player.
3. Mulligan Labs: read-only, low volume, only when the player asks (building slice 11 counts: one
   fetch of the player's own game history to verify it). Never game actions, never a seat, no AI player.
4. The MCP server is read-only use; `push.py` owns every Archidekt write.
5. Secrets only through `mtg.config`; never print `.env` values. `.mcp.json` holds no secrets.
6. Primers never mention tools.

## Fixtures

`tests/fixtures/` (new): trimmed real responses, captured once per slice and named for their source
(`spellbook_estimate_*.json`, `edhrec_commander_*.json`, `edhrec_salt_top.json`, `scryfall_cards.json`,
`forge_sim_*.txt`). Network seams are faked with `mock.patch.object` on `spellbook.http.request`,
`edhrec._fetch`, `scryfall.collection` / `scryfall.search`, as the suite already does for
`archidekt.call`.

## Every slice keeps green

- `python3 -m unittest discover tests`.
- `check_commander.py`'s combo and `!!` lines (primers take combo claims from them).
- Script docstrings are their usage; ARCHITECTURE.md codemap and `docs/apis.md` updated when a slice
  adds a module or learns an endpoint.
- Standard library only in repo code.

## Review checkpoints (non-blocking)

Show evidence, wait ~5 minutes, then decide on the evidence and record it in the slice file.
- 02: the bracket line on three of Brian's decks.
- 03: the tone of the Rule 0 pitch.
- 06: the source-count table's provenance.
- 08: the primer word budget.
- 10: Forge go / no-go after the spike.
- 11: the privacy audit (`git -C ~/Projects/mtg status` clean of replay data).

## Open questions for Brian

- **Game Changer cap:** keep "around 4" (officially B4, called 3.75) or cap at 3 (truly B3)? Default:
  keep; tools print both labels.
- **Stale `cache/`** at the repo root: delete it? Default: leave it, gitignored.

## Research and sources

- Research ranking and outside-tool notes: [brief.md](brief.md) (the interview brief; superseded by
  this README where they differ).
- WotC Brackets update 2026-02-09:
  https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-february-9-2026
- EDHREC salt 2026: https://edhrec.com/articles/salt-vote-results-2026
- j4th/mtg-mcp-server: https://github.com/j4th/mtg-mcp-server (MIT, PyPI 3.0.0, Python ≥3.12)
- Forge: https://github.com/Card-Forge/forge (`forge-gui-desktop/.../SimulateMatch.java`)
- Ideas: dreliq9/urza (pairwise interaction density), QuackQuackLabs/MTG-Analyzer (goldfish outputs),
  P47Phoenix/Claude-Plugins (challenger review), TytaniumDev/MagicBracketSimulator (Forge pods; no
  license, read only).
