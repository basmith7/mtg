#!/usr/bin/env python3
"""Download every card from a list of sets into cache/pool.json (for check_decks.py --pool).

    scripts/build_pool.py                 # all Ravnica sets
    scripts/build_pool.py dmu bro one     # any sets
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import scryfall

sets = sys.argv[1:] or scryfall.RAVNICA_SETS
cards = scryfall.set_pool(sets)
out = os.path.join(os.path.dirname(__file__), '..', 'cache', 'pool.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(cards, open(out, 'w'))
print(f'{len(cards)} cards from {len(sets)} sets -> {os.path.normpath(out)}')
