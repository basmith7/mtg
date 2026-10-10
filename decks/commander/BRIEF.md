# Brief for the 2026-10 Commander decks

Brian is building six new Commander decks to play **online** (MTGO/Arena-style clients or SpellTable,
so price doesn't matter and any card is available).

## Who he is as a player
His existing decks lean toward table politics and weird interaction: forced combat and goad
(Kardur, Thantis), stealing (Kotis, Don Andres, Tergrid), chaos (Yusri coin flips, Obosh odd costs,
Xantcha), meld, and spellslinging. He tags commanders "Very Silly", "Hmmmm" and "Actually Good".
**Fun first, winning second.** A good deck here makes memorable turns and interacts with the whole
table, and can still close a game.

## Power target: "bracket 3.75"
A strong bracket 3 or light bracket 4:
- **At most 4 Game Changers** (Scryfall `is:gamechanger`; the checker counts them). Use them only where
  they fit the theme. Don't add them just because they're strong.
- Real interaction: around 8–10 pieces of removal or counters, 1–3 board wipes if they fit, and
  efficient ramp and card draw.
- Tutors are fine in moderation.
- **No fast-mana package.** Sol Ring and Arcane Signet are fine. Skip Mana Vault, Chrome Mox and
  Mox Diamond, and Mana Crypt is banned.
- No extra-turn chains.
- No two-card infinite combo that wins out of nowhere in the early game. Late-game finishers and
  synergies that happen to go infinite late are fine, but say so in the primer.
- No mass land destruction.

## Rules
- **No Universes Beyond cards** (Fallout, Warhammer, LotR, Doctor Who, Final Fantasy, Marvel, etc.).
  D&D sets (AFR, CLB, AFC) count as normal Magic. **Exception:** the Wise Mothman deck may use UB
  cards, especially Fallout rad-counter cards.
- Verify every card exists and does what you think. The rules text in the primer must match Scryfall
  oracle text (`from mtg import scryfall; scryfall.named(name)` or `scryfall.search(query)`, about
  10 requests a second max). Don't rely on memory.
- Use the exact Scryfall card names. Double-faced and split cards take the full name with ` // `.

## Files
Write two files in `decks/commander/`:

`<slug>.txt`, exactly 100 cards including the commander:
```
# Karazikar – Goad Table (B3.75) | BR
Commander: Karazikar, the Eye Tyrant
1 Karazikar, the Eye Tyrant
1 Sol Ring
...
14 Mountain
```
The deck name follows "Commander – Theme or nickname (B3.75)". Make the nickname playful, like his
other decks ("Kenrith – Big Booty", "Talrand – Counter Target Dan").

`<slug>.md` is the primer, in light markdown: `## ` headings, `- ` bullets, `**bold**`, and `[[Card Name]]`
links. Keep it about 300–500 words, in plain, direct English. Sections:
1. One or two lines on what the deck is and why it's fun.
2. `## How it plays`: early, mid and late game.
3. `## How it wins`: list the win routes. Call out any late-game combos honestly.
4. `## Key cards`: 6–10 bullets, each with what the card actually does, checked against oracle text.
5. `## Tips`: table politics, sequencing, and what to mulligan for.

## Check before you finish
```
scripts/check_commander.py decks/commander/<slug>.txt          # add --allow-ub for the Mothman deck only
```
It must pass with no `!!` lines. It also asks Commander Spellbook which combos the deck contains: a
two-card infinite combo is a `!!` problem, and combos marked `EARLY` (two cards, or every piece at mana
value 3 or less) need a look. **The primer's "How it wins" combo claims must come from this output**:
name every included combo that is infinite or wins the game, say what it needs and that it's a late-game
finisher, and don't claim combos the checker didn't list. Run with `--near` to find combos one card away
(for suggestions, or to be sure you didn't leave one half-built). Also look at the land count (usually 35–37, fewer with heavy ramp)
and the curve it prints. Don't touch Archidekt, git, or any other file.

End your reply with the checker's output, your Game Changers and why you chose them, and anything you
weren't sure about.
