# deck-tools: choices made without Brian

Every decision the build made where the spec was silent, re-audited against the shipped code on
2026-10-24 (branch `feat/deck-tools`). Grouped by verdict, least confident first. Per-slice drafts were
folded in here and deleted.

## Needs Brian (each has a provisional call already in the code)

### Game Changer cap stays "around 4" (RULES.md unchanged) — confidence: medium
- **Scenario:** WotC's Bracket 3 allows at most 3 Game Changers (the official list of extra-strong
  cards). RULES.md says "around 4", so a deck with 4 is officially Bracket 4. `check_commander.py` now
  prints both: `Official B4 (4 Game Changers) · Spellbook R · House 3.75 ✓`. RULES.md got one sentence
  saying that line is normal.
- **Gap:** the spec left the cap to Brian.
- **Reach:** every bracket line, `--max-gc` default 4 in `check_commander.py` and `table_feel.py`.
- **Provisional:** keep 4. To cap at 3: change RULES.md's Game Changer bullet and both `--max-gc` defaults.

### Primer word budget raised from 300–500 to 300–550 — confidence: medium
- **Scenario:** primers now must end "How it plays" on a narrated *signature turn* (the turn the deck
  aims for) and carry a Mulligan and a Politics bullet in Tips: about 120 more words. The Etali test
  rewrite fit 500 only by dropping its late-game paragraph. The budget is counted with `wc -w`, so the
  words in `[[Card Name]]` links count.
- **Gap:** the spec made the budget a checkpoint for Brian; he was away, so it was decided on evidence.
- **Reach:** every future primer's length.
- **Provisional:** 550. Reverse by editing the number in RULES.md and the commander-deck skill.

## Sound, less certain

### Spellbook's own bracket tag is shown but never decides anything — confidence: medium
- **Scenario:** Commander Spellbook's `/estimate-bracket` uses its own scale (E C O P S R B). Probed:
  4 Game Changers → R (Ruthless), Winter Orb alone → R. So it would call most of Brian's decks Ruthless.
  The code takes its per-card flags (Game Changer, mass land denial, extra turn) and per-combo flags
  (definitely two-card) as facts, computes the official bracket itself, and prints Spellbook's tag only
  as information.
- **Reach:** if Spellbook changes its tag scale, nothing breaks.

### The official bracket: B2 floor, chained extra turns = 2+ extra-turn cards — confidence: medium
- **Scenario:** `brackets.official` says B4 for 4+ Game Changers, any mass land denial, 2+ extra-turn
  cards, or a fast two-card combo; B3 for 1–3 Game Changers or a late two-card combo; else B2. It never
  says B1 (that's about intent, a theme deck) or B5 (cEDH, also intent). "Fast" stays our old proxy
  (pieces total 6 mana or less, or Spellbook rates the combo Ruthless/Banned), since WotC's newest
  wording is "expect at least six turns" and Spellbook's `speed` field is undocumented.
- **Gap:** WotC's criteria are prose; the counting rules are ours.

### Two-card combos for the bracket come from `/estimate-bracket`, infinite combos for the house rule from find-my-combos — confidence: medium
- **Scenario:** Thassa's Oracle + Demonic Consultation wins the game without anything "infinite", so
  the official bracket uses Spellbook's `definitelyTwoCard` flag. The house `!!` line still fires only
  on fast *infinite* combos (its text unchanged), because that's what RULES.md bans.
- **Reach:** a fast non-infinite two-card win shows as Official B4 but not as a house failure. That
  matches RULES.md today; tighten RULES.md if Brian wants it to be a failure.

### Table feel: "touches the table" = any oracle pattern but extra turns — confidence: medium
- **Scenario:** `patterns.classify` reads oracle text for mld, extra-turn, stax, theft, donate, goad,
  vote, coin, monarch and each-opponent. `table_share` counts a nonland card as touching other players
  if it has any tag except extra-turn, so "each opponent loses 1 life" counts. Theft also matches "You
  control enchanted creature" (Treachery, Control Magic). Any stax card counts as stax, not only locks.
  Scryfall has no usable otag for stax or land destruction (both match nothing), hence regexes.
- **Reach:** the Rule 0 pitch's first words ("Goad and theft deck" / "Mostly self-focused deck") come
  from these counts.

### Rule 0 pitch wording — confidence: medium
- **Scenario:** one sentence: up to two themes with 3+ cards, else "Interactive" (25%+ share) or "Mostly
  self-focused"; "B<n> on paper (first reason)"; then "with …" or "but no …" stax / land wipes /
  extra-turn chains / fast combos; the saltiest card if any is over 2.0; "it bends our house rules" when the house check fails. Example: "Goad deck, B2 on paper
  (no Game Changers or two-card combos) but no stax, land wipes, extra-turn chains or fast combos." The
  "but" reads oddly after B2; cosmetic, left.

### Salt from MTGJSON, kept as a small table — confidence: high
- **Scenario:** salt is EDHREC's community "how annoying is this card" score (0–4). EDHREC's per-card
  pages would cost ~85 requests a deck at 1 a second; MTGJSON's AtomicCards file (52 MB download) has
  the same number (`edhrecSaltiness`, matched EDHREC's page on 3 decks, 245/245 cards). `edhrec.salt`
  downloads it weekly, keeps a 0.9 MB `{name: salt}` table in `~/.cache/mtg/edhrec/salt.json`; the
  download is read in memory and never stored. Basics are left out of the average (Forest scores 0.62).

### Hidden gems: inclusion under 15%, at least 20 decks, ranked by EDHREC lift — confidence: medium
- **Scenario:** EDHREC's commander pages carry `lift` (how much more often a card appears with this
  commander than its general popularity predicts). `edhrec_recs.py --gems` lists cards under 15%
  inclusion and at least 20 decks, highest lift first, basics always out, deck cards out with `--deck`.
  `--gem-max` and `--gem-min-decks` override. The 20-deck floor never bit on a real page tried; it's
  there for tiny commanders.

### Odd swaps: same role, most played first, but never a format-wide staple — confidence: medium
- **Scenario:** `originality.py` offers, for the deck's most-included staples, three cards with the
  same Scryfall role tag in colour identity. Ordering least-played first (the spec) surfaced joke cards
  (Cursed Firebreathing Yogurt), so it orders most-played first, skips the deck's cards, the
  commander's EDHREC staples, Game Changers, `is:funny` sets, and (added in the final audit) any card in
  the top 1000 by Scryfall's `edhrec_rank` (unranked cards are kept), which had made Sol Ring's swaps Mind Stone and Thought Vessel. Gonti now
  gets Sol Ring → Kodama of the East Tree, Nyxbloom Ancient, Roiling Regrowth.
- **Reach:** role tags are crowd-sourced and noisy (Mana Drain is tagged ramp), so swaps are prompts
  for the agent, printed with "?".

### Synergy density is our own metric, calibrated on Brian's decks — confidence: medium
- **Scenario:** `scores.density` = share of nonland card pairs where one card's oracle text names a
  type, subtype, keyword, counter or token the other has or makes (own name masked, own keywords
  skipped). Not urza's tables (only the idea), so the output prints Brian's decks as the scale:
  Zedruu group hug 0.17, Ayula bears 0.21, Breya artifacts 0.59. The spec's "both share a patterns tag"
  clause was left out and stays out: density is about cards naming each other, table tags are another
  axis (table_feel). Known noise: "destroy target artifact or enchantment" counts as naming artifacts.

### Goldfish model: free first mulligan, keep rule, recast after removal — confidence: medium
- **Scenario:** Commander's first mulligan in multiplayer is free (CR 103.5c), so the sim takes it free
  and caps at four mulligans. A seven is kept with 2–5 lands and either 3+ lands or a 2-drop it can pay
  for. Pips are paid by colour. The commander is assumed removed the turn it lands and recast at +2
  ("recast by T8 70%"). Twelve turns are simulated so a 9-drop has a recast number.
- **Reach:** the primer's Mulligan bullet quotes the keepable-seven rate.

### Colour sources are judged against Karsten's published 2022 Commander table — confidence: high
- **Scenario:** `goldfish.sources_needed(pips, mv)` looks up Frank Karsten's 2022 99-card numbers
  (article and content-API URL in the docstring); unpublished cells take the nearest MV for that pip
  count. The old hand-typed table was 3–9 sources too low. Fetch lands count as a source of every
  colour they can fetch (generic basic fetchers: the deck's identity), as Karsten counts them. The mana
  check flags the card needing the most sources, often a one-pip one-drop, not the most pips.
- **Reach:** most 3-colour decks now show SHORT on some colour; that's Karsten's verdict, not a bug.

### Discovery leaves Universes Beyond out by default — confidence: high
- **Scenario:** Brian's profile avoids Universes Beyond (licensed sets like LotR, Fallout). Six of the
  nine control-swap commanders (Bilbo, Yes Man…) were UB-only. Every discovery and challenge query now
  carries `not:universesbeyond` unless `--allow-ub`, mirroring `check_commander.py --allow-ub`.

### Discovery queries and ordering — confidence: medium
- **Scenario:** control-swap also matches "under the control of an opponent" (Xantcha-style), chaos
  only `o:"at random"` (the broader `o:random` was mostly unrelated). Commanders sort by Scryfall's
  `edhrec_rank`, which is a card's rank in all decks, not as a commander, so `--counts` re-sorts the top
  15 by EDHREC's own commander deck counts. Brian's own commanders (from `decks/commander`) and
  `--avoid` names are skipped; when nothing is left the script says so. Keyword map: "works for the
  table" means control-swap, not each-player.

### Challenge decks — confidence: medium
- **Scenario:** `discover.py --challenge` rolls commander+mechanic, art tag (29 curated `atag:`s with
  111–2240 cards each), flavour word, or a year's sets, then picks a commander from that pool. It prints
  the Scryfall query, not the pool size (a second request). `check_commander.py --pool "<query>"`
  checks a deck against it in 2–3 chunked searches; basics (including snow basics and Wastes) are
  exempt; outside cards are `!!` and exit 1.

### MCP server pinned to an upstream commit with a dependency date cutoff — confidence: medium
- **Scenario:** PyPI's mtg-mcp-server 3.0.0 crashes on start (a dependency broke) and its bulk tools hit
  a Scryfall field rename. Upstream `main` fixes both but isn't released, so `.mcp.json` runs
  `uvx --from git+…@51479f7 --exclude-newer 2026-10-24` (dependencies resolved as of the audited date).
  Modules on: Scryfall, Spellbook, bulk data, rules. Off: EDHREC (our cache owns that rate limit),
  Moxfield (our client), 17Lands, Spicerack, MTGGoldfish (no Commander use).
- **Reach:** upgrading means bumping the commit and the date and re-running the supply-chain audit.

### Forge setup — confidence: medium
- **Scenario:** Forge 2.0.15 lives in `~/.local/share/forge`, with a `forge.profile.properties` that
  keeps its user and cache dirs inside that folder (its defaults `~/.forge`, `~/.cache/forge` were
  outside the approval and were removed). `forge_sim.py` defaults to `-n 10` games and `-c 600` seconds
  per game (spike games took 17–47 s, none timed out). Deck names are reduced to letters, digits and
  spaces; `A // B` names are kept only for real split cards (from Forge's card database), front face
  otherwise, since Forge dropped four double-faced cards written in full.

### Post-game report: what counts as "played" — confidence: medium
- **Scenario:** Mulligan Labs replays log cards entering play and moving zones, but not which cards were
  drawn. A card counts as played if it entered the battlefield, or (instants, sorceries) moved hand →
  graveyard/exile, so a discarded spell also counts. "Never played" leaves out basics, splits lands from
  spells, names at most ten in the draft entry (the report lists all), and says the replay can't tell undrawn from held. Default: the last 5
  games with that deck. The draft entry's Fun and Change read "ask the player".

### Playgroup meta finds Brian's seat by his Mulligan Labs player id — confidence: high
- **Scenario:** matching seats by deck URL found Brian in 9 of 14 games; his player id is stable in all,
  so `meta.py` uses it and can't count his own commander as a friend's. Default lookback 20 games;
  themes use `mtg.patterns` plus the site's own `detectedMechanics`; "Unknown Commander" is dropped.
- **Reach:** all of this lives in the private `mtg-table` repo; nothing reaches the public repo.

### `MTG_REPO` selects which mtg checkout mtg-table imports — confidence: high
- **Scenario:** mtg-table imports the public `mtg` package from `~/Projects/mtg` by default; `MTG_REPO`
  points it at a branch worktree for testing. Deck lists always come from the main checkout.

## Sound, structural (what Brian now owns)

- **New pure modules** (no network): `cards` (front face, oracle text, is-land), `brackets`, `patterns`,
  `scores`, `goldfish`. `scryfall.matching(names, query)` is the one chunked "these names AND this
  query" search (Universes Beyond check, roles, `--pool`). `decklist.BASICS` is the one basics set. All
  confidence high.
- **`check_commander.show_combos` returns its lines** instead of printing, so the bracket line sits
  under the Game Changers line, and `brackets.house` owns every bracket `!!`. High.
- **Fresh-eyes primer review gets the check scripts' output**, or it flags correct claims it can't
  verify; the skill also gains a "how cards combine" check after the old Etali primer claimed tutors
  find the commander. High.
- **Discovery, gems, table feel and originality are steps in the existing `commander-deck` skill**, not
  new skills. High.
- **Play-log entries need Brian's confirmation**; `profile.add_entry` inserts newest first below the
  template, `render_entry` writes "not given" for empty fields. High.
- **Trivial discretion** (column layouts, flag names, test file split, fixture trimming): not listed.
