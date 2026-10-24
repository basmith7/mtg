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
ignores colours and commander tax, so its on-curve odds run optimistic.
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
from mtg.goldfish import is_land, mana_producer, need, pips, simulate
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
        srcs = sum(cards[n] for n in lands if col in (data[n].get('produced_mana') or []))
        srcs += sum(cards[n] for n, p in producers.items() if col in p[0])
        worst = None  # (pips, mv, card): heaviest demand, ties broken by the lower MV
        for n in names:
            if is_land(data[n]):
                continue
            p, mv = pips(data[n])[col], int(data[n].get('cmc', 0))
            if p and (worst is None or (p, -mv) > (worst[0], -worst[1])):
                worst = (p, mv, n)
        if not worst:
            print(f'{col}: {srcs} sources, no {col} pips')
            continue
        want = need(worst[0], worst[1]) if cmd_deck else None
        status = '' if want is None else f' (want ~{want}: ' + ('SHORT' if srcs < want else 'ok') + ')'
        print(f'{col}: {srcs} sources; heaviest {col * worst[0]} at MV {worst[1]} ({worst[2]}){status}')
    print('(source thresholds are approximate Karsten-style Commander guidance; fetch/search lands are not counted)')

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
        for _ in range(cards[n]):
            if is_land(c):
                lib.append(('land', 0, 0))
            elif p:
                lib.append(('rock' if p[2] else 'dork', int(c.get('cmc', 0)), p[1]))
            elif n in lramp and int(c.get('cmc', 0)) >= 2:
                lib.append(('lramp', int(c.get('cmc', 0)), 1))
            else:
                lib.append(('other', int(c.get('cmc', 0)), 0))
    cmc = int(data[cmdrs[0]].get('cmc', 0)) if cmdrs and cmdrs[0] in data else None
    ct, lands4, drops4, ramp2, mulls = simulate(lib, cmc, games, random.Random(seed))
    print(f'\n-- Goldfish ({games} games, seed {seed}) --')
    print('simple model: 7 cards, London mulligan (keep 2-5 lands, keep anything at 4 cards), draw every turn,'
          ' one land per turn, colours ignored, ramp cast cheapest-first; rocks work at once, dorks/land-ramp'
          ' next turn; no tax, no other plays.')
    print(f'mulligans: ' + ', '.join(f'{k}: {mulls[k] / games:.1%}' for k in sorted(mulls)))
    if cmc is not None:
        by = ', '.join(f'T{t} {sum(x <= t for x in ct) / games:.0%}' for t in range(max(2, cmc - 3), cmc + 2))
        print(f'commander (MV {cmc}) castable by turn: {by}  (turns before T{cmc} need ramp)')
    print(f'lands drawn by turn 4 (in hand + played): {lands4:.2f}; all 4 land drops by turn 4: {drops4:.1%}')
    print(f'ramp piece cast by turn 2: {ramp2:.1%}  ({sum(1 for c in lib if c[0] in ("rock", "dork", "lramp"))} ramp cards modelled)')
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
