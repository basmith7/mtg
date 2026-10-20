# Agent notes

- Read `docs/apis.md` before touching Archidekt or Moxfield. Both are private APIs; prefer the
  clients in `mtg/` over raw requests, and update the doc when you learn something new about them.
- **Credentials:** never print the Archidekt password. `mtg.archidekt` pipes it from 1Password and
  caches tokens in `~/.config/mtg/archidekt-session.json`. Each `op` call prompts Brian, so renew with
  the refresh token (the client does this) instead of logging in again.
- **Rate limits:** Archidekt's card lookup returns 429 quickly (keep ~1 req/s, use the id cache);
  Scryfall wants ~10 req/s max and an `Accept` header.
- **Before writing to Archidekt**, back up what you'll change (`archidekt.deck(id)` JSON), and confirm
  deletes with Brian. Archive rather than delete.
- Deck-building rules live in `decks/commander/RULES.md`. Brian plays Commander online; paper decks
  are rare and get their own rules when they come up.
- Card text you put in primers or recommendations: check it against Scryfall oracle text, don't
  rely on memory.
- `decks/PLAYLOG.md` records how decks actually played. Read it before building or tuning a deck,
  and whenever Brian mentions how a game went, add an entry (and update the "enjoys" summary).
