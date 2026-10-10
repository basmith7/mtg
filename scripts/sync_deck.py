#!/usr/bin/env python3
"""Sync an Archidekt deck to a local decklist.

    scripts/sync_deck.py 27270377 decks/commander/foo.txt [--primer foo.md | --no-primer] [--dry-run] [--no-rename]

The deck can be an id or an archidekt.com/decks/<id> URL. The primer defaults to a 'foo.md' beside
'foo.txt'. Maybeboard/Sideboard cards on the site are left alone; existing cards keep their categories.
The deck JSON is backed up to ~/.cache/mtg-backups/ before any write.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck', help='deck id or Archidekt URL')
    ap.add_argument('decklist')
    ap.add_argument('--primer')
    ap.add_argument('--no-primer', action='store_true', help="don't touch the deck's primer")
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-rename', action='store_true')
    a = ap.parse_args()
    deck_id = int(a.deck) if a.deck.isdigit() else int(re.search(r'/decks/(\d+)', a.deck).group(1))
    md = os.path.splitext(a.decklist)[0] + '.md'
    primer = None if a.no_primer else a.primer or (md if os.path.exists(md) else None)
    s = archidekt.sync(deck_id, a.decklist, primer, a.dry_run, not a.no_rename)
    for k in ('removed', 'added', 'changed'):
        print(f'{k} ({len(s[k])}):', *(f'\n  {x}' for x in s[k]))
    if s['renamed']:
        print('rename ->', s['renamed'])
    print('primer:', 'update' if s['primer'] else 'untouched')
    print('dry run, nothing written' if a.dry_run else f"match: {'yes' if s['match'] else 'NO'}")
    sys.exit(0 if a.dry_run or s['match'] else 1)


if __name__ == '__main__':
    main()
