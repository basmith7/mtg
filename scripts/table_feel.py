#!/usr/bin/env python3
"""How a Commander deck will feel to the other three players, and a Rule 0 pitch.

    scripts/table_feel.py decks/commander/kardur.txt [more lists...]

salt: EDHREC salt scores (0-4, the community's "least fun to play against" vote) of the nonland cards.
table: the share of nonland cards that touch other players (theft, goad, stax, votes, "each opponent"...,
from oracle text), then counts per kind; MLD and extra turns always show. Rule 0: one sentence to say
before the game, with the official bracket. Reads Scryfall, Commander Spellbook and MTGJSON (cached).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import brackets, decklist, edhrec, patterns, scores, scryfall, spellbook

SHOW = [('theft', 'theft'), ('donate', 'donate'), ('goad', 'goad'), ('stax', 'stax'), ('vote', 'vote'),
        ('coin', 'coin'), ('monarch', 'monarch'), ('mld', 'MLD'), ('extra-turn', 'extra turns')]
ALWAYS = {'mld', 'extra-turn'}
NAME_UP_TO = 2  # list the cards when a kind has this few


def feel(path, max_gc):
    name, _, cards = decklist.parse(path)
    cmdrs = decklist.commanders(path)
    data = scryfall.collection(cards)
    spells = [n for n in cards if n in data and 'Land' not in data[n]['type_line'].split('//')[0]]
    classified = {n: patterns.classify(data[n]) for n in spells}
    est = spellbook.estimate_bracket(cmdrs, list(cards))
    fl = brackets.flags(classified, est and est['cards'])
    mv = brackets.mana_value(data)
    gcs = [n for n in cards if data.get(n, {}).get('game_changer')]
    official = brackets.official(gcs, fl,
                                 [{**c, 'fast': brackets.is_fast(c, mv)} for c in est['combos']] if est else [])
    if not est:
        official[1].append('combos not checked')
    house = brackets.house(gcs, fl, [], max_gc)  # fast combos already show in the official reasons
    salt = scores.salt_summary(spells, edhrec.salt(spells))
    share = scores.table_share(classified)

    print(name)
    if salt['avg'] is None:
        print('   salt: no scores')
    else:
        top = ', '.join(f'{n} {s:.1f}' for n, s in salt['top'])
        n = len(salt['over2'])
        print(f'   salt: average {salt["avg"]:.1f}; saltiest {top} ({n} card{"s" * (n != 1)} over {scores.SALTY})')
    kinds = []
    for tag, label in SHOW:
        names = fl[tag]
        if names or tag in ALWAYS:
            kinds.append(f'{label} {len(names)}' + (f' ({", ".join(names)})' if 0 < len(names) <= NAME_UP_TO else ''))
    print(f'   table: {share:.0%} of spells touch other players · ' + ' · '.join(kinds))
    print(f'   Rule 0: "{brackets.pitch(official, house, fl, salt, share)}"')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--max-gc', type=int, default=4, help='house Game Changer cap (as check_commander)')
    a = ap.parse_args()
    for p in a.decks:
        feel(p, a.max_gc)


if __name__ == '__main__':
    main()
