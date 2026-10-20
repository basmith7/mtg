#!/usr/bin/env python3
"""Push a local decklist to its Archidekt deck.

    scripts/sync_deck.py decks/commander/foo.txt [--deck ID|URL] [--primer foo.md | --no-primer]
                         [--dry-run] [--no-rename] [--force]

The deck defaults to the file's '# source:' Archidekt URL (pull_deck.py and upload_decks.py write it).
The primer defaults to a 'foo.md' beside 'foo.txt' and is written only if it differs from the site's.
Maybeboard/Sideboard cards on the site are left alone; existing cards keep their categories. The deck
JSON is backed up to ~/.cache/mtg-backups/ before any write.

Refuses (unless --force) if the deck changed on the site since it was last pulled or pushed, or if a
changed primer would drop site formatting markdown can't hold.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, decklist


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('decklist')
    ap.add_argument('--deck', help="deck id or Archidekt URL (default: the file's # source: line)")
    ap.add_argument('--primer')
    ap.add_argument('--no-primer', action='store_true', help="don't touch the deck's primer")
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-rename', action='store_true')
    ap.add_argument('--force', action='store_true', help='overwrite newer site edits and site-only formatting')
    a = ap.parse_args()
    deck_id = archidekt.deck_id(a.deck or decklist.source(a.decklist) or '')
    if not deck_id:
        sys.exit(f'sync_deck: {a.decklist} has no Archidekt # source: line; pass --deck')
    md = os.path.splitext(a.decklist)[0] + '.md'
    primer = None if a.no_primer else a.primer or (md if os.path.exists(md) else None)
    try:
        s = archidekt.sync(deck_id, a.decklist, primer, a.dry_run, not a.no_rename, a.force)
    except archidekt.Refused as e:
        sys.exit(f'sync_deck: refused, nothing written: {e}')
    for k in ('removed', 'added', 'changed'):
        print(f'{k} ({len(s[k])}):', *(f'\n  {x}' for x in s[k]))
    if s['renamed']:
        print('rename ->', s['renamed'])
    print('primer:', 'update' if s['primer'] else 'untouched')
    if a.dry_run:
        if s['stale']:
            print('warning: the deck changed on the site since it was last pulled or pushed; pull first')
        if s['primer_loses']:
            print('warning: the new primer would drop site formatting:', ', '.join(s['primer_loses']))
        print('dry run, nothing written')
    else:
        print(f"match: {'yes' if s['match'] else 'NO'}")
    sys.exit(0 if a.dry_run or s['match'] else 1)


if __name__ == '__main__':
    main()
