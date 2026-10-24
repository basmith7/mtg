#!/usr/bin/env python3
"""EDHREC card recommendations for a commander, optionally compared with one of your decks.

    scripts/edhrec_recs.py "Ruric Thar, the Unbowed"
    scripts/edhrec_recs.py "Ruric Thar, the Unbowed" --theme burn --top 10
    scripts/edhrec_recs.py "Ruric Thar, the Unbowed" --deck decks/commander/foo.txt --min-inclusion 20
    scripts/edhrec_recs.py "Ruric Thar, the Unbowed" --themes     # just list themes
    scripts/edhrec_recs.py "Ruric Thar, the Unbowed" --gems [--deck decks/commander/foo.txt]

--gems: hidden gems, cards few decks play (under --gem-max %) that fit this commander unusually well,
ranked by EDHREC lift (how much likelier the card is here than in other decks of these colours).
With --deck it leaves out cards the deck already has.

With --deck: shows deck cards EDHREC lists (in deck), the top cards you're missing, and deck cards
EDHREC plays rarely (cut candidates; under --cut-below % inclusion, or missing from EDHREC's list, which is capped per category).
"""
import argparse
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import decklist, edhrec, scores

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('commander')
ap.add_argument('--theme')
ap.add_argument('--budget', choices=['budget', 'expensive'])
ap.add_argument('--deck')
ap.add_argument('--min-inclusion', type=float, default=10, help='ignore recs below this %% (default 10)')
ap.add_argument('--top', type=int, default=15, help='cards per category (default 15)')
ap.add_argument('--cut-below', type=float, default=5, help='with --deck: cut-candidate threshold %% (default 5)')
ap.add_argument('--gems', action='store_true', help='list hidden gems (low inclusion, high lift) and exit')
ap.add_argument('--gem-max', type=float, default=15, help='with --gems: inclusion cap %% (default 15)')
ap.add_argument('--gem-min-decks', type=int, default=20, help='with --gems: at least this many decks (default 20)')
ap.add_argument('--themes', action='store_true', help='list available themes and exit')
args = ap.parse_args()

data = edhrec.commander(args.commander, args.theme, args.budget)
if args.themes:
    for t in edhrec.themes(args.commander):
        print(f"{t['slug']:<24} {t['count']:>5} decks")
    sys.exit()

print(f"{data['name']}{' / ' + args.theme if args.theme else ''}: {data['num_decks']} decks")
print('Themes: ' + ', '.join(f"{t['slug']} ({t['count']})" for t in edhrec.themes(args.commander)[:8]))


def line(c, mark=''):
    return f"  {c['inclusion']:5.1f}%  syn {c['synergy']*100:+4.0f}%  {c['name']}{mark}"


def show(title, cards):
    by = defaultdict(list)
    for c in cards:
        by[c['section']].append(c)
    print(f'\n== {title} ==')
    for sec, cs in by.items():
        print(f'-- {sec}')
        for c in sorted(cs, key=lambda c: -c['inclusion'])[:args.top]:
            print(line(c))


basics = decklist.BASICS | {'Snow-Covered ' + b for b in decklist.BASICS}
if args.gems:
    exclude = set(basics)
    if args.deck:
        exclude |= set(decklist.parse(args.deck)[2])
    found = scores.gems(data['cards'], args.gem_max, args.gem_min_decks, exclude)
    print(f'\n== Hidden gems (inclusion under {args.gem_max:g}%, by lift) ==')
    for c in found[:args.top]:
        print(f"  lift {c['lift']:4.1f}  inc {c['inclusion']:4.1f}%  trend {c['trend_zscore']:+4.1f}  {c['name']}")
    if not found:
        print('  none')
    sys.exit()

recs = [c for c in data['cards'] if c['inclusion'] >= args.min_inclusion and c['name'] not in basics]
if not args.deck:
    show('Recommended', recs)
    sys.exit()

_, _, deck = decklist.parse(args.deck)
have = {n.lower() for n in deck} | {n.split('//')[0].strip().lower() for n in deck}
known = {}
for c in data['cards']:
    known.setdefault(c['name'].lower(), c)
inn = lambda c: c['name'].lower() in have
show('In deck (EDHREC lists these)', [c for c in recs if inn(c)])
show("Top cards you're missing", [c for c in recs if not inn(c)])

print(f'\n== Cut candidates (under {args.cut_below:g}% inclusion, or not on the EDHREC list) ==')
cuts = []
for n in deck:
    if n in basics or n in decklist.commanders(args.deck):
        continue
    c = known.get(n.lower()) or known.get(n.split('//')[0].strip().lower())
    if c is None:
        cuts.append((-1, n))
    elif c['inclusion'] < args.cut_below:
        cuts.append((c['inclusion'], n))
for inc, n in sorted(cuts):
    print(f'  {"not in list" if inc < 0 else f"{inc:5.1f}%":>10}  {n}')
