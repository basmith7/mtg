#!/usr/bin/env python3
"""Push local decklists to Archidekt, creating the deck for a file that has none yet.

    scripts/push.py decks/commander/foo.txt [more.txt ...] [--dry-run] [--no-primer] [--force] [--folder ID]
    scripts/push.py --dry-run decks/**/*.txt        # what differs between the working copy and the site

A file's deck is its '# source:' line (pull.py writes it). A file without one becomes a new deck in
--folder (default ARCHIDEKT_DECKS_FOLDER), unless a deck of that name is already on the account: then
pull that deck instead. The '.md' beside a list is its primer, written only if it differs from the
site's. Maybeboard/Sideboard cards on the site are left alone; existing cards keep their categories.
Each deck's JSON is backed up to ~/.cache/mtg/backups/ before any write.

Refuses (unless --force) if the deck changed on the site since the file's '# updated:' version, or if a
changed primer would drop site formatting markdown can't hold. Exits 1 if any deck failed.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, config, decklist


def create(path, folder, dry_run):
    """Create the deck for a file with no '# source:' line and link the file to it. False if refused."""
    name, _, cards = decklist.parse(path)
    taken = [d['id'] for d in archidekt.my_decks() if d['name'] == name]
    if taken:
        print(f'{path}: "{name}" is already on Archidekt ({archidekt.url(taken[0])}); pull it instead')
        return False
    archidekt.resolve(cards)  # an unknown card fails here, before the deck exists
    if dry_run:
        print(f'{path}: would create "{name}" ({sum(cards.values())} cards)')
        return False
    cmdrs = decklist.commanders(path)
    deck_id = archidekt.create_deck(name, 'commander' if cmdrs else 'custom', folder)
    decklist.set_meta(path, 'source', archidekt.url(deck_id))
    decklist.set_meta(path, 'updated', archidekt.deck(deck_id)['updatedAt'])
    print(f'{path}: created {archidekt.url(deck_id)}')
    return True


def push(path, a):
    if not decklist.meta(path, 'source') and not create(path, a.folder, a.dry_run):
        return a.dry_run
    s = archidekt.sync(path, not a.no_primer, a.dry_run, a.force)
    changes = [f'  {k}: {x}' for k in ('removed', 'added', 'changed') for x in s[k]]
    changes += [f"  rename -> {s['renamed']}"] * bool(s['renamed']) + ['  primer: update'] * s['primer']
    if a.dry_run:
        changes += ['  warning: changed on the site since this file was pulled; pull first'] * s['stale']
        changes += [f"  warning: the primer would drop {', '.join(s['primer_loses'])}"] * bool(s['primer_loses'])
        print(f"{'DIFFERS' if changes else 'same'}  {path}  {s['url']}", *changes, sep='\n')
        return True
    print(f"{path}  {s['url']}  match: {'yes' if s['match'] else 'NO'}", *changes, sep='\n')
    return s['match']


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('decklists', nargs='+')
    ap.add_argument('--dry-run', action='store_true', help='show what would change; write nothing')
    ap.add_argument('--no-primer', action='store_true', help="don't touch the deck's primer")
    ap.add_argument('--force', action='store_true', help='overwrite newer site edits and site-only formatting')
    ap.add_argument('--folder', type=int, help='folder for new decks (default: ARCHIDEKT_DECKS_FOLDER)')
    a = ap.parse_args()
    a.folder = a.folder or int(config.get('ARCHIDEKT_DECKS_FOLDER'))
    ok = True
    for i, path in enumerate(a.decklists):
        if i:
            time.sleep(1)  # Archidekt rate-limits quickly
        try:
            ok &= push(path, a)
        except (archidekt.Refused, KeyError) as e:
            ok = False
            print(f'{path}: refused, nothing written: {e}')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
