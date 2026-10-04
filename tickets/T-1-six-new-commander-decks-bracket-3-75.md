---
id: T-1
title: Six new Commander decks (bracket ~3.75)
status: doing
labels: []
depends: []
created: 2026-10-04T17:40:04Z
updated: 2026-10-04T17:40:08Z
kind: build
risk: low
riskReason: Only creates new Archidekt decks; nothing existing is changed or deleted
size: medium
---
Build and upload to Archidekt's Commander folder (1914431), for online play:
Karazikar, the Eye Tyrant · Jon Irenicus, Shattered One · Tivit, Seller of Secrets · Gluntch, the Bestower · Maelstrom Wanderer · The Wise Mothman.

Rules from Brian: fun first, winning second. Bracket "3.75" = strong 3 / light 4: at most 4 Game Changers, real tutors and interaction, no fast-mana package, combos only ones that win late. Avoid Universes Beyond cards, except in the Mothman deck where UB rad cards are fine.

## Done when
- [ ] Six 100-card lists in decks/commander/ pass check_commander.py (singleton, colour identity, Commander-legal, Game Changers ≤ 4, no UB outside Mothman)
- [ ] Each deck has a primer (how it plays, key cards checked against Scryfall oracle text)
- [ ] All six are on Archidekt in the Commander folder with 100 cards, the commander in the Commander category, and the primer attached
