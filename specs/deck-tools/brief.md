> Superseded by [README.md](README.md) where they differ; kept as the drafters' shared brief.

# Interview brief: deck-tools (2026-10-24)

The brief every spec drafter got. Decisions here are owned by the README once it exists.

## Ask
Brian asked for research into tools and skills that help build fun, good Commander decks, got a ranked
list of ten ideas plus two outside tools, and answered **"do it all"**. That answer also settles the
three open questions from the research: spec all ten, install j4th/mtg-mcp-server, and Forge AI-vs-AI
simulations of the player's own decks are within the line ("no AI player" means no bot at their table).

## The ten tools (research ranking)
1. **Bracket check** in `scripts/check_commander.py`: Commander Spellbook `POST /estimate-bracket`
   (verified 2026-10-23: `{"main":[{"card":…}],"commanders":[{"card":…}]}` → `bracketTag` plus per-card and
   per-combo detail; a Thoracle + Consultation list returns `R` = Ruthless) **plus** our own count of WotC's
   official criteria (Game Changers via Scryfall `is:gamechanger`, already used; mass land denial; extra
   turns; early two-card combos, already flagged as FAST). Print both labels: "Official B4 (4 GC) · House 3.75 ✓".
   Fact: official Bracket 3 allows ≤3 Game Changers, so RULES.md's "around 4" is officially B4 — the house
   label stays, the tool reports both. (WotC update 2026-02-09 is the latest; no bracket changes promised
   until the next MagicCon.)
2. **Table feel**: EDHREC salt (`json.edhrec.com/pages/top/salt.json`, 200 verified; per-card salt also in
   MTGJSON `edhrecSaltiness`), stax / MLD / extra turns / theft patterns, and a rough "touches other players"
   vs solitaire ratio from Scryfall otags and oracle text; prints a one-line Rule 0 pitch.
3. **Hidden gems**: EDHREC commander pages already fetched by `mtg/edhrec.py` carry `lift`, `trend_zscore`,
   `num_decks`, `potential_decks` per card (verified on zur-the-enchanter). `_cards()` keeps only synergy.
   Rank high-lift / low-inclusion cards in `scripts/edhrec_recs.py`.
4. **Commander discovery** skill: Scryfall searches for mechanics Brian loves (control swap / donate /
   "target opponent gains control", goad, voting, coin flips, monarch, "each player"), ranked by low EDHREC
   deck count, filtered by the profile's "enjoys" lines. The play log literally asks for this.
5. **Originality score**: share of the 99 that is EDHREC high-inclusion staples for the commander, overlap
   with the player's other decks in `decks/`, and 2–3 odd same-role alternatives (Scryfall otag) per staple.
6. **Post-game report** from Mulligan Labs replays: which cards were played / moved / never seen per game and
   across games, drafted into a play-log entry for the player to confirm. API in `docs/apis.md` (Mulligan
   Labs section): `GET /api/export/my-games`, `GET /api/replays/{id}` with `deckSnapshots` (`sourceUrl` =
   Archidekt deck) and `events` keyed by `instanceId`. `DRAW_CARDS` has only a count, so *drawn* cards and
   opening hands are NOT recorded — report "played" / "never played", not "drawn".
7. **Better goldfish and mana**: colour-aware draws, commander tax, keepable-hand %, commander-landing turn,
   Karsten source counts per pip. `deck_stats.py`'s `KARSTEN_99` table is from memory and marked unverified:
   verify against Frank Karsten's article before relying on it.
8. **Primer extras**: a narrated "signature turn", a mulligan guide, a "how to play the politics" note. Skill
   and RULES.md primer-format change; must hold the 300–500 word budget or deliberately raise it.
9. **Challenge decks**: roll constraints (random underplayed commander from discovery, Scryfall art tag
   `atag:` — verified `atag:dragon f:commander` = 1109 cards, flavour-text theme, one-year card pool).
10. **Playgroup meta**: friends' commanders and themes, so a new deck doesn't duplicate or hard-counter one.
    Source: Mulligan Labs replays (`players[].commanderName`, `deckSnapshots`).

## Outside tools
- **j4th/mtg-mcp-server** (MIT, ★20, pushed 2026-10-21, Python, 69 tools incl. `similar_cards`,
  `theme_search`, `estimate_bracket`, `evaluate_upgrade`): `claude mcp add mtg -- uvx mtg-mcp-server`.
  uv is already installed (`~/.local/bin/uvx`). Install at **project scope** (`.mcp.json` in the repo) so the
  playgroup gets it, read-only use only; our scripts own every write. Unverified: it was never run.
- **Forge** (Card-Forge/forge, GPL-3.0, Java, active): headless `sim` mode, e.g.
  `java -jar forge-gui-desktop-*.jar sim -d deck1 deck2 -n 10 -f Commander -q` (from old docs, unverified).
  Java is already installed (OpenJDK 25). Forge AI plays combo and politics badly; this is an experiment:
  a "your decks, N pods" report. Needs a deck-format converter from our `.txt` to Forge `.dck`. Forge itself
  is a download kept outside the repo (e.g. `~/.local/share/forge` or the cache dir), not a system package.
  Reference: TytaniumDev/MagicBracketSimulator (no license: read only).
- Ideas borrowed: pairwise interaction density (dreliq9/urza, MIT) as a "synergy vs pile" number;
  MTG-Analyzer's goldfish outputs; an unprimed "challenger" subagent review before push (P47Phoenix plugin).

## Constraints (sacred)
- **Public repo** (`basmith7/mtg` is PUBLIC). Anything derived from Mulligan Labs game history — replays,
  friends' names, friends' commanders, the playgroup meta — never goes into git. Mulligan Labs API tooling
  lives in `~/Projects/mtg-table` (local git, no remote) or writes only to gitignored / cache paths. The play
  log entry for the player's own deck in `players/<player>.md` is fine (existing practice) but names no
  other players. Never send game actions; no AI player at the table; connect only when the player asks.
- Standard library only for repo scripts (no numpy etc.). Optional extras go in the repo `.venv` like yt-dlp.
- Rate limits: Archidekt ~1 req/s, Scryfall <10 req/s with Accept header, EDHREC ~1 req/s cached a week.
- Never read or print `.env` secrets (Archidekt password, `MULLIGAN_LABS_API_KEY`); go through `mtg.config`.
- Primers are public and never mention the tools.
- Offline `unittest` suite in `tests/`; fakes at the network seam. New checks get offline tests with fixtures.
- Card text in primers/recommendations checked against Scryfall oracle text.
- Scripts' docstrings are their usage. ARCHITECTURE.md codemap must be updated as modules land.
- No backward compatibility or migration scaffolding (default: neither).

## Open taste question (non-blocking)
Should RULES.md cap Game Changers at 3 (truly official B3) or keep "around 4" (officially B4, labelled 3.75)?
Default until Brian answers: keep RULES.md; tools print both labels.
