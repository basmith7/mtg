#!/usr/bin/env python3
"""Pull Archidekt decks into local decklists (the gitignored working copy; Archidekt is canonical).

    scripts/pull.py https://archidekt.com/decks/27632721     # or a deck id
    scripts/pull.py 27632721 -o decks/commander/q.txt
    scripts/pull.py --folder <id>                            # every deck in a folder
    scripts/pull.py                                          # every deck in ARCHIDEKT_DECKS_FOLDER

Writes the list and its primer as a '.md' beside it, overwriting both. Without -o a deck goes to the
local file whose '# source:' line names it, else to decks/commander/<name>.txt for Commander decks and
decks/<name>.txt otherwise. The '# updated:' line records the site version, for push.py. Primer formatting the
markdown can't hold is reported and dropped (the text is kept).
"""
import argparse
import glob
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, config, decklist, scryfall

DECKS = os.path.join(os.path.dirname(__file__), '..', 'decks')


def local_path(deck_id, name, commander):
    for f in glob.glob(os.path.join(DECKS, '**', '*.txt'), recursive=True):
        if archidekt.deck_id_of(decklist.meta(f, 'source') or '') == deck_id:
            return f
    slug = re.sub(r'[^a-z0-9]+', '_', name.split(' – ')[0].lower()).strip('_')
    return os.path.join(DECKS, 'commander' if commander else '', slug + '.txt')


def pull(deck_id, path=None):
    d = archidekt.deck(deck_id)
    e = archidekt.export(d)
    commander = bool(e['commanders'])
    path = path or local_path(deck_id, e['name'], commander)
    colors = scryfall.color_identity(e['commanders'] or e['cards'])
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        f.write(decklist.render(e['name'], colors, e['commanders'], e['cards'],
                                archidekt.url(deck_id), d['updatedAt']))
    md = os.path.splitext(path)[0] + '.md'
    if e['primer']:
        with open(md, 'w') as f:
            f.write(e['primer'] + '\n')
    elif os.path.exists(md):
        os.remove(md)
    note = f"  (primer formatting dropped: {', '.join(e['dropped'])})" if e['dropped'] else ''
    print(f"{os.path.relpath(path)}  {e['name']}  {sum(e['cards'].values())} cards{note}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('decks', nargs='*', help='deck ids or Archidekt URLs')
    ap.add_argument('-o', '--out', help='file to write (one deck only)')
    ap.add_argument('--folder', type=int, action='append', default=[], help='pull every deck in this folder')
    a = ap.parse_args()
    ids = [archidekt.deck_id_of(x) for x in a.decks]
    if None in ids:
        sys.exit(f'pull: not a deck id or Archidekt URL: {a.decks[ids.index(None)]}')
    if not ids and not a.folder:
        a.folder = [int(config.get('ARCHIDEKT_DECKS_FOLDER'))]
    for folder in a.folder:
        ids += [d['id'] for d in archidekt.folder(folder)['decks']]
    if a.out and len(ids) != 1:
        ap.error('-o takes exactly one deck')
    for i, deck_id in enumerate(ids):
        if i:
            time.sleep(1)  # Archidekt rate-limits quickly
        pull(deck_id, a.out)


if __name__ == '__main__':
    main()
