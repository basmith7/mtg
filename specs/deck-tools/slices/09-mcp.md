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
