#!/usr/bin/env python3
"""Upload decklists (with optional primers) to Brian's Archidekt.

    scripts/upload_decks.py --folder 1914718 --primers decks/ravnica/primers_core.py decks/ravnica/power/*.txt

--primers is a Python file defining PRIMERS = {deck file name: light-markdown text}. Without it, a
'deck.md' beside 'deck.txt' is used as that deck's primer. Commander lists ('Commander:' lines, see
mtg/decklist.py) file their commanders under Commander.
Cards are filed under their card type (Creature, Instant, ...). Needs cache/pool.json for type lines
when cards aren't looked up from Scryfall (falls back to Scryfall per card).
"""
import argparse
import importlib.util
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, decklist, quill


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--folder', type=int, required=True)
    ap.add_argument('--primers')
    ap.add_argument('--format', help='default: commander for lists with a Commander: line, else custom')
    a = ap.parse_args()

    primers = {}
    if a.primers:
        spec = importlib.util.spec_from_file_location('primers', a.primers)
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, os.path.dirname(os.path.abspath(a.primers)))
        spec.loader.exec_module(mod)
        primers = mod.PRIMERS

    for path in a.decks:
        name, _, cards = decklist.parse(path)
        cmdrs = decklist.commanders(path)
        did = archidekt.create_deck(name, a.format or ('commander' if cmdrs else 'custom'), a.folder)
        archidekt.add_cards(did, [(archidekt.card_id(c), q, 'Commander' if c in cmdrs else archidekt.category(c), False)
                                  for c, q in cards.items()])
        md = os.path.splitext(path)[0] + '.md'
        primer = primers.get(os.path.basename(path)) or (open(md).read() if os.path.exists(md) else None)
        if primer:
            archidekt.update(did, description=quill.to_delta(primer), hasPrimer=True)
        got = archidekt.deck(did)
        print(f'{did} {name}: {sum(c["quantity"] for c in got["cards"])} cards, primer={got["hasPrimer"]}  '
              archidekt.url(did))


if __name__ == '__main__':
    main()
