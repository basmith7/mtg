# 03 Table feel

**Contract:** `scripts/table_feel.py <list>` says how a deck will feel to the other three players and
drafts a Rule 0 pitch.

**Seam:**
- Salt source, decided by a probe at the start of the slice: MTGJSON `AtomicCards.json.gz` (52 MB,
  per-card `edhrecSaltiness`; one download cached a week in `config.CACHE`) if that field exists and is
  populated for ≥90% of a sample deck; otherwise EDHREC per-card pages (`pages/cards/<slug>.json` →
  `container.json_dict.card.salt`) through `edhrec._fetch` at 1 req/s. Owner: `edhrec.salt(names) ->
  {name: float}` either way (MTGJSON reader lives there too, as EDHREC's data). Record the choice in
  `docs/apis.md`.
- `patterns.classify` gains `stax` (oracle regex: "can't untap", "don't untap", "each player can't",
  tax effects "costs {1} more" for opponents), `theft` ("gain control of"), `donate` ("target
  opponent gains control" / "target player gains control"), `goad`, `vote`, `coin`, `monarch`,
  `each-opponent` ("each opponent", "target opponent", "each player"). Scryfall `otag:stax` and
  `otag:land-destruction` match nothing (probed), so regexes own this.
- `scores.salt_summary(names, salt) -> {'avg', 'top': [(name, s)], 'over2': [names]}`.
- `scores.table_share(classified) -> float`: share of nonland cards with any table-touching tag.
- `brackets.pitch(official, house, flags, salt_summary, share) -> str`: one plain sentence, never names
  a tool.

**Run:**
```
scripts/table_feel.py decks/commander/kardur.txt
salt: average 1.3; saltiest Cyclonic Rift 2.4, Propaganda 2.0 (2 cards over 2.0)
table: 41% of spells touch other players · theft 3 · goad 6 · stax 1 (Propaganda) · MLD 0 · extra turns 0
Rule 0: "Goad and theft deck, B4 on paper (4 Game Changers) but no stax lock, land wipes or fast combos."
```

**Tests:** `tests/test_patterns.py` on inline oracle texts (Armageddon → mld, Time Warp → extra-turn,
Propaganda → stax, Treachery → theft, Xantcha → donate, Sol Ring → ∅). `tests/test_scores.py` salt
summary and share on a synthetic deck. Pitch contains no script or tool name.

**Checkpoint:** the pitch tone on two of Brian's decks.
**Delegated:** regex details, display order.
**Feedback that changes this slice:** pitch wording.
