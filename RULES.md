# Commander deck rules

The playgroup's house rules for Commander decks: the default for every deck unless the player says
otherwise for one. Each player's taste, extra preferences and play log live in
`players/<MTG_PLAYER>.md`; read it too, and when it and these rules differ, the player wins.
**Fun first, winning second.** A good deck makes memorable turns, interacts with the whole table,
and can still close a game.

## Power: "bracket 3.75", everything in moderation
A strong bracket 3 or light bracket 4. The rule is moderation, not a checklist: the deck should feel
strong and interactive without being oppressive or deciding the game early. The numbers below are
guideposts, so break them when the deck's plan calls for it and say why.
- **Game Changers:** around 4 at most, and only where they fit the theme.
- **Interaction:** enough to answer threats, usually 8–10 removal or counters. Board wipes depend on
  the plan: a control deck wants several, a creature deck may want none or one that spares its board.
- **Ramp and draw:** efficient, enough to do what the deck wants on time.
- **Tutors:** a few are fine.
- **Fast mana:** Sol Ring and Arcane Signet are fine; skip the Mana Vault / Chrome Mox / Mox Diamond
  package (Mana Crypt is banned anyway).
- **Combos:** welcome if they're fun and not a turn-2 or turn-3 win. Late-game finishers and synergies
  that happen to go infinite late are fine; say so in the primer.
- **Avoid:** extra-turn chains and mass land destruction.

## Cards
- **Universes Beyond** (Fallout, Warhammer, LotR, Doctor Who, Final Fantasy, Marvel, etc.): follow
  the player's profile; without a stated preference, ask first. D&D sets (AFR, CLB, AFC) count as
  normal Magic.
- Verify every card exists and does what you think. Rules text in the primer must match Scryfall
  oracle text (`scryfall.collection(names)`, `scryfall.oracle_text(card)`). Don't rely on memory.
- Use the exact Scryfall card names. Double-faced and split cards take the full name with ` // `.

## Someone else's list
When importing a deck (a netdeck, a video, a friend's list), ask the player whether to keep it close to
the original or tune it to these rules before changing cards. Credit the original author in the primer.

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
Partner commanders (or a commander plus its Background) get a `Commander:` line each, and each is also
listed as `1 Card Name`.

The deck name follows "Commander – Theme or nickname (B3.75)". Make the nickname playful, like the
player's other decks (e.g. "Kenrith – Big Booty", "Talrand – Counter Target Dan").

`<slug>.md` is the primer, in light markdown: `## ` headings, `- ` bullets, `**bold**`, and `[[Card Name]]`
links. Keep it about 300–550 words (as `wc -w` counts them), in plain, direct English. It's public on Archidekt, so write for any
player picking up the deck: state combos, odds and card counts as plain facts about the deck ("Etali
usually lands by turn 5–6"). Never mention our tools in a primer (no "the checker", "goldfish sim" or
script names); tooling and build notes go in your reply to the player. Sections:
1. One or two lines on what the deck is and why it's fun.
2. `## How it plays`: early, mid and late game, ending on the deck's **signature turn**: two or three
   sentences narrating the turn the deck is built for (the turn to aim at, not a typical one), so a new
   pilot knows what to aim at. It can stand in for the late game.
3. `## How it wins`: list the win routes. Name any late-game combos and what they need.
4. `## Key cards`: 6–10 bullets, each with what the card actually does, checked against oracle text.
5. `## Tips`: sequencing, plus two bullets every primer has. **Mulligan:** what a keepable seven looks
   like for this deck (lands, colours, the early play it needs), grounded in how often a random seven is
   keepable. **Politics:** how to play the table: who to make deals with, when to be the villain and when
   to look harmless, which cards will draw hate.

## Check before you finish
```
scripts/check_commander.py decks/commander/<slug>.txt          # --allow-ub only where UB is approved
scripts/deck_stats.py decks/commander/<slug>.txt               # role counts, mana sources, goldfish
scripts/table_feel.py decks/commander/<slug>.txt               # salt, table interaction, a Rule 0 pitch
scripts/originality.py decks/commander/<slug>.txt              # same-99 share, overlap with your decks
```
The checker's `!!` lines are flags, not verdicts: fix them or explain why the deck is still in
moderation. It asks Commander Spellbook which combos the deck contains and marks an infinite combo
`FAST` (pieces total mana value 6 or less, or Spellbook rates it Ruthless/Banned), the proxy for "could
win on turn 2 or 3". **The primer's combo claims must come from this output**: name every included combo
that is infinite or wins the game, say what it needs, and don't claim combos the checker didn't list.
`--near` shows combos one card away (for suggestions, or to avoid leaving one half-built).
Its bracket line shows the official WotC bracket next to the house verdict: "around 4 Game Changers"
is officially Bracket 4, so `Official B4 · House 3.75 ✓` is a normal result for these decks.
`deck_stats.py` flags LOW/HIGH role counts against generic targets; judge them against the deck's plan.
Also look at the land count (usually 35–37, fewer with heavy ramp) and the curve.

While building, only write the two deck files: uploading to Archidekt is a separate step (see
`.claude/skills/commander-deck`), done when the player has asked for it. Deck files are never committed.

End your reply with the checker's output, your Game Changers and why you chose them, and anything you
weren't sure about.
