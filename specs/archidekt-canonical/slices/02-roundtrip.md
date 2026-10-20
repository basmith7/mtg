# 02 — Decklist and primer round-trip (offline)

**Contract:** the decklist format and primer markdown each have one owner that both reads and
writes, so pull (slice 03) is just plumbing.

**Seam:**
- `mtg/decklist.py: render(name, colors, commanders, cards, source=None) -> str`, moved from
  `scripts/import_deck.py:render`. `parse(render(x))` returns `x`. `import_deck.py` calls it.
- `colors(commanders, cards)` moves from `scripts/import_deck.py:colors` into `mtg/scryfall.py`
  (`color_identity(names) -> 'WUBRG'-ordered str`).
- `mtg/quill.py: from_delta(delta_json) -> (markdown, dropped)` — inverse of `to_delta` for
  headers (level 2; other levels render as `## ` and count as dropped formatting), bullet lists,
  bold, paragraphs. Unsupported attributes (italic, links, ordered lists, images, other header
  levels) keep their text and are listed in `dropped` (a sorted set of attribute names).

**Verify:** `tests/test_decklist.py` (render/parse round-trip incl. a Commander list and a `#
source:` line); `tests/test_quill.py`: `from_delta(to_delta(md))[0] == md` (normalised blank lines)
for every existing primer: `decks/commander/*.md` and the `PRIMERS` dicts in
`decks/ravnica/primers_*.py`, read from the main checkout if missing here; a hand-built delta with
italics and a link returns its text plus `dropped == {'italic', 'link'}`.

**Delegated:** whitespace normalisation rules; how `[[Card]]` links survive (they're plain text
in both directions today).

**Stays green:** `import_deck.py` output byte-identical for an Archidekt URL and a text list.
