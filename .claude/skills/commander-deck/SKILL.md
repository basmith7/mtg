---
name: commander-deck
description: Use when Brian wants a Magic deck built, tuned, imported or put on Archidekt — "build a <commander> deck", "improve this deck", "add this deck (link) to Archidekt", "write a primer", or when he says how a game with one of his decks went.
---

# Commander deck workflow

Read `AGENTS.md`, `decks/commander/RULES.md` (power target, card rules, primer format) and `decks/PLAYLOG.md`
(what he actually enjoys) first. Run everything from the repo root. Brian plays Commander online,
so price doesn't matter; paper decks are rare and get their own rules. Universes Beyond cards: ask first.

## Importing a deck from a link
`scripts/import_deck.py <url> -o decks/commander/<slug>.txt` handles Moxfield, Archidekt, MTGGoldfish,
plain-text lists and Instagram reels (caption → link-in-bio → Moxfield/Archidekt profile). Instagram
needs the repo `.venv` with yt-dlp; the script prints the one-line setup if it's missing. If it lists
candidates instead of picking one, show Brian the candidates rather than guessing.
Then ask Brian whether to keep the list close to the original or tune it to RULES.md before changing
cards. Rename the header to "Commander – Nickname (B#)" and credit the original author in the primer.

## Building or tuning
1. **Start from data, not memory.** `scripts/edhrec_recs.py "<Commander>" --themes`, then
   `--theme <t>` for the angle Brian wants, and `--deck <file>` on a draft for missing staples and cut
   candidates. "Not on the EDHREC list" only means outside its top lists; low inclusion % is the real
   cut signal. Taste beats popularity: keep odd, fun cards that fit the PLAYLOG.
2. **Check roles and mana.** `scripts/deck_stats.py <file>` shows ramp, draw, removal and wipe counts
   against targets, colour sources, and a goldfish sim (commander on curve %). Fix shortfalls.
3. **Check legality and combos.** `scripts/check_commander.py <file> --near` must show no `!!` lines.
   `!!` lines are flags to fix or justify (the rule is moderation). Fun late combos are fine; fast infinite combos (pieces totalling 6 MV or less, or rated Ruthless/Banned by
   Spellbook) are not. `--near`
   shows combos one card away, for suggestions or to avoid half-building one.
4. **Verify card text** against Scryfall (`scryfall.collection(names)`, `scryfall.oracle_text(card)`)
   before writing anything about a card.
5. A brand-new deck is a medium task: give Brian a short pitch (angle, nickname, key cards) before
   building the full list. Tuning an existing deck: just do it and report the swaps.

## Primer
`<slug>.md` beside the list, in the format RULES.md describes (what/why fun, How it plays, How it wins,
Key cards, Tips; ~300–500 words; `[[Card Name]]` links), written for any player reading it on Archidekt.
Combo claims come from the checker's output only, stated as facts about the deck. Card counts you state (e.g. "94 permanents") must be computed, not estimated.

## Archidekt
Writes go to Brian's real account: upload or sync only when he asked for the deck on Archidekt (or
confirm first), and check the folder id before creating anything.
- New deck: `scripts/upload_decks.py --folder <id> decks/commander/<slug>.txt` (uses the `.md` primer).
  Folders: Commander `1914431` (played online), Paper `1914435`, Lists & Ideas `1914436` (other people's
  lists and ideas), Archive `1914437`.
- Existing deck: `scripts/sync_deck.py <id or url> <file> --dry-run`, then without `--dry-run`. It backs
  up first and verifies afterwards.
- `sync_deck.py` overwrites the primer from the `.md` beside the list; pass `--no-primer` to leave it.
- Never delete on Archidekt without asking; archive instead: `archidekt.move([deck_id], 1914437)`.

## Finishing
Commit the deck files on a branch and open a PR (Brian merges with merge commits). Report the Archidekt
link, the swaps and why, checker output, Game Changers used, and anything unverified.

## After games
When Brian says how a game went, add an entry to `decks/PLAYLOG.md` and update its "enjoys" summary if
a pattern is emerging. Offer tuning swaps if something flopped.
