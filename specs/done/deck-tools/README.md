# Deck tools: checks and finders for fun Commander decks

Shipped 2026-10-24 on branch `feat/deck-tools`, from a research pass Brian answered with "do it all".
Decisions made without him are in [choices.md](choices.md).

## What it is

Tools an agent uses while building a deck so the result is fun at the table, not only legal and
efficient:

- **Bracket line** in `scripts/check_commander.py`: the official WotC bracket, Commander Spellbook's tag
  and the house verdict side by side (`Official B4 (4 Game Changers) · Spellbook R · House 3.75 ✓`).
- **Table feel** (`scripts/table_feel.py`): salt, how much of the deck touches other players, stax /
  theft / goad / land-destruction / extra-turn counts, and a one-sentence Rule 0 pitch.
- **Hidden gems** (`scripts/edhrec_recs.py --gems`): cards that fit a commander unusually well (EDHREC
  `lift`) but few decks play.
- **Originality** (`scripts/originality.py`): the share of the 99 that is the commander's staples,
  overlap with the player's other decks, synergy density, and odd same-job swaps.
- **Goldfish and mana** (`scripts/deck_stats.py`): colour-aware draws, the free first mulligan,
  keepable sevens, a recast after removal, and colour sources judged against Karsten's table.
- **Discovery and challenges** (`scripts/discover.py`): underplayed commanders for the mechanics in the
  player's "enjoys" bullets, or a rolled challenge brief whose pool `check_commander.py --pool` enforces.
- **Primer format** (RULES.md): a signature turn, a Mulligan bullet, a Politics bullet, and a fresh-eyes
  subagent review before push (`.claude/skills/commander-deck/SKILL.md`).
- **Outside tools:** the j4th/mtg-mcp-server (`.mcp.json`, read-only search tools) and Forge AI-vs-AI
  pods of the player's own decks (`scripts/forge_sim.py`, `docs/forge.md`).
- **Private, in `~/Projects/mtg-table`:** a post-game report and a playgroup meta from Mulligan Labs
  replays (`replays.py`, `postgame`, `meta.py`).

## Why this shape

- **Two bracket labels.** Official Bracket 3 allows at most 3 Game Changers, so the house's "around 4"
  is officially B4. Printing both keeps the pregame conversation honest without changing the house
  rule; RULES.md says `Official B4 · House 3.75 ✓` is a normal result.
- **Spellbook informs, our code decides.** `/estimate-bracket` uses its own scale (4 Game Changers or
  Winter Orb alone → Ruthless), so only its per-card and per-combo flags feed `brackets.official`.
- **Table feel is its own script.** `check_commander.py`'s `!!` lines mean "this list has a problem"
  (legality, colour, a house rule); salt and solitaire play are judgement calls, not problems.
- **One skill owns deckbuilding.** Discovery, gems, table feel and originality are steps in
  `commander-deck`, not separate skills.
- **Logic in `mtg/`, scripts print.** Pure modules (`cards`, `brackets`, `patterns`, `scores`,
  `goldfish`) never import `mtg.http`, so tests run offline on plain dicts; network clients
  (`scryfall`, `edhrec`, `spellbook`) do no scoring.
- **Fetch once, cache wide.** Salt comes from MTGJSON (one weekly download reduced to a 0.9 MB table)
  rather than ~85 EDHREC card pages per deck; discovery ranks by Scryfall's `edhrec_rank` and spends
  EDHREC requests only on `--counts`.
- **Experiments carried kill criteria.** The MCP server and Forge each started with a spike that could
  have ruled them out; both survived (numbers below).

## Invariants

Enforced by structure or code:

- **Nothing from Mulligan Labs game history enters this public repo**: no replays, other players'
  names or commanders, game ids or meta. That tooling lives in `~/Projects/mtg-table` (no remote,
  `replays/` gitignored) and imports `mtg`, never the reverse. Tests use invented seats.
- **Every bracket `!!` comes from `brackets.house`**; the fast-infinite-combo rule is
  `brackets.is_fast` (pieces total 6 mana or less, an unknown mana value, or Spellbook says
  Ruthless/Banned).
- **Universes Beyond stays out of discovery and challenge pools** unless `--allow-ub`
  (`discovery.legal`), matching the profile.
- **The MCP server's EDHREC module is off** (`.mcp.json`), so all EDHREC traffic goes through
  `edhrec._fetch`'s cache and 1 req/s limit.

Policy (followed by agents, not checked by code):

- **Play-log entries cross into this repo only after the player confirms them.** `postgame` prints a
  draft; nothing calls `profile.add_entry` on its own.
- **Mulligan Labs: read-only GETs, low volume, only when the player asks**; never game actions or a seat.
- **The MCP server is for searching**; `push.py` owns every Archidekt write.
- **Forge keeps its files under its install folder** via a hand-made `forge.profile.properties`
  (`docs/forge.md`), and only ever plays the player's decks against each other offline.
- **Primers never mention the tools**; the odds and combos they state come from the scripts' output.

## Pointers into the code

| Concept | Code | Tests |
|---|---|---|
| Card basics (front face, oracle text, is-land) | `mtg/cards.py` | via the modules below |
| Chunked "these names AND this query" search | `scryfall.matching` | `tests/test_scryfall.py` |
| Official bracket, house verdict, fast combos, Rule 0 pitch | `mtg/brackets.py` | `tests/test_brackets.py` |
| Spellbook bracket estimate | `spellbook.estimate_bracket` | `tests/test_spellbook.py` |
| Oracle patterns (mld, stax, theft, donate, goad…) | `patterns.classify` | `tests/test_patterns.py` |
| Salt table | `edhrec.salt` | `tests/test_table_feel.py` |
| Gems, staple share, overlap, density, salt summary, table share | `mtg/scores.py` | `tests/test_gems.py`, `tests/test_originality.py`, `tests/test_table_feel.py` |
| Roles and odd swaps | `roles.role_hits`, `roles.alternatives` | `tests/test_originality.py` |
| Goldfish, Karsten table, fetch lands | `goldfish.simulate`, `goldfish.sources_needed`, `goldfish.land_produces` | `tests/test_goldfish.py` |
| Discovery mechanics, challenges, UB filter | `discovery.MECHANICS`, `discovery.candidates`, `discovery.challenge`, `discovery.legal` | `tests/test_discovery.py` |
| Profile enjoys bullets, play-log entries | `profile.enjoys`, `profile.render_entry`, `profile.add_entry` | `tests/test_profile.py`, `tests/test_profile_entry.py` |
| Forge `.dck`, run, parse | `mtg/forge.py` | `tests/test_forge.py` |
| Replays, post-game, meta (private) | `mtg-table/replays.py`, `postgame`, `meta.py` | `mtg-table/tests/test_replays.py` |

## Evidence (2026-10-24)

- **Bracket line** on Brian's decks: Etali Official B4 / Spellbook R / House ✓; Gonti B3 / P / ✓;
  Krark B3 / S / ✓; Kardur B2 / E / ✓.
- **Salt** runs low on real decks (averages 0.4–0.6); Gonti's saltiest is Tergrid at 2.8.
- **Density** calibration, the scale `originality.py` prints: Zedruu group hug 0.17, Ayula bears 0.21,
  Breya artifacts 0.59.
- **Karsten's 2022 99-card table** replaced a hand-typed one that was 3–9 sources too low. Breya (WUBR)
  casting its commander by T4 went from 87% (colours ignored) to 54% (colours, fetch lands, free
  mulligan).
- **Discovery probe counts** (`is:commander f:commander`, before the UB filter): control-swap 9, goad
  30, vote 7, coin 7, monarch 15, each-player 86, chaos 28. With UB out, control-swap leaves only
  Xantcha, Zedruu and Jon Irenicus, all already Brian's decks.
- **MCP server:** 70 read-only tools; startup 2–6 s; supply-chain audit of the installed tree found no
  known advisories (one stale package, `toml`).
- **Forge 2.0.15** on OpenJDK 25: games 17–47 s, no draws at `-c 600`, no unsupported cards once
  double-faced cards use their front name.
- **Mulligan Labs:** 9 of 14 completed games map to a local list by deck URL; the player id finds the
  player's seat in all 14.
- **Primer test:** an agent rewrote the Etali primer from RULES.md and the skill alone (494 words). Its
  fresh-eyes review caught an error in the live primer (tutors can't find the commander, it's in the
  command zone).

## Dead ends

- **PyPI mtg-mcp-server 3.0.0**: crashes on start (selectolax 1.x) and its bulk tools hit a Scryfall
  field rename; pinned to an upstream commit with `--exclude-newer` instead.
- **Scryfall `kw:monarch`** matches thousands of commanders; `otag:stax` and `otag:land-destruction`
  match nothing. Oracle-text regexes own those patterns.
- **Least-played-first swaps** surfaced joke and playtest cards; most-played-first without a staple
  filter gave Mind Stone for Sol Ring. Shipped: most-played first after skipping the EDHREC top 1000.
- **A computed hypergeometric source table** disagreed with Karsten at MV 1–3 because it ignored the
  free mulligan; his published numbers won and the computation was deleted.
- **EDHREC per-card salt pages** (85 requests a deck) lost to MTGJSON's single file.
- **Urza's synergy bands** (goodstuff ~0.1, tribal ~0.5) don't fit our density metric; Brian's own decks
  are the scale.
- **Matching the player's replay seat by deck URL** missed 5 of 14 games; the player id doesn't.
- **Forge `-d` with absolute paths** fails ("Could not load deck"); decks go in one `-D` directory.

## Open

- RULES.md Game Changer cap: around 4 (now) or 3 (truly B3); see [choices.md](choices.md).
- Not verified live: a split card (`Fire // Ice`) in a Forge sim; `discover.py --avoid -` from a pipe;
  a real Spellbook outage; the weekly MTGJSON salt rebuild end to end.
