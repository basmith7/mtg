Mono-red roulette. Q pulls one random spell out of your library, and from then on every card in your hand can become another copy of it. Every nonland card in the deck is worth copying, so each game asks which jackpot Q hands you.

## How it plays
**Early:** ramp. [[Sol Ring]], [[Arcane Signet]] and [[Ruby Medallion]] get Q down on turn 3 or 4. Keep spare lands in hand: they're fuel.

**Mid:** cast Q. It exiles cards from the top until it hits a nonland card, and that card gains "Exile a card from your hand: Create a copy of this card. You may cast the copy." You pay the copy's mana cost, and only on your turn. The ability lives on the exiled card, so it keeps working if Q dies. Make Q enter again for more jackpots: [[Helm of the Host]], [[Splinter Twin]], [[Molten Echoes]] (name "Q"), [[Mirror March]], [[Conjurer's Closet]], [[Heat Shimmer]], and [[Panharmonicon]] for two hits at once.

**Late:** refill your hand with wheels, then cash it in. In goldfish testing, Q triggers about 4–5 times by turn 10 and casts about 6 copies. A typical big turn is 2–3 copies, and 1 game in 6 has a 5-copy turn. Mana and spare cards run out at about the same rate, so wheels, [[Seething Song]] and [[Brass's Bounty]] are the hits that keep a turn going.

## How it wins
- **Burn by the handful:** copied [[Fireball]], [[Comet Storm]], [[Banefire]] or [[Lightning Bolt]], made bigger by [[Guttersnipe]], [[Torbran, Thane of Red Fell]] or [[Fiery Emancipation]].
- **Token armies:** copies of [[Terror of the Peaks]], [[Inferno Titan]] or [[Siege-Gang Commander]].
- **Backup combos.** The pieces also work as Q cards, but in goldfish testing (`scripts/sim_q.py`) a combo lands by turn 10 in only about 16% of games:
  - **Dualcaster:** cast [[Heat Shimmer]], [[Twinflame]] or [[Electroduplicate]], then flash in [[Dualcaster Mage]] to copy it onto itself. Each new Dualcaster copies the spell again, for infinite hasty tokens.
  - **Endless combat:** [[Combat Celebrant]] wearing [[Helm of the Host]], enchanted with [[Splinter Twin]], or copied by [[Fable of the Mirror-Breaker // Reflection of Kiki-Jiki]]'s Reflection. A fresh, unexerted copy each combat means another combat each time.
  - **Table nuke:** [[Blasphemous Act]] with [[Repercussion]] out deals each player 13 damage per creature they control, you included.

## Key cards
- [[Wheel of Fortune]]: each player discards their hand and draws seven. If Q exiles it, each copy is a fresh seven for three mana.
- [[Birgi, God of Storytelling // Harnfel, Horn of Bounty]]: adds R whenever you cast a spell, copies included.
- [[Molten Echoes]]: name Q. A token copy of Q enters with it and triggers again; the legend rule then makes you keep one.
- [[Rite of the Raging Storm]]: every player gets a hasty 5/1 trampler each upkeep that can't attack you. Copies stack, so the table fights itself.
- [[Tempt with Vengeance]]: X hasty 1/1s for you. Each opponent may take X too, and you get X more for each who does.
- [[Fiery Gambit]]: keep flipping coins. With three wins you draw nine cards (a full tank of fodder) and untap your lands.
- [[Combat Celebrant]]: exert it as it attacks to untap your other creatures and get another combat phase.

## Tips
- Steal hits are table events: a few copies of [[Act of Treason]] borrow everyone's best creature, and copied [[Mob Rule]] can take both the big and the small creatures in one turn.
- Exile lands from hand first.
- Q only copies on your turn, so copied removal is proactive.
- A legendary hit like [[Torbran, Thane of Red Fell]] copies poorly; cast one and keep the rest of your hand.
- Wheels feed the table. Fire them when your hand is empty and theirs isn't.
- Mulligan for 3–4 lands and a mana rock.
