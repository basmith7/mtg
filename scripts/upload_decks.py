#!/usr/bin/env python3
"""Upload decklists (with optional primers) to Brian's Archidekt.

    scripts/upload_decks.py --folder 1914718 --primers decks/ravnica/primers_core.py decks/ravnica/power/*.txt

--primers is a Python file defining PRIMERS = {deck file name: light-markdown text}.
Cards are filed under their card type (Creature, Instant, ...). Needs cache/pool.json for type lines
when cards aren't looked up from Scryfall (falls back to Scryfall per card).
"""
import argparse
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, decklist, quill, scryfall

POOL = os.path.join(os.path.dirname(__file__), '..', 'cache', 'pool.json')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--folder', type=int, required=True)
    ap.add_argument('--primers')
    ap.add_argument('--format', default='custom')
    a = ap.parse_args()

    primers = {}
    if a.primers:
        spec = importlib.util.spec_from_file_location('primers', a.primers)
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, os.path.dirname(os.path.abspath(a.primers)))
        spec.loader.exec_module(mod)
        primers = mod.PRIMERS
    types = {c['name']: c['type_line'] for c in json.load(open(POOL))} if os.path.exists(POOL) else {}

    def category(card):
        tl = types.get(card) or scryfall.named(card)['type_line']
        return next((t for t in archidekt.TYPES if t in tl.split('//')[0]), 'Other')

    for path in a.decks:
        name, _, cards = decklist.parse(path)
        did = archidekt.create_deck(name, a.format, a.folder)
        archidekt.add_cards(did, [(archidekt.card_id(c), q, category(c), False) for c, q in cards.items()])
        primer = primers.get(os.path.basename(path))
        if primer:
            archidekt.update(did, description=quill.to_delta(primer), hasPrimer=True)
        got = archidekt.deck(did)
        print(f'{did} {name}: {sum(c["quantity"] for c in got["cards"])} cards, primer={got["hasPrimer"]}  '
              f'https://archidekt.com/decks/{did}')


if __name__ == '__main__':
    main()
