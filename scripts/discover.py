#!/usr/bin/env python3
"""Find underplayed commanders that match the player's taste, or roll a challenge deck.

    scripts/discover.py                              # mechanics picked from the player's "enjoys" bullets
    scripts/discover.py --mechanic goad --mechanic vote --colours BR
    scripts/discover.py --avoid friends.txt --counts # skip the names in a file ('-' reads stdin)
    scripts/discover.py --challenge --seed 3         # a challenge brief and the Scryfall query for its pool
    scripts/discover.py --challenge --kind art

Mechanics: control-swap, goad, vote, coin, monarch, each-player, chaos (queries in mtg/discovery.py).
Commanders are listed least played first by Scryfall's EDHREC rank. Commanders of the decks in --decks
(default decks/commander) are skipped, and so are --avoid names (one per line, '#' comments ignored).
--colours keeps commanders whose identity fits inside the colours. --counts adds EDHREC's deck count
for the first 15 (one EDHREC request each) and orders those by it. Check a challenge deck with
scripts/check_commander.py --pool "<query>".
"""
import argparse
import glob
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import config, decklist, discovery, edhrec, profile

ROOT = os.path.join(os.path.dirname(__file__), '..')


def read_names(path):
    if path == '-':
        lines = sys.stdin.readlines()
    else:
        with open(path) as f:
            lines = f.readlines()
    return {l.strip() for l in lines if l.strip() and not l.lstrip().startswith('#')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mechanic', action='append', choices=sorted(discovery.MECHANICS))
    ap.add_argument('--colours', help='colour identity to fit inside, e.g. BR')
    ap.add_argument('--avoid', action='append', default=[], help="file of commander names to skip, or '-' for stdin")
    ap.add_argument('--decks', default=os.path.join(ROOT, 'decks', 'commander'), help='skip commanders of the lists here')
    ap.add_argument('--counts', action='store_true', help='EDHREC deck counts for the first 15')
    ap.add_argument('--limit', type=int, default=25)
    ap.add_argument('--challenge', action='store_true')
    ap.add_argument('--kind', action='append', choices=discovery.KINDS, help='challenge kinds to roll from')
    ap.add_argument('--seed', type=int)
    a = ap.parse_args()

    exclude = set().union(*map(read_names, a.avoid)) if a.avoid else set()
    for path in glob.glob(os.path.join(a.decks, '*.txt')):
        exclude.update(decklist.commanders(path))

    if a.challenge:
        c = discovery.challenge(random.Random(a.seed), a.kind, exclude)
        print(c['text'])
        print(f'   pool: {c["query"]}')
        return

    mechanics = a.mechanic
    if not mechanics:
        player = config.get('MTG_PLAYER')
        mechanics = discovery.mechanics_for(profile.enjoys(player))
        if not mechanics:
            sys.exit(f"nothing in players/{player}.md's enjoys bullets matches a mechanic; pass --mechanic")
        print(f'from {player.capitalize()}\'s profile: {", ".join(mechanics)}')
    rows = discovery.candidates(mechanics, exclude, a.colours)[:a.limit]
    counts = {}
    if a.counts:  # edhrec_rank is the card's rank in all decks, so a commander's own deck count orders better
        for name, *_ in rows[:15]:
            try:
                counts[name] = edhrec.commander(name)['num_decks']
            except (OSError, ValueError, KeyError) as e:
                print(f'  EDHREC failed for {name}: {e}')
        rows[:15] = sorted(rows[:15], key=lambda r: counts.get(r[0], float('inf')))
    for name, ms, rank, ident in rows:
        decks = f'  {counts[name]} decks' if name in counts else ''
        print(f'  {",".join(ms):<14} rank {rank or "-":<6} {ident or "C":<5} {name}{decks}')


if __name__ == '__main__':
    main()
