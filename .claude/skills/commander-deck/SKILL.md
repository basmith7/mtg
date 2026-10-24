---
name: commander-deck
description: Use when the player wants a Magic deck built, tuned, imported or put on Archidekt — "build a <commander> deck", "find me a commander", "something weird", "challenge deck", "improve this deck", "add this deck (link) to Archidekt", "write a primer", or when they say how a game with one of their decks went.
---

# Commander deck workflow

## Before anything
1. `scripts/whoami.py` says who the player is (`MTG_PLAYER`) and which Archidekt folders are theirs.
   If it fails, help them fill in `.env` from `.env.example` before going further.
2. Read `AGENTS.md`, `RULES.md` (house rules: power target, card rules, primer format) and
   `players/<player>.md` (their taste, extra preferences and play log). Where the profile and the house
   rules differ, the profile wins.
3. Run everything from the repo root. Decks live on Archidekt and `decks/` is a gitignored working
   copy, so pull before touching an existing deck: `scripts/pull.py <id|url>`, or no argument for
   every deck in their decks folder.

## Importing a deck from a link
Someone else's deck: `scripts/import_deck.py <url> -o decks/commander/<slug>.txt` handles Moxfield,
Archidekt, MTGGoldfish, plain-text lists and Instagram reels (caption → link-in-bio → Moxfield/Archidekt
profile). Instagram needs the repo `.venv` with yt-dlp; the script prints the one-line setup if it's
missing. If it lists candidates instead of picking one, show the player the candidates rather than
guessing. Then ask whether to keep the list close to the original or tune it to the rules before
changing cards. Rename the header to "Commander – Nickname (B#)" and credit the original author in the
primer.

## Finding a commander
When the player has no commander in mind, pull their decks first (so their commanders are skipped),
then `scripts/discover.py`: it reads the profile's "enjoys" bullets, picks matching mechanics and lists
underplayed commanders. `--mechanic` overrides the pick, `--colours` bounds the identity, `--avoid
<file|->` skips the playgroup's commanders, `--counts` orders the top 15 by EDHREC deck count (the
reliable "underplayed" signal). Offer three, each with a line on why it fits their play log.

**Challenge deck:** `scripts/discover.py --challenge` rolls a brief (a commander plus an art tag,
flavour word or year) and the Scryfall query for its pool. Build from that query and check with
`scripts/check_commander.py <file> --pool "<query>"`; basic lands are always in the pool.

## Building or tuning
1. **Start from data, not memory.** `scripts/edhrec_recs.py "<Commander>" --themes`, then
   `--theme <t>` for the angle the player wants, and `--deck <file>` on a draft for missing staples and
   cut candidates. "Not on the EDHREC list" only means outside its top lists; low inclusion % is the
   real cut signal. Taste beats popularity: keep odd, fun cards that fit the player's profile.
2. **Check roles and mana.** `scripts/deck_stats.py <file>` shows ramp, draw, removal and wipe counts
   against targets, colour sources, and a goldfish sim (commander on curve %). Fix shortfalls.
3. **Check legality and combos.** `scripts/check_commander.py <file> --near` must show no `!!` lines:
   fix them or justify them (the rule is moderation). Fun late combos are fine; fast infinite combos
   (pieces totalling 6 MV or less, or rated Ruthless/Banned by Spellbook) are not. `--near` shows
   combos one card away, for suggestions or to avoid half-building one.
4. **Use canonical names and check legality while drafting**, not at the end. Double-faced, split and
   adventure cards take the full `A // B` name (RULES.md; the checker flags a front-face name). Drafts have picked banned (Dockside Extortionist), Universes Beyond (Delighted Halfling) and
   off-colour cards (Phyrexian Metamorph in RG). Red decks keep landing one card from a fast combo:
   Dualcaster Mage with Twinflame / Heat Shimmer / Electroduplicate / Molten Duplication, Reiterate with
   Jeska's Will, Rionya with Terror of the Peaks.
5. **Verify card text** against Scryfall (`scryfall.collection(names)`, `scryfall.oracle_text(card)`)
   before writing anything about a card.
6. A brand-new deck is a medium task: give the player a short pitch (angle, nickname, key cards)
   before building the full list, unless they already gave the direction (e.g. "build these seven").
   Tuning an existing deck: just do it and report the swaps.

**Several decks at once:** give each subagent one deck to draft and check (files only), then upload
from one place, one deck after another: parallel uploads share one Archidekt session, and parallel
Scryfall checks from many agents hit 429s.

## Primer
`<slug>.md` beside the list, in the format RULES.md describes, written for any player reading it on
Archidekt. Which combos to name comes from the checker's output only, but the primer states them as
facts about the deck and never mentions the checker, sims or scripts. Card counts you state (e.g. "94
permanents") must be computed, not estimated. Agents tend to run long: hold the 300–500 words.

## Archidekt
Writes go to the player's real account: push only when they asked for the deck on Archidekt (or
confirm first).
- `scripts/push.py <file> --dry-run`, then without `--dry-run`. A file with a `# source:` line updates
  that deck; one without becomes a new deck in their decks folder (`--folder <id>` for another) and gets
  the line. Push backs up first and verifies afterwards. It refuses if the deck changed on the site since
  the file's `# updated:` version: pull again and redo your change rather than `--force`.
- The `.md` beside the list is the primer, pushed only when it changed; `--no-primer` leaves it.
- Never delete on Archidekt without asking; archive instead: `archidekt.archive([deck_id])`.

## Finishing
The deck is done when it's on Archidekt; deck files aren't committed. Report the Archidekt link, the
swaps and why, checker output, Game Changers used, and anything unverified. Changes to `RULES.md`, a
profile in `players/` or the tools go on a branch with a PR.

## After games
When the player says how a game went, add an entry to the play log in `players/<player>.md` and update
its "enjoys" summary if a pattern is emerging. Offer tuning swaps if something flopped.
