#!/usr/bin/env python3
"""Play the player's own decks against each other with Forge's AI, offline, for a rough win share.

Usage: scripts/forge_sim.py a.txt b.txt [c.txt d.txt] [-n 10] [-c 600]

  -n  games to play (default 10)
  -c  seconds before Forge calls a game a draw (default 600)

Needs Forge unpacked under ~/.local/share/forge (or FORGE_HOME) and Java; see docs/forge.md.
Forge's AI plays combo and politics badly: this is a sparring read, never a power verdict.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mtg import decklist, forge  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('decks', nargs='+', help='2 to 4 Commander decklist .txt files')
    ap.add_argument('-n', type=int, default=10, help='games (default 10)')
    ap.add_argument('-c', type=int, default=600, help='seconds per game before a draw (default 600)')
    args = ap.parse_args()
    if not 2 <= len(args.decks) <= 4:
        ap.error('give 2 to 4 decks')

    os.makedirs(forge.DECK_DIR, exist_ok=True)
    split = forge.split_cards()
    dcks = []
    for path in args.decks:
        name, _, cards = decklist.parse(path)
        dck = os.path.join(forge.DECK_DIR, os.path.splitext(os.path.basename(path))[0] + '.dck')
        with open(dck, 'w') as f:
            f.write(forge.to_dck(name, decklist.commanders(path), cards, split))
        dcks.append(dck)

    print(f'Playing {args.n} games, {args.c}s each at most...', flush=True)
    result = forge.parse(forge.run(dcks, args.n, args.c))
    print(forge.LABEL)
    games = result['games'] or 1
    for deck, wins in result['wins'].most_common():
        print(f'  {deck}: {wins}/{result["games"]} ({wins / games:.0%})')
    print(f'  draws (timed out): {result["draws"]}/{result["games"]}')
    if result['games'] < args.n:
        print(f'!! only {result["games"]} of {args.n} games reported a result')
    for card in result['unsupported']:
        print(f'!! Forge could not load: {card}')


if __name__ == '__main__':
    main()
