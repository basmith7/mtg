# Players

One file per player, named for the `MTG_PLAYER` in their `.env` (`brian` → `brian.md`). The house
rules in [RULES.md](../RULES.md) apply to everyone; a profile holds what's personal:

- **Who they are as a player:** the kinds of decks and turns they enjoy.
- **Preferences beyond the house rules:** online or paper, Universes Beyond, which Archidekt folders mean what.
- **What they enjoy (distilled):** a short summary, each line pointing back to games in the log.
- **Play log:** newest first, one entry per game or session (copy the block format from an existing profile).

Agents read the profile before building or tuning a deck and add a log entry whenever the player says
how a game went. To join, copy an existing profile, rewrite it for yourself, and open a PR.
