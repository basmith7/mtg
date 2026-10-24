#!/usr/bin/env python3
"""Numbers for a decklist: role counts, mana base, a goldfish simulation and the curve.

    scripts/deck_stats.py decks/commander/ruric_thar.txt
    scripts/deck_stats.py --games 20000 --seed 7 decks/commander/*.txt

Roles come from Scryfall oracle tags (`otag:`), one query per role restricted to the deck's cards;
answers are cached per card in ~/.cache/mtg/deck_stats_roles.json. Tags are crowd-sourced and a bit noisy,
so each role query also excludes lands and overlapping roles; read the card lists, not just counts.
Known noise: ramp counts rituals and treasure makers, removal counts burn and pingers, and
land-or-spell cards (Valakut Awakening) count as neither lands nor ramp, so LOW flags can be false.
LOW/HIGH flags judge against generic targets; a deck's plan can rightly break them. The goldfish
pays coloured pips and commander tax but plays nothing except lands, ramp and the commander.
Each colour's source count is judged against goldfish.sources_needed() for the card that needs the most.
Commander lists (a 'Commander:' line) are 99-card libraries; other lists are treated as 60-card.
"""
import argparse
import os
import random
import sys
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT)
from mtg import decklist, scryfall
from mtg.cards import is_land
from mtg.goldfish import Card, Cost, faces, land_produces, mana_producer, pips, simulate, sources_needed
from mtg.roles import ROLES, SHOW, TARGETS, TARGETS_60, role_hits

TYPES = ['Land', 'Creature', 'Planeswalker', 'Battle', 'Artifact', 'Enchantment', 'Instant', 'Sorcery']


def main_type(c):
    tl = c['type_line'].split('//')[0]
    return next((t for t in TYPES if t in tl), 'Other')


def stats(path, games, seed):
    name, header, cards = decklist.parse(path)
    cmdrs = decklist.commanders(path)
    data = scryfall.collection(cards)
    missing = [n for n in cards if n not in data]
    cards = Counter({n: q for n, q in cards.items() if n in data})
    names = list(cards)
    total = sum(cards.values())
    cmd_deck = bool(cmdrs)
    targets = {**{r: t for r, (_, t) in ROLES.items() if t}, **(TARGETS if cmd_deck else TARGETS_60)}
    roles = role_hits(names)
    in_deck = lambda n: n not in cmdrs
    print(f'=== {name}: {total} cards{" (" + ", ".join(cmdrs) + ")" if cmdrs else ""} ===')
    if missing:
        print(f'!! not found on Scryfall: {", ".join(missing)}')

    def flag(count, key):
        lo, hi = targets.get(key, (None, None))
        if lo is None:
            return ''
        return f'  [target {lo}-{hi}: ' + ('LOW' if count < lo else 'HIGH' if count > hi else 'ok') + ']'

    print('\n-- Roles (Scryfall oracle tags; commander excluded) --')
    for r in SHOW:
        cs = sorted(n for n in roles[r] if in_deck(n))
        print(f'{r:13} {len(cs):2}{flag(len(cs), r)}  {", ".join(cs) or "-"}')
    ints = {n for r in ('removal', 'counterspell') for n in roles[r] if in_deck(n)}
    print(f'{"removal+counters":13} {len(ints):2}{flag(len(ints), "removal+counters")}')

    # Mana
    lands = [n for n in names if is_land(data[n])]
    nlands = sum(cards[n] for n in lands)
    producers = {n: mana_producer(data[n]) for n in names if in_deck(n) and mana_producer(data[n])}
    colours = [c for c in 'WUBRG' if c in header] or [c for c in 'WUBRG' if any(c in data[n]['color_identity'] for n in cmdrs)]
    print('\n-- Mana --')
    print(f'lands {nlands}{flag(nlands, "lands")}, mana rocks/dorks {sum(cards[n] for n in producers)}')
    for col in colours:
        srcs = sum(cards[n] for n in lands if col in land_produces(data[n], colours))
        srcs += sum(cards[n] for n, p in producers.items() if col in p[0])
        worst = None  # (wants, pips, mv, card): the card that needs the most sources of this colour
        for n in names:
            p, mv = pips(data[n])[col], int(data[n].get('cmc', 0))
            if p and not is_land(data[n]):
                w = (sources_needed(p, mv) or 99, p, mv, n)
                worst = max(worst or w, w)
        if not worst:
            print(f'{col}: {srcs} sources, no {col} pips')
            continue
        want, p, mv, n = worst
        status = f' wants {want}: ' + ('SHORT' if srcs < want else 'ok') if cmd_deck else ''
        print(f'{col}: {srcs} sources; hardest {col * p} at MV {mv} ({n}){status}')
    if cmd_deck:
        print("(wants: Karsten's 2022 Commander table, ~90% on curve given enough lands;"
              ' fetch lands count for the colours they can find)')

    # Curve and types
    spells = [n for n in names if in_deck(n) and not is_land(data[n])]
    nsp = sum(cards[n] for n in spells)
    avg = sum(data[n].get('cmc', 0) * cards[n] for n in spells) / max(nsp, 1)
    types = Counter()
    for n in names:
        types[main_type(data[n])] += cards[n]
    curve = Counter()
    for n in spells:
        curve[min(int(data[n].get('cmc', 0)), 7)] += cards[n]
    print('\n-- Curve and types --')
    print(f'average MV of {nsp} nonland cards (excl. commander): {avg:.2f}')
    print('curve ' + '  '.join(f'{k}{"+" if k == 7 else ""}:{curve[k]}' for k in range(8)))
    print('types ' + ', '.join(f'{t} {types[t]}' for t in TYPES if types[t]))

    # Simulation
    lramp = roles['land-ramp']
    lib = []
    for n in names:
        if not in_deck(n):
            continue
        c, p = data[n], producers.get(n)
        mv, cost = int(c.get('cmc', 0)), dict(pips(c))
        for _ in range(cards[n]):
            if is_land(c):
                lib.append(Card('land', 0, 1, frozenset(land_produces(c, colours) or 'C'), {}))
            elif p:
                lib.append(Card('rock' if p[2] else 'dork', mv, p[1], frozenset(p[0]), cost))
            elif n in lramp and mv >= 2:
                lib.append(Card('lramp', mv, 1, frozenset(), cost))
            else:
                lib.append(Card('other', mv, 0, frozenset(), cost))
    cmdr = data.get(cmdrs[0]) if cmdrs else None
    commander = Cost(int(cmdr.get('cmc', 0)), dict(pips(cmdr))) if cmdr else None
    r = simulate(lib, commander, games, random.Random(seed))
    print(f'\n-- Goldfish ({games} games, seed {seed}) --')
    print('model: London mulligan to 4, first one free (keep 2-5 lands with 3+ lands or a castable 2-drop), draw every turn,'
          ' one land per turn, coloured pips paid, ramp cast cheapest-first; rocks work at once, dorks/land-ramp'
          ' next turn; the commander is removed on landing and recast with tax; nothing else is played.')
    line = f'keepable 7: {r["keep7"]:.0%}'
    if commander:
        by, again = r['cast_by'], r['recast_by']
        t1, t2, t3 = (min(max(t, 1), len(by)) for t in (commander.mv, commander.mv + 1, commander.mv + 3))
        cost = faces(cmdr)[0].get('mana_cost') or cmdr.get('mana_cost')
        line += (f' · commander {cost} castable by T{t1} {by[t1]:.0%}, T{t2} {by[t2]:.0%}'
                 f' · recast by T{t3} {again[t3]:.0%}')
    print(line)
    print('mulligans: ' + ', '.join(f'{k}: {r["mulls"][k] / games:.1%}' for k in sorted(r['mulls'])))
    print(f'lands drawn by turn 4 (in hand + played): {r["lands4"]:.2f}; all 4 land drops by turn 4: {r["drops4"]:.1%}')
    nramp = sum(1 for c in lib if c.kind in ('rock', 'dork', 'lramp'))
    print(f'ramp piece cast by turn 2: {r["ramp2"]:.1%}  ({nramp} ramp cards modelled)')
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--games', type=int, default=10000)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    for p in a.decks:
        stats(p, a.games, a.seed)


if __name__ == '__main__':
    main()
