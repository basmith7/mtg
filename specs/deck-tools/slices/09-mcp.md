# 09 MCP server (j4th/mtg-mcp-server)

**Contract:** agents in this repo get read-only card search tools we lack (`similar_cards`,
`theme_search`, `evaluate_upgrade`), pinned and audited.

**Spike first:** `uvx mtg-mcp-server==3.0.0` with default flags (EDHREC, bulk-data, rules modules
default **off**; keep EDHREC off so all EDHREC traffic stays in our 1 req/s cache). List its tools,
then call `estimate_bracket`, `theme_search`, `similar_cards` (needs `MTG_MCP_ENABLE_BULK_DATA`?) on
one deck. Run `supply-chain-risk-auditor` over its dependency tree.

**Kill if:** it fails to start; any tool writes to an account; the useful tools need EDHREC enabled;
the audit finds a serious advisory. Record evidence here.

**Ship:** `.mcp.json` at the repo root, `{"mcpServers": {"mtg": {"command": "uvx", "args":
["mtg-mcp-server==3.0.0"], "env": {...bulk flag if needed}}}}`; `AGENTS.md` one line (read-only; our
scripts own writes); `docs/apis.md` a short section; ARCHITECTURE.md mentions it.
**Delegated:** which optional modules to enable besides EDHREC (keep off).

## Done (2026-10-24): alive, shipped with a commit pin

Spike evidence:
- **PyPI 3.0.0 fails to start**: `ImportError: Modest backend is deprecated since selectolax 1.0`
  (3.0.0 allows `selectolax>=0.4.7`; uvx resolves 1.x). With `--with "selectolax<1"` it starts, but
  `theme_search` and `bulk_similar_cards` return `Bulk metadata missing 'download_uri'` (Scryfall
  renamed it `jsonl_download_uri`; upstream issue #69). Upstream `main` fixes both, unreleased.
- **Shipped pin:** `git+…@51479f7a` with `--exclude-newer 2026-10-24T00:00:00Z`. Starts in 1.7–6.3 s;
  bulk data loads 35,544 cards in ~8 s on the first bulk call.
- **The spec's premise was wrong:** every module defaults to **on** (`config.py`: `enable_edhrec: bool
  = True`, …). `.mcp.json` sets EDHREC, Moxfield, 17Lands, Spicerack and MTGGoldfish off; with
  EDHREC off the `edhrec_*` tools are not registered at all.
- **Writes:** 70 tools, all `readOnlyHint: true`; none take account credentials.
- **Calls on Krenko (EDHREC off):** `spellbook_estimate_bracket` → `E`, no concerns;
  `theme_search goblin R` → Goblin Flotilla, Spitfire Handler, Akki Rockspeaker, Goblin Trashmaster…;
  `bulk_similar_cards Krenko, Mob Boss` → Pashalik Mons, Bolg of the North, Azog…;
  `evaluate_upgrade Goblin Bombardment` → "Synergy: EDHREC disabled", 5 combos. Useful tools
  (theme, similar, rules) do not need EDHREC.
- **Supply chain** (`supply-chain-risk-auditor`): the repo's `uv.lock` has fastmcp 3.2.0
  (GHSA-7xgj-8392-5q4r, medium), filelock 3.25.2 (GHSA-v4x8-3wr5-3wq8 high, Windows/symlink lock
  issues), opentelemetry-api 1.40.0 (medium). `uvx` ignores that lock; the tree it actually installs
  (81 packages: fastmcp 4.1.3, opentelemetry-api 1.45.1, no filelock) has **0 known advisories**; one
  maintenance flag (`toml` 0.10.2, no push since 2024-06). Publisher concentration and install
  scripts are unassessable on PyPI.
