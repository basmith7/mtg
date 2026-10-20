#!/usr/bin/env python3
"""Check local decklists against Archidekt, card for card (read-only).

    scripts/verify_decks.py                         # every decks/**/*.txt
    scripts/verify_decks.py decks/ravnica/core/*.txt

A file matches its site deck by the '# source:' Archidekt URL, else by its '# Name' header. Prints
OK, MISSING (no site deck), AMBIGUOUS (several site decks share the name) or DIFFERS with details, and
the primer state. Exits 1 unless every deck is OK.
"""
import argparse
import glob
import os
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, decklist

DECKS = os.path.join(os.path.dirname(__file__), '..', 'decks')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('paths', nargs='*')
    a = ap.parse_args()
    paths = a.paths or sorted(glob.glob(os.path.join(DECKS, '**', '*.txt'), recursive=True))
    by_name = defaultdict(list)
    for d in archidekt.my_decks():
        by_name[d['name']].append(d['id'])
    bad = 0
    for path in paths:
        name = decklist.parse(path)[0]
        ids = [archidekt.deck_id(decklist.source(path) or '')] if archidekt.deck_id(decklist.source(path) or '') \
            else by_name.get(name, [])
        label = os.path.relpath(path)
        if len(ids) != 1:
            bad += 1
            print(f"{'MISSING' if not ids else 'AMBIGUOUS ' + str(ids)}  {label}  ({name})")
            continue
        time.sleep(1)  # Archidekt rate-limits quickly
        c = archidekt.compare(path, archidekt.deck(ids[0]))
        problems = [f'{k}: {", ".join(v)}' for k, v in c.items() if k.endswith(('site', 'diffs')) and v]
        if not c['commanders_match']:
            problems.append('commanders differ')
        bad += bool(problems)
        print(f"{'DIFFERS' if problems else 'OK'}  {label}  -> {archidekt.url(ids[0])}  primer: {c['primer']}")
        for p in problems:
            print('    ' + p)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
