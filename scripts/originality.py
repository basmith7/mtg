#!/usr/bin/env python3
"""How original is a Commander deck? Staple share, overlap with your other decks, synergy density,
and a few less-played cards that do a staple's job.

    scripts/originality.py decks/commander/zedruu.txt
    scripts/originality.py decks/commander/zedruu.txt --threshold 50 --swaps 5

staples: the share of the 99's nonland cards that EDHREC plays in --threshold %+ of the commander's decks.
closest own deck: the other list in the same folder sharing the most cards (basics don't count).
synergy density: the share of nonland card pairs where one card's text names a type, subtype, counter,
keyword or token the other is or makes; compare with the player's own decks printed alongside.
odd swaps: for the --swaps most-played staples with a role (ramp, draw, removal...), cards in colour
that do the same job but aren't in the deck or among this commander's staples.
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import decklist, edhrec, roles, scores, scryfall
from mtg.cards import is_land

# Calibrated 2026-10-24 on the player's decks (specs/deck-tools/slices/05-originality.md).
BANDS = 'Zedruu group hug 0.17, Ayula bears 0.21, Breya artifacts 0.59'

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('list')
ap.add_argument('--threshold', type=float, default=40, help='staple inclusion %% (default 40)')
ap.add_argument('--swaps', type=int, default=3, help='staples to suggest swaps for (default 3)')
args = ap.parse_args()

_, _, cards = decklist.parse(args.list)
cmdrs = decklist.commanders(args.list)
if not cmdrs:
    sys.exit(f'{args.list}: no "Commander:" line')
data = scryfall.collection(cards)
nonland = [n for n in cards if n not in cmdrs and n in data and not is_land(data[n])]
missing = [n for n in cards if n not in data]

recs = edhrec.commander(cmdrs[0])['cards']
share, staples = scores.staple_share(nonland, recs, args.threshold)

others = {}
for path in glob.glob(os.path.join(os.path.dirname(os.path.abspath(args.list)), '*.txt')):
    if os.path.abspath(path) != os.path.abspath(args.list):
        others[os.path.basename(path)] = set(decklist.parse(path)[2])
close = scores.overlap(cards, others)
closest = f'{close[0][0]}, {close[0][1]} shared (Jaccard {close[0][2]:.2f})' if close else 'none'

print(f'staples: {share:.0%} of the nonland 99 ({len(staples)} cards at {args.threshold:g}%+ inclusion)'
      f' · closest own deck: {closest}')
print(f'synergy density: {scores.density(nonland, data):.2f} (own decks: {BANDS})')

inc = {c['name']: c['inclusion'] for c in recs}
popular = {c['name'] for c in recs if c['inclusion'] >= args.threshold}
identity = ''.join(sorted(set().union(*(data[c]['color_identity'] for c in cmdrs if c in data)),
                          key='WUBRG'.index))
roles.role_hits(staples)  # one batched lookup; role_of below reads the cache
swaps, offered = [], set(cards) | popular
for s in sorted(staples, key=lambda s: -inc.get(s, 0)):
    if len(swaps) == args.swaps:
        break
    role = roles.role_of(s)
    if role:
        alts = roles.alternatives(s, identity, exclude=offered)
        offered |= set(alts)  # two ramp staples shouldn't get the same three swaps
        if alts:
            swaps.append(f"  {s} ({role}) -> {', '.join(a + '?' for a in alts)}")
print('odd swaps:' + ('\n' + '\n'.join(swaps) if swaps else ' none'))
if missing:
    print(f'(not found on Scryfall, left out: {", ".join(missing)})')
