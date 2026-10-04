"""Primers for the ten guild decks (power versions). Light markup:
'## ' heading, '- ' bullet, **bold**, [[Card]] links; blank line between blocks."""

COMMON_LANDS = ("**Lands:** shock lands (pay 2 life or they enter tapped) and surveil lands "
                "(enter tapped, surveil 1) fix your mana. Play shocks untapped only when you need the mana that turn.")

PRIMERS = {
'01_boros.txt': """**The Boros Legion** is Ravnica's army and police force: disciplined soldiers who win by attacking together, every single turn.

## How it wins
Flood the board with cheap creatures, grow them with mentor, and finish with burn. Most games end by turn 6 or 7.

## Mechanics to know
- **Mentor:** when this creature attacks, put a +1/+1 counter on another attacking creature with lower power. Attack with mentors alongside small creatures.
- **Battalion:** triggers when this creature and at least two others attack.

## Key cards
- [[Legion Warboss]] makes a hasty Goblin every combat that must attack, and mentors it.
- [[Aurelia, the Warleader]] untaps your team and gives you a second combat. [[Aurelia, Exemplar of Justice]] pumps and gives trample.
- [[Truefire Captain]] deals damage to a player whenever it's dealt damage, so blocking it hurts.
- [[Boros Charm]]: 4 to the face, indestructible for your team against a sweeper, or double strike for the kill.
- [[Warleader's Call]] pumps the team and pings every opponent each time a creature enters.

## Tips
- Attack every turn. Your creatures are worse on defense than theirs.
- Save [[Lightning Helix]] and [[Lightning Bolt]] for blockers early, and for the opponent's face late.
""",
'02_selesnya.txt': """**The Selesnya Conclave** is a nature cult where everyone joins the collective. The deck goes wide with tokens and makes the whole army bigger.

## How it wins
Make Centaurs, Wurms and Soldiers, pump them all at once, and swarm. It's resilient against removal because every card is a body.

## Mechanics to know
- **Convoke:** tap your creatures to help pay a spell's cost. Each creature pays {1} or one mana of its color. Cast big spells early by tapping tokens.
- **Populate:** create a copy of a creature token you already control. Copy your best token, like a 5/5 Wurm.

## Key cards
- [[Voice of Resurgence]] punishes instant-speed tricks on your turn and leaves a big Elemental behind when it dies.
- [[Trostani Discordant]] pumps the team and makes two lifelink Soldiers. [[Trostani, Selesnya's Voice]] gains life and populates every turn.
- [[March of the Multitudes]] is an instant convoke army, at the end of the opponent's turn or as a surprise block.
- [[Conclave Tribunal]] is convoke removal that often costs almost nothing.
- [[Unbreakable Formation]] protects you from a board wipe, or gives a pump and counters when cast main phase.

## Tips
- Don't overextend into a likely board wipe unless you're holding [[Unbreakable Formation]] or [[Selesnya Charm]].
- [[Emmara, Soul of the Accord]] makes a Soldier whenever it taps, so convoking with Emmara is free value.
""",
'03_izzet.txt': """**The Izzet League** are mad scientists and inventors who love explosive experiments. The deck casts lots of cheap instants and sorceries in a single turn.

## How it wins
Chain cheap spells to grow your threats, bring back [[Arclight Phoenix]], and burn the opponent out.

## Mechanics to know
- **Jump-start:** cast this card from your graveyard by discarding a card in addition to its cost, then exile it. [[Radical Idea]] is two spells in one.
- **Overload / replicate:** some spells can hit every target or be copied for extra mana. Read them carefully.

## Key cards
- [[Goblin Electromancer]] makes every instant and sorcery cost {1} less.
- [[Arclight Phoenix]]: if you've cast **three or more instants or sorceries** this turn, it returns from your graveyard to the battlefield at the start of combat, flying and hasty. Discarding it to jump-start is a plan, not a waste.
- [[Crackling Drake]] has power equal to your instants and sorceries in graveyard and exile.
- [[Niv-Mizzet, Parun]] draws a card whenever *anyone* casts an instant or sorcery, and pings for 1 whenever you draw.
- [[Murmuring Mystic]] makes a 1/1 flying Bird for every instant or sorcery you cast.

## Tips
- Plan "big turns": hold two or three cheap spells and fire them together for Phoenix or Mystic value.
- Count your graveyard before casting [[Crackling Drake]]. It's best after a few turns of spells.
""",
'04_golgari.txt': """**The Golgari Swarm** tends Ravnica's undercity, where death feeds new growth. The deck uses its graveyard as a second hand.

## How it wins
Fill your graveyard early, then get value from it with big undergrowth creatures, recursion and efficient removal. Grind the opponent out.

## Mechanics to know
- **Undergrowth:** counts the number of creature cards in your graveyard. More dead creatures make these cards stronger.
- **Mill:** put cards from the top of your library into your graveyard. Here that's a resource, not a cost.

## Key cards
- [[Underrealm Lich]]: whenever you'd draw, look at the top three, keep one and put the rest in your graveyard. Pay 4 life to make it indestructible.
- [[Izoni, Thousand-Eyed]] makes an Insect for each creature in your graveyard, then sacrifices them to draw cards.
- [[Jarad, Golgari Lich Lord]] grows with your graveyard and drains by sacrificing creatures.
- [[Golgari Findbroker]] returns any permanent card from your graveyard.
- [[Assassin's Trophy]], [[Abrupt Decay]] and [[Putrefy]] answer almost anything.
- [[Deathrite Shaman]] gives early mana if there are lands in graveyards, and later drains or gains life.

## Tips
- Early on, mill aggressively with [[Glowspore Shaman]] and [[Grisly Salvage]]. Glowspore can put a land back on top if you need one.
- [[Kraul Harpooner]] kills an opposing flier when undergrowth is high, so hold it for a flier.
""",
'05_rakdos.txt': """**The Cult of Rakdos** are Ravnica's performers, a demonic circus that turns violence into entertainment. The deck is fast and punishing.

## How it wins
Hit the opponent early with cheap, hasty creatures, then use **spectacle** cards to cast spells at a discount and finish them off.

## Mechanics to know
- **Spectacle:** you may cast the card for its cheaper spectacle cost if an opponent **lost life this turn**. Attack or ping first, then cast.
- **Unleash** (on [[Rakdos Cackler]]): enters with a +1/+1 counter if you want, but then it can't block. Usually take the counter.

## Key cards
- [[Skewer the Critics]] deals 3 damage for {R} with spectacle.
- [[Rix Maadi Reveler]]: with spectacle, discard your hand and draw three.
- [[Rakdos, Lord of Riots]] can only be cast after an opponent lost life this turn, and makes your creatures cheaper by the life they lost.
- [[Judith, the Scourge Diva]] gives your team +1/+0 and pings when your creatures die, so trades hurt them.
- [[Gutterbones]] returns from your graveyard to your hand during your turn, once an opponent has lost life.

## Tips
- Order matters: attack before casting spectacle spells in your second main phase.
- [[Dreadbore]] and [[Bedevil]] clear blockers. Burn goes to the face once they're low.
""",
'06_azorius.txt': """**The Azorius Senate** writes and enforces Ravnica's laws: lawmages, judges and bureaucrats. The deck controls the board and wins in the air.

## How it wins
Deploy efficient fliers, lock down the opponent's best creature, and counter their key spells.

## Mechanics to know
- **Detain:** until your next turn, the target can't attack or block and its activated abilities can't be used. Detain a blocker, then swing.
- **Forecast:** during your upkeep, reveal the card from your hand and pay for a bonus effect while keeping the card. [[Pride of the Clouds]] makes a Bird each upkeep.
- **Addendum:** a bonus if you cast the instant during your own main phase.

## Key cards
- [[Teferi, Time Raveler]]: opponents can only cast spells at sorcery speed, so no combat tricks or counterspells. Its -3 bounces a threat and draws.
- [[Detention Sphere]] exiles a permanent, and every other copy of it with the same name.
- [[Lyev Skyknight]] is a flier that detains on arrival.
- [[Isperia, Supreme Judge]] draws a card every time a creature attacks you.
- [[Dovin's Veto]] and [[Absorb]] counter key spells. [[Sphinx's Revelation]] refuels late.

## Tips
- You're the control deck in most matchups. Don't race; trade, counter, and let the fliers do the work.
- Keep 2 mana open for counters on the opponent's turn when you've already developed.
""",
'07_dimir.txt': """**House Dimir** is Ravnica's secret guild of spies, assassins and information brokers. The deck is evasive, sneaky and full of answers.

## How it wins
Evasive threats chip in while removal and counterspells keep the opponent off balance. Surveil keeps your draws sharp.

## Mechanics to know
- **Surveil N:** look at the top N cards of your library, put any into your graveyard and the rest back in any order. Many cards here reward you for surveilling.

## Key cards
- [[Dimir Spybug]] is a flying menace creature that grows each time you surveil.
- [[Darkblade Agent]] has deathtouch and draws a card on combat damage once you've surveilled this turn.
- [[Thief of Sanity]]: when it hits, look at the opponent's top three cards, steal one, and cast it with any mana.
- [[Notion Thief]] (flash): opponents' extra draws become *your* draws.
- [[Doom Whisperer]] is a 6/6 flying trampler for 5. Pay 2 life to surveil 2 whenever you like.
- [[Lazav, Dimir Mastermind]] becomes a copy of creatures that hit the opponent's graveyard.

## Tips
- Surveil before combat when you have [[Darkblade Agent]] or [[Whispering Snitch]] out.
- Don't over-surveil away good cards. It's selection, not a free mill.
""",
'08_orzhov.txt': """**The Orzhov Syndicate** is a church that's also a crime family, run by ghosts who collect debts even after death. Every creature that dies still pays out.

## How it wins
Creatures that leave ghosts behind, plus drain effects, slowly bleed the opponent while you gain life. Trading creatures is good for you.

## Mechanics to know
- **Afterlife N:** when this creature dies, create N 1/1 white and black flying Spirits.
- **Extort:** whenever you cast a spell, you may pay {W/B}. Each opponent loses 1 life and you gain that much. Each extort permanent triggers separately.

## Key cards
- [[Teysa Karlov]] makes every death trigger (afterlife, [[Cruel Celebrant]], [[Vein Ripper]]) happen **twice**, and gives your tokens vigilance and lifelink.
- [[Cruel Celebrant]] drains 1 whenever your creatures die.
- [[Vein Ripper]] drains 2 whenever *any* creature dies. Opponents must sacrifice a creature to target it.
- [[Karlov of the Ghost Council]] grows by two counters every time you gain life, then exiles creatures.
- [[Afterlife Insurance]] gives your whole team afterlife for a turn and draws a card. Cast it before a big attack or a board wipe.

## Tips
- Attack into bad trades on purpose. Your creatures are worth more dead than theirs.
- Leave mana up for extort when you can. Each extort trigger is a 2-point life swing.
""",
'09_simic.txt': """**The Simic Combine** are biologists who splice creatures into impossible hybrids. Everything grows with +1/+1 counters.

## How it wins
Grow a board of creatures that keep getting bigger, then use the counters for card draw, fights, or an alternate win with [[Simic Ascendancy]].

## Mechanics to know
- **Evolve:** whenever a creature with greater power **or** toughness enters under your control, put a +1/+1 counter on this creature. Play creatures in increasing size.
- **Adapt N:** if this creature has no +1/+1 counters, put N on it. It doesn't work again while counters remain, except with [[Biomancer's Familiar]].

## Key cards
- [[Growth-Chamber Guardian]]: whenever it gets counters, fetch another copy from your library.
- [[Biomancer's Familiar]] makes adapt costs {2} cheaper and lets a creature adapt again even with counters.
- [[Lonis, Genetics Expert]] investigates (makes a Clue) whenever it gets counters. Sacrifice Clues to draw and to place more counters.
- [[Master Biomancer]] makes every later creature enter with extra counters.
- [[Hydroid Krasis]]: X spell. When you cast it, draw half X and gain half X life, even if it's countered.
- [[Simic Ascendancy]] wins the game at 20 growth counters. Every counter you place adds to it.

## Tips
- Sequence creatures smallest to largest to maximize evolve.
- [[Mutant's Prey]] and [[Titanic Brawl]] are your removal and need a creature with counters, so set them up.
""",
'10_gruul.txt': """**The Gruul Clans** are the rubble-dwelling rebels who reject civilization. The deck smashes with big, hasty creatures.

## How it wins
Curve out with creatures that get bigger or hasty, fight anything in the way, and trample through.

## Mechanics to know
- **Riot:** the creature enters with your choice of a +1/+1 counter **or** haste. Take haste to surprise-attack, the counter when you're not attacking this turn.
- **Bloodrush:** discard the card from your hand and pay its cost to give an attacking creature its bonus, an instant-speed pump that can't be "blocked".

## Key cards
- [[Burning-Tree Emissary]] gives back {R}{G} when it enters, so play another 2-drop the same turn.
- [[Pelt Collector]] grows each time a bigger creature enters or dies, and gets trample at 3 counters.
- [[Herald of Ilharg]] gets two counters per creature you cast, and deals damage to opponents when you cast big ones.
- [[Ilharg, the Raze-Boar]]: when it attacks, put a creature from your hand onto the battlefield attacking. It returns to your hand at end of turn.
- [[Rhythm of the Wild]] gives every creature riot and makes them uncounterable.
- [[Domri's Ambush]] and [[Savage Smash]] are fight-style removal.

## Tips
- Fight spells need your creature to survive. Use them with your biggest creature, ideally after a counter.
- Hold [[Ghor-Clan Rampager]] in hand as a bloodrush trick when an attack would otherwise stall.
""",
}

for k in PRIMERS:
    PRIMERS[k] = PRIMERS[k].rstrip() + "\n\n## Mana\n" + COMMON_LANDS + "\n"
