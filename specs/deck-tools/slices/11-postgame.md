# 11 Post-game report (mtg-table, private)

**Contract:** after games, the agent can show which of the player's cards were played and which never
were, and draft a play-log entry for the player to confirm.

**Lives in `~/Projects/mtg-table`** (local git, no remote). Read README Firewalls first.

**Seam:**
- `mtg-table/replays.py`: `games() -> [row]` from `GET /api/export/my-games` (CSV); `replay(id)` from
  `GET /api/replays/{id}`, cached in `mtg-table/replays/` (add to its `.gitignore` *before* the first
  fetch); `my_seat(replay, sources)` matches `deckSnapshots[].sourceUrl` to the `# source:` lines of the
  player's lists in `~/Projects/mtg/decks` (fallback: ≥80 shared card names); `instances(replay) ->
  {instanceId: name}`; `usage(replays, seat) -> {'played': Counter, 'never': set}` from `PLAY_CARD` and
  `MOVE_CARDS` to battlefield (counted once per instance). `DRAW_CARDS` has no card names, so never
  claim "drawn".
- `mtg-table/postgame <deck.txt|archidekt url> [--last N]` prints games, placements, played and
  never-played cards, and a draft entry rendered by `mtg.profile.render_entry` (added to
  `mtg/profile.py` here, with a public test) that names no other player.
- Key through `mtg.config` (as `look` does); never printed.

**Spike first:** `replays.py --shape <id>` prints keys, types and counts only (no names): seats,
snapshots, event counts by type, whether `sourceUrl` matches a local list.
**Kill if:** fewer than half of completed games map to a local list.

**Tests:** `mtg-table/tests/` with a synthetic replay (seats "Seat A".."Seat D", invented cards):
instance mapping; no double count; abandoned games skipped; the draft contains no other seat's name.
**Checkpoint:** privacy audit — `git -C ~/Projects/mtg status` shows nothing from replays;
`git -C ~/Projects/mtg-table status` shows `replays/` ignored. The draft entry goes into
`players/brian.md` only after Brian confirms it.
