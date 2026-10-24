#!/usr/bin/env python3
"""Validate Commander decklists.

    scripts/check_commander.py decks/commander/*.txt
    scripts/check_commander.py --max-gc 4 --allow-ub decks/commander/wise_mothman.txt

A list needs a 'Commander: Card Name' line (see mtg/decklist.py). Checks: 100 cards, singleton
(basics and "any number" cards excepted), every card found and Commander-legal, colour identity
within the commanders', at most --max-gc Game Changers, and no Universes-Beyond-only cards unless
--allow-ub. Also prints the curve and land count. Exits 1 if any deck has problems.

Then asks Commander Spellbook which combos the deck contains (network; --no-combos skips it).
Combos are fine if they're fun and late (house rule, RULES.md). A combo is FAST when its pieces total mana
value 6 or less, or Spellbook rates it Ruthless or Banned; a fast infinite combo is a problem (`!!`).
--near also lists combos missing one card. Primers should take their combo claims from this output.

--pool "<query>" checks a challenge deck (scripts/discover.py --challenge): every card but basic lands
must match the Scryfall query, e.g. --pool "atag:dragon f:commander".
"""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import brackets, decklist, scryfall, spellbook


def show_combos(cmdrs, cards, data, near):
    """Print Spellbook combos; return problem strings."""
    def mv(n):  # Spellbook sometimes names one face of a double-faced card
        c = data.get(n) or next((v for k, v in data.items() if n in k.split(' // ')), None)
        return c.get('cmc', 0) if c else None

    def total(c):
        t = brackets.total_mv(c, mv)
        return '?' if t is None else t

    def fast(c):
        return brackets.is_fast(c, mv)

    found = spellbook.find_combos(cmdrs, list(cards))
    if near:  # look up the missing pieces too, so near-miss combos get a real total
        missing = {n for c in found['almost'] for n in c['cards'] if mv(n) is None}
        data = {**data, **(scryfall.collection(missing) if missing else {})}
    problems = []

    def line(c, tag=''):
        print(f'   {tag}{" + ".join(c["cards"])} [{c["bracket"]}] total MV {total(c)}{" FAST" if fast(c) else ""}')
        print(f'      -> {"; ".join(c["results"])}')
        if c['prerequisites'] and not tag:
            print(f'      needs: {c["prerequisites"].replace(chr(10), " ")}')
        print(f'      {c["url"]}')

    print(f'   combos: {len(found["included"])} included, {len(found["almost"])} one card away')
    for c in found['included']:
        line(c)
        if fast(c) and any(r.lower().startswith('infinite') for r in c['results']):
            problems.append(f'fast infinite combo: {" + ".join(c["cards"])} ({c["url"]})')
    if near:
        print('   near (missing one card):')
        for c in found['almost']:
            line(c, f'+{c["missing"][0]}: ' if c['missing'] else '')
    return problems


def check(path, max_gc, allow_ub, combos=True, near=False):
    name, _, cards = decklist.parse(path)
    cmdrs = decklist.commanders(path)
    data = scryfall.collection(cards)
    problems = []
    if not cmdrs:
        problems.append('no "Commander:" line')
    identity = set()
    for c in cmdrs:
        if c not in cards:
            problems.append(f'commander not in list: {c}')
        if c in data:
            identity |= set(data[c]['color_identity'])
    total = sum(cards.values())
    if total != 100:
        problems.append(f'{total} cards')
    gcs, lands, curve = [], 0, Counter()
    for card, q in cards.items():
        c = data.get(card)
        if not c:
            problems.append(f'not found on Scryfall: {card}')
            continue
        if c['name'] != card:  # the site exports the full name, so a front-face name shows up as a change
            problems.append(f'use the full name: {card} -> {c["name"]}')
        if q > 1 and 'Basic' not in c['type_line'] and 'any number of cards named' not in scryfall.oracle_text(c):
            problems.append(f'{q} copies: {card}')
        if c['legalities'].get('commander') != 'legal':
            problems.append(f'not Commander-legal: {card}')
        if cmdrs and not set(c['color_identity']) <= identity:
            problems.append(f'off-colour: {card} ({"".join(c["color_identity"])})')
        if c.get('game_changer'):
            gcs.append(card)
        if 'Land' in c['type_line'].split('//')[0]:
            lands += q
        elif card not in cmdrs:
            curve[min(int(c.get('cmc', 0)), 7)] += q
    if len(gcs) > max_gc:
        problems.append(f'{len(gcs)} Game Changers (max {max_gc})')
    if not allow_ub:
        problems += [f'Universes Beyond: {c}' for c in scryfall.ub_only([n for n in cards if n in data]) if c not in cmdrs]
    print(f'{name}: {total} cards, {lands} lands, Game Changers {len(gcs)}: {", ".join(gcs) or "-"}')
    print('   curve ' + '  '.join(f'{k}{"+" if k == 7 else ""}:{curve[k]}' for k in range(8)))
    if combos:
        try:
            problems += show_combos(cmdrs, cards, data, near)
        except (OSError, KeyError, TypeError) as e:  # network down or an unexpected response
            print(f'   combos: Spellbook unavailable ({e})')
    for p in problems:
        print(f'   !! {p}')
    return not problems


def outside_pool(path, query):
    """Cards in the list (basic lands aside) that the Scryfall query doesn't match. Searches the
    query ANDed with the deck's names, in chunks short enough for Scryfall."""
    names = [n for n in decklist.parse(path)[2] if n not in decklist.BASICS]
    inside, chunk = set(), []
    for n in names + [None]:
        if chunk and (n is None or sum(map(len, chunk)) > 700):
            try:
                found = scryfall.search(f'({query}) (' + ' or '.join(chunk) + ')')
                inside |= {x for c in found for x in (c['name'], c['name'].split(' // ')[0])}
            except scryfall.http.urllib.error.HTTPError as e:  # 404: nothing in this chunk matches
                if e.code != 404:
                    raise
            chunk = []
        if n:
            chunk.append(f'!"{n.split(" // ")[0]}"')
    return [n for n in names if n not in inside and n.split(' // ')[0] not in inside]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--max-gc', type=int, default=4)
    ap.add_argument('--allow-ub', action='store_true')
    ap.add_argument('--near', action='store_true', help='also list combos missing one card')
    ap.add_argument('--no-combos', action='store_true', help='skip the Commander Spellbook lookup')
    ap.add_argument('--pool', help='challenge pool: a Scryfall query every card must match')
    a = ap.parse_args()
    ok = []
    for p in a.decks:
        ok.append(check(p, a.max_gc, a.allow_ub, not a.no_combos, a.near))
        if a.pool:
            out = outside_pool(p, a.pool)
            print(f'   pool ({a.pool}): {len(out)} cards outside')
            ok[-1] &= not out
            for n in out:
                print(f'   !! outside the pool: {n}')
    sys.exit(0 if all(ok) else 1)


if __name__ == '__main__':
    main()
