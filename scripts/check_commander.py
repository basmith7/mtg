#!/usr/bin/env python3
"""Validate Commander decklists.

    scripts/check_commander.py decks/commander/*.txt
    scripts/check_commander.py --max-gc 4 --allow-ub decks/commander/wise_mothman.txt

A list needs a 'Commander: Card Name' line (see mtg/decklist.py). Checks: 100 cards, singleton
(basics and "any number" cards excepted), every card found and Commander-legal, colour identity
within the commanders', at most --max-gc Game Changers, and no Universes-Beyond-only cards unless
--allow-ub. Also prints the curve and land count. Exits 1 if any deck has problems.
"""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import decklist, scryfall


def check(path, max_gc, allow_ub):
    name, _, cards = decklist.parse(path)
    cmdrs = decklist.commanders(path)
    data = scryfall.collection(cards)
    problems = []
    if not cmdrs:
        problems.append('no "Commander:" line')
    identity = set()
    for c in cmdrs:
        if c not in cards:
            problems.append(f'commander not in list: {c}')
        if c in data:
            identity |= set(data[c]['color_identity'])
    total = sum(cards.values())
    if total != 100:
        problems.append(f'{total} cards')
    gcs, lands, curve = [], 0, Counter()
    for card, q in cards.items():
        c = data.get(card)
        if not c:
            problems.append(f'not found on Scryfall: {card}')
            continue
        if q > 1 and 'Basic' not in c['type_line'] and 'any number of cards named' not in scryfall.oracle_text(c):
            problems.append(f'{q} copies: {card}')
        if c['legalities'].get('commander') != 'legal':
            problems.append(f'not Commander-legal: {card}')
        if cmdrs and not set(c['color_identity']) <= identity:
            problems.append(f'off-colour: {card} ({"".join(c["color_identity"])})')
        if c.get('game_changer'):
            gcs.append(card)
        if 'Land' in c['type_line'].split('//')[0]:
            lands += q
        elif card not in cmdrs:
            curve[min(int(c.get('cmc', 0)), 7)] += q
    if len(gcs) > max_gc:
        problems.append(f'{len(gcs)} Game Changers (max {max_gc})')
    if not allow_ub:
        problems += [f'Universes Beyond: {c}' for c in scryfall.ub_only([n for n in cards if n in data]) if c not in cmdrs]
    print(f'{name}: {total} cards, {lands} lands, Game Changers {len(gcs)}: {", ".join(gcs) or "-"}')
    print('   curve ' + '  '.join(f'{k}{"+" if k == 7 else ""}:{curve[k]}' for k in range(8)))
    for p in problems:
        print(f'   !! {p}')
    return not problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--max-gc', type=int, default=4)
    ap.add_argument('--allow-ub', action='store_true')
    a = ap.parse_args()
    ok = [check(p, a.max_gc, a.allow_ub) for p in a.decks]
    sys.exit(0 if all(ok) else 1)


if __name__ == '__main__':
    main()
