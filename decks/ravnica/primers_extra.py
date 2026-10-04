"""Primers for the 12 extra Ravnica decks (same light markup as primers_core)."""
from primers_core import COMMON_LANDS

PRIMERS = {
'11_dimir_cipher.txt': """**House Dimir's** spies carry coded messages. **Cipher** spells get "encoded" on an unblockable creature and are recast for free every time it connects.

## How it wins
Land cheap unblockable creatures, encode spells on them, and let every hit tap blockers, drain life, make fliers or rip apart the opponent's hand.

## Mechanics to know
- **Cipher:** after the spell resolves, you may exile it "encoded" on a creature you control. Whenever that creature deals combat damage to a player, you cast a free copy. If the creature leaves play, the encoded spell is lost, so encode on your hardest-to-kill evasive creature.

## Key cards
- [[Dimir Infiltrator]], [[Deathcult Rogue]] and [[Duskmantle Operative]] are your cipher carriers. They're hard or impossible to block.
- [[Hands of Binding]] taps a blocker and locks it down for a turn, then repeats every hit.
- [[Undercity Plague]] encoded means every hit makes them lose life, discard, *and* sacrifice a permanent.
- [[Etrata, the Silencer]] exiles a creature on each hit. Three "hit" counters on an opponent's exiled cards wins the game.
- [[Lazav, the Multifarious]] becomes a copy of any creature in your graveyard.

## Tips
- Spread encodes across two carriers so one removal spell doesn't undo everything.
- [[Rogue's Passage]] makes any creature unblockable for a turn.
""",
'12_golgari_saprolings.txt': """**The Golgari** recycle everything. Dead creatures sprout fungus, and insects swarm out of the graveyard. This is a token swarm built on death and mill.

## How it wins
Make piles of 1/1 Saprolings and Insects from creatures dying and cards leaving your graveyard, then eat the board with removal or swarm the opponent.

## Mechanics to know
- **Saprolings:** 1/1 green fungus tokens. Several cards here make them when creatures die or get milled.
- **Cards leaving your graveyard** (returning them, exiling them) triggers [[Amzu, Swarm's Hunger]] and [[Insidious Roots]].

## Key cards
- [[Tribune of Rot]] mills two each attack and makes a Saproling per creature milled.
- [[Golgari Germination]]: every nontoken creature that dies leaves a Saproling.
- [[Insidious Roots]] lets every creature token tap for any color of mana, and grows Plants when cards leave your graveyard.
- [[Izoni, Thousand-Eyed]] makes an Insect per creature in your graveyard, then sacrifices them to draw.
- [[Savra, Queen of the Golgari]] makes opponents sacrifice when you sacrifice black creatures.
- [[Amzu, Swarm's Hunger]] makes big Insects whenever cards leave your graveyard.

## Tips
- Tokens + [[Insidious Roots]] = lots of mana. Cast multiple spells a turn.
- [[Fungal Rebirth]] is best after something died this turn: get the card back *and* two Saprolings.
""",
'13_izzet_niv.txt': """**Niv-Mizzet** is the dragon genius who founded the Izzet League. This deck is about drawing cards, because every card you draw shoots someone.

## How it wins
Land a Niv-Mizzet, then cast cheap draw spells. Each card drawn deals 1 damage. Pingers and spell-triggers finish the job.

## Mechanics to know
- Nothing new. The trick is **draw triggers**: "whenever you draw a card" fires once per card, even in the middle of a spell.

## Key cards
- [[Niv-Mizzet, Parun]]: draw on *any* instant or sorcery cast, and ping on each draw. Uncounterable.
- [[Niv-Mizzet, the Firemind]]: taps to draw, pings on each draw. [[Niv-Mizzet, Dracogenius]] pings for {U}{R} and draws when it hits a player. The three Nivs are different cards, so you can have all three out.
- [[Electrostatic Field]] and [[Gelectrode]] deal damage whenever you cast instants or sorceries.
- [[Cerebral Vortex]] makes a player draw two and damages them per card drawn that turn. It's a finisher on an opponent, or card draw for you.
- [[Ral, Storm Conduit]] pings with every instant or sorcery and copies a spell.

## Tips
- With a Niv out, cast [[Electrolyze]] or [[Chemister's Insight]] at the end of the opponent's turn for double value.
- Protect Niv. Hold [[Izzet Charm]] to counter a removal spell (unless they pay {2}).
""",
'14_rakdos_devils.txt': """**Rakdos devils** are gleeful little monsters that explode when they die. This deck sacrifices its own creatures to burn the opponent out.

## How it wins
Every creature that dies, and every permanent you sacrifice, deals damage. Sacrifice your team at the right moment to finish the game.

## Mechanics to know
- **Sacrifice:** put your own permanent into the graveyard as a cost. Here it's a resource. Your creatures want to die.
- **Clues** (from [[Carnage Interpreter]]) are artifacts you sacrifice for {2} to draw a card. They also trigger "whenever you sacrifice".

## Key cards
- [[Mayhem Devil]]: whenever *any* player sacrifices a permanent (including Clues and opponents' sacrifices), deal 1 damage.
- [[Footlight Fiend]] and [[Tibalt's Rager]] ping when they die.
- [[Priest of Forgotten Gods]]: sacrifice two creatures to make opponents lose 2 and sacrifice a creature, plus {B}{B} and a card.
- [[Judith, the Scourge Diva]] gives your team +1/+0 and pings when your nontoken creatures die.
- [[Carnage Interpreter]] discards your hand for four Clues, and is a 5/5 menace while you have one or fewer cards in hand.

## Tips
- Don't sacrifice randomly. Hold sacrifice outlets until blockers are declared, or until it finishes the opponent.
- [[Plaguecrafter]] and [[Angrath's Rampage]] make *opponents* sacrifice, which triggers [[Mayhem Devil]] too.
""",
'15_orzhov_ghosts.txt': """**The Orzhov Ghost Council** rules from beyond the grave. Ghosts haunt the living, and every spell you cast extorts a tithe.

## How it wins
Extort drains a little every spell, haunt cards trigger twice, and you outlast the opponent behind removal and lifegain.

## Mechanics to know
- **Extort:** whenever you cast a spell, you may pay {W/B} per extort permanent. Each opponent loses 1 life and you gain 1.
- **Haunt:** when the card dies (or the spell resolves), exile it "haunting" a creature. When *that* creature dies, the effect happens again. Haunt an opponent's creature you plan to kill, or your own creature that will die soon.

## Key cards
- [[Pontiff of Blight]] gives *all* your creatures extort.
- [[Crypt Ghast]] doubles mana from Swamps, more mana for extort payments.
- [[Seize the Soul]], [[Orzhov Euthanist]] and [[Blind Hunter]] are haunt removal and drain that fire twice.
- [[Obzedat, Ghost Council]] drains 2 on entering, and can blink out at end of turn to dodge sorcery-speed removal and drain again.
- [[Teysa, Orzhov Scion]] makes Spirits when black creatures die, and exiles creatures by sacrificing white ones.

## Tips
- Cheap spells are extort engines. Play two cheap spells rather than one big one when you can pay extort.
- This is a grindy deck. Trade, gain life and let extort win.
""",
'16_simic_graft.txt': """**The Simic Combine's** original experiment, from the first Ravnica era: **graft**, moving living tissue (counters) from one creature to another.

## How it wins
Graft creatures enter loaded with +1/+1 counters, then hand them to each new creature, so your whole board grows and adapts to any threat.

## Mechanics to know
- **Graft N:** enters with N +1/+1 counters. Whenever *another* creature enters (yours or theirs), you may move one counter from this onto it. Usually move onto your own creatures.
- Many cards care about "creatures with a +1/+1 counter".

## Key cards
- [[Vigean Hydropon]] enters with 5 counters but can't attack or block. It's a pure counter battery.
- [[Cytoplast Manipulator]]: steal any creature with a +1/+1 counter. Graft a counter onto *their* creature first if you need to.
- [[Experiment Kraj]] gains every activated ability of your other countered creatures and adds counters itself.
- [[Vorel of the Hull Clade]] doubles all counters on a creature.
- [[Bioshift]] moves counters at instant speed to save a creature or make a surprise attacker.

## Tips
- Opponents' creatures entering also trigger graft, so you *may* move counters, but don't.
- [[Plaxcaster Frogling]] gives shroud to a countered creature to protect your best one.
""",
'17_azorius_filibuster.txt': """**The Azorius Senate's** real weapon is procedure. This is a control deck that buries the opponent in paperwork and can win by simply talking until they give up.

## How it wins
Counter spells, sweep the board, draw cards, and win with fliers, or with [[Azor's Elocutors]] reaching five filibuster counters.

## Mechanics to know
- **Forecast:** during your upkeep, reveal the card from your hand and pay its forecast cost for an effect while keeping the card.
- **Addendum:** an instant with a bonus if cast during your main phase.

## Key cards
- [[Azor's Elocutors]] gets a filibuster counter every upkeep and wins at five. Any damage to you removes one, so keep the board clear.
- [[Supreme Verdict]] is an uncounterable board wipe.
- [[Grand Arbiter Augustin IV]] makes your spells cheaper and theirs more expensive.
- [[Lavinia, Azorius Renegade]] stops expensive noncreature spells early and counters free spells.
- [[Sky Hussar]] (forecast) taps two creatures in your upkeep to draw a card.
- [[Pride of the Clouds]] (forecast) makes a flying Bird every upkeep.

## Tips
- Be patient. Play at instant speed: hold counters, and cast flash creatures like [[Hussar Patrol]] at end of turn.
- Wipe the board before landing Elocutors, then protect it with counters.
""",
'18_gruul_ramp.txt': """**The Gruul Clans** worship the giant cyclops Borborygmos. This deck ramps hard into the biggest monsters on Ravnica.

## How it wins
Mana creatures and land ramp on turns 1–3, then 6- to 11-mana monsters from turn 4 on.

## Mechanics to know
- **Bloodrush:** discard the card to give an attacking creature its stats as a pump. [[Rubblehulk]] gives +X/+X equal to your land count.

## Key cards
- [[Zhur-Taa Druid]] taps for mana and pings each opponent. [[Paradise Druid]] taps for any color and has hexproof while untapped.
- [[Zhur-Taa Ancient]] doubles every land's mana, *for everyone*. Make sure you're the one who can use it.
- [[Borborygmos Enraged]]: discard lands to deal 3 damage each, and refills on lands when it connects.
- [[Worldspine Wurm]] leaves three 5/5 tramplers when it dies.
- [[End-Raze Forerunners]] is a hasty finisher that pumps the whole team.
- [[Gruul Ragebeast]]: each creature you play fights an opponent's creature.

## Tips
- Keep hands with a mana creature or [[Farseek]]. Ramp is the whole plan.
- Late in the game, spare lands are ammo for [[Borborygmos Enraged]].
""",
'19_dreadhorde.txt': """**The War of the Spark:** Nicol Bolas invaded Ravnica with an army of undead Eternals. This deck builds that one giant zombie Army.

## How it wins
Almost every card adds counters to a single Army token, growing it into a huge threat while your spells clear blockers.

## Mechanics to know
- **Amass Zombies N:** put N +1/+1 counters on your Army creature token. If you don't have one, first create a 0/0 black Zombie Army. You only ever have one Army, and every amass makes it bigger.

## Key cards
- [[Dreadhorde Invasion]]: amass 1 every upkeep (lose 1 life), and a 6+ power Zombie token attacking gains lifelink.
- [[Gleaming Overseer]] gives your Zombie tokens hexproof and menace, protecting the Army.
- [[Widespread Brutality]] amasses 2, then your Army deals damage to every other creature. A one-sided-ish wipe.
- [[Nicol Bolas, Dragon-God]]: draws, removes, steals other planeswalkers' abilities, and can win outright with -8.
- [[Liliana, Dreadhorde General]] makes Zombies and draws a card whenever your creatures die.
- [[Commence the Endgame]]: an uncounterable instant that draws two and amasses equal to your hand size.

## Tips
- Removal is the Army's enemy. Play [[Gleaming Overseer]] before investing heavily in it.
- Three colors: play your lands to keep all of {U}{B}{R} available. Black is the main color.
""",
'20_detectives.txt': """**Murders at Karlov Manor:** the Ravnica Agency's detectives investigate a murder. Lots of small Detectives, lots of Clues, lots of cards.

## How it wins
Go wide with Detectives that pump each other, crack Clues for cards, and fly over for damage.

## Mechanics to know
- **Investigate:** create a Clue token, an artifact with "{2}, sacrifice: draw a card". Crack Clues when you have spare mana.
- **Disguise:** cast face down for {3} as a 2/2 with ward {2}, then turn face up any time for its disguise cost.
- **Cases:** enchantments with a "To solve" condition. When solved at end of turn, they gain a bonus.

## Key cards
- [[Private Eye]] gives other Detectives +1/+1, and makes one unblockable when you draw your second card each turn. Crack a Clue on your turn!
- [[Case of the Pilfered Proof]] puts a +1/+1 counter on each Detective entering. Solved, your tokens come with a bonus Clue.
- [[Perimeter Enforcer]] is a lifelink flier that grows when Detectives enter.
- [[Ezrim, Agency Chief]] is a 5-mana flier with two Clues.
- [[Alquist Proft, Master Sleuth]] cashes in Clues for X cards and X life.

## Tips
- Crack a Clue at the end of the opponent's turn unless you need [[Private Eye]]'s second-draw trigger on your own turn.
- [[Inside Source]] and [[Museum Nightwatch]] make 2/2 Detective tokens, which count for everything.
""",
'21_superfriends.txt': """**War of the Spark** brought dozens of planeswalkers to Ravnica. This deck plays as many as possible and protects them.

## How it wins
Land planeswalker after planeswalker. Each one generates value every turn while your removal and counters keep attackers off them. Win with ultimates, Gideon and drain.

## Mechanics to know
- **Proliferate:** choose any number of permanents and/or players with counters and add one more of each kind. Here it means **extra loyalty on all your planeswalkers at once**.
- Many War of the Spark planeswalkers have a **static ability** that works all the time, plus only minus abilities.

## Key cards
- [[Teferi, Time Raveler]] stops opponents casting at instant speed and bounces a threat.
- [[Narset, Parter of Veils]] stops opponents drawing more than one card a turn. [[Ob Nixilis, the Hate-Twisted]] pings them for every card they draw.
- [[Gideon Blackblade]] is a 4/4 indestructible attacker on your turn.
- [[Flux Channeler]] proliferates every time you cast a noncreature spell, and planeswalkers count.
- [[Tomik, Wielder of Law]] is cheaper per planeswalker, and punishes opponents who attack with two or more creatures.
- [[Interplanar Beacon]] makes two colors of mana for planeswalkers. [[Karn's Bastion]] proliferates.

## Tips
- Protect first: a planeswalker with no blockers or removal behind it just dies.
- Use minus abilities early on cheap planeswalkers. They're meant to be spent.
""",
'22_guildpact.txt': """**The Guildpact** is the magical treaty that binds all ten guilds. This five-color deck plays one of every guildgate, every guild charm, and both five-color Niv-Mizzets.

## How it wins
Ramp out gates, draw cards off them, and either win with [[Maze's End]] (10 different gates) or overpower the opponent with gold cards and the five-color dragons.

## Mechanics to know
- **Gates:** every guildgate and [[Gateway Plaza]] is a Gate. Many cards count or fetch Gates.
- **Maze's End:** {3}, tap, return it to hand to fetch any Gate onto the battlefield. If you then control **10 Gates with different names, you win**. You have 11 different Gates in the deck.

## Key cards
- [[Gatecreeper Vine]], [[District Guide]] and [[Circuitous Route]] find your Gates.
- [[Guild Summit]] draws a card for each Gate you tap when it enters, and for every new Gate after.
- [[Niv-Mizzet Reborn]] reveals your top 10 and takes one card for each two-color pair. With this many gold cards that's usually several.
- [[Leyline of the Guildpact]] (start with it in play) makes your lands every basic type, which fixes everything.
- Ten charms, one per guild: each has three modes. Read them, because each is your answer to something.

## Tips
- Prioritize *different* Gates. Duplicates don't help [[Maze's End]].
- [[Gate Colossus]] gets very cheap, and returns from your graveyard to the top of your library whenever a Gate enters.
""",
}

for k in PRIMERS:
    lands = (COMMON_LANDS if k != '22_guildpact.txt' else
             "**Lands:** gates enter tapped, so the deck starts slow. Play a tapped Gate every turn you can, and use [[Plaza of Harmony]] for any color your Gates make.")
    PRIMERS[k] = PRIMERS[k].rstrip() + "\n\n## Mana\n" + lands + "\n"
