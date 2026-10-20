#!/usr/bin/env python3
"""Upload decklists (with optional primers) to your Archidekt account.

    scripts/upload_decks.py decks/commander/foo.txt            # into ARCHIDEKT_DECKS_FOLDER
    scripts/upload_decks.py --folder <id> decks/ravnica/core/*.txt

A 'deck.md' beside 'deck.txt' is that deck's primer. Each file gets a '# source:' line linking it to
its new deck, for sync_deck.py. A file whose deck name already exists on the account is skipped, so
re-running is safe. Commander lists ('Commander:' lines, see mtg/decklist.py) file their commanders
under Commander. Cards are filed under their card type (Creature, Instant, ...). Needs cache/pool.json for type lines
when cards aren't looked up from Scryfall (falls back to Scryfall per card).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, config, decklist, quill


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--folder', type=int, help='Archidekt folder id (default: ARCHIDEKT_DECKS_FOLDER)')
    ap.add_argument('--format', help='default: commander for lists with a Commander: line, else custom')
    a = ap.parse_args()
    a.folder = a.folder or int(config.get('ARCHIDEKT_DECKS_FOLDER'))

    existing = {d['name']: d['id'] for d in archidekt.my_decks()}
    for path in a.decks:
        name, _, cards = decklist.parse(path)
        if name in existing:
            print(f'skip {name}: already on Archidekt  {archidekt.url(existing[name])}')
            continue
        cmdrs = decklist.commanders(path)
        # Resolve every card first so a bad name fails before an empty deck is created.
        entries = [(archidekt.card_id(c), q, 'Commander' if c in cmdrs else archidekt.category(c), False)
                   for c, q in cards.items()]
        did = archidekt.create_deck(name, a.format or ('commander' if cmdrs else 'custom'), a.folder)
        archidekt.add_cards(did, entries)
        md = os.path.splitext(path)[0] + '.md'
        primer = open(md).read() if os.path.exists(md) else None
        if primer:
            archidekt.update(did, description=quill.to_delta(primer), hasPrimer=True)
        got = archidekt.deck(did)
        archidekt.mark_seen(got)
        if not decklist.source(path):  # link the file to its new deck for sync_deck.py
            head, *rest = open(path).read().split('\n', 1)
            with open(path, 'w') as f:
                f.write('\n'.join([head, f'# source: {archidekt.url(did)}', *rest]))
        print(f'{did} {name}: {sum(c["quantity"] for c in got["cards"])} cards, primer={got["hasPrimer"]}  '
              f'{archidekt.url(did)}')


if __name__ == '__main__':
    main()
