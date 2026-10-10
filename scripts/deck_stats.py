#!/usr/bin/env python3
"""Numbers for a decklist: role counts, mana base, a goldfish simulation and the curve.

    scripts/deck_stats.py decks/commander/ruric_thar.txt
    scripts/deck_stats.py --games 20000 --seed 7 decks/commander/*.txt

Roles come from Scryfall oracle tags (`otag:`), one query per role restricted to the deck's cards;
answers are cached per card in cache/deck_stats_roles.json. Tags are crowd-sourced and a bit noisy,
so each role query also excludes lands and overlapping roles; read the card lists, not just counts.
Commander lists (a 'Commander:' line) are 99-card libraries; other lists are treated as 60-card.
"""
import argparse
import json
import os
import random
import re
import sys
import time
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT)
from mtg import decklist, http, scryfall

# Role -> (Scryfall query suffix, target (min, max) or None). Edit targets freely.
ROLES = {
    'ramp': ('otag:ramp -t:land -otag:removal', (8, 12)),
    'draw': ('otag:draw -t:land -otag:ramp', (8, 12)),
    'removal': ('otag:removal -otag:board-wipe -t:land', None),
    'counterspell': ('otag:counterspell -t:land', None),
    'board-wipe': ('otag:board-wipe -t:land', (1, 3)),
    'tutor': ('otag:tutor -otag:ramp -t:land', None),
    'protection': ('otag:protection -t:land', None),
    'recursion': ('otag:recursion -t:land', None),
    'land-ramp': ('otag:land-ramp -t:land', None),  # only feeds the simulation
}
TARGETS = {  # not per-tag
    'removal+counters': (8, 10),  # BRIEF.md
    'lands': (35, 37),            # Commander; 60-card decks get 22-26 instead
}
TARGETS_60 = {'lands': (22, 26), 'removal+counters': (6, 10)}
SHOW = ['ramp', 'draw', 'removal', 'counterspell', 'board-wipe', 'tutor', 'protection', 'recursion']

# Coloured sources wanted in a 99-card deck for {pips} of one colour on a card of MV {mv}.
# Approximate, from memory of Frank Karsten's Commander guidance (about 90% on curve); NOT verified
# against his article. Treat as a rough flag, not a verdict. Index: pips -> list for MV 1,2,3,4,5+.
KARSTEN_99 = {1: [19, 16, 14, 13, 12], 2: [99, 24, 21, 19, 17], 3: [99, 99, 28, 25, 22]}

CACHE = os.path.join(ROOT, 'cache', 'deck_stats_roles.json')
TYPES = ['Land', 'Creature', 'Planeswalker', 'Battle', 'Artifact', 'Enchantment', 'Instant', 'Sorcery']


def front(n):
    return n.split(' // ')[0]


def role_hits(names):
    """{role: set(names)} using the per-card cache; queries only uncached names."""
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    for role, (suffix, _) in ROLES.items():
        known = cache.setdefault(role, {})
        chunk, size = [], 0
        for n in [n for n in names if n not in known] + [None]:  # chunk by length: Scryfall truncates long queries
            term = f'!"{front(n)}"' if n else ''
            if chunk and (n is None or size + len(term) > 800):
                hit = set()
                try:
                    q = '(' + ' or '.join(f'!"{front(c)}"' for c in chunk) + ') ' + suffix
                    hit = {x for c in scryfall.search(q) for x in (c['name'], front(c['name']))}
                except http.urllib.error.HTTPError as e:  # 404: nothing in this chunk matches
                    if e.code != 404:
                        raise
                known.update({c: c in hit or front(c) in hit for c in chunk})
                os.makedirs(os.path.dirname(CACHE), exist_ok=True)
                json.dump(cache, open(CACHE, 'w'))  # save as we go so a rate-limit crash can resume
                time.sleep(0.3)
                chunk, size = [], 0
            if n:
                chunk.append(n)
                size += len(term) + 4
    return {r: {n for n in names if cache[r].get(n)} for r in ROLES}


def faces(c):
    return c.get('card_faces') or [c]


def is_land(c):
    return 'Land' in c['type_line'].split('//')[0]


def mana_producer(c):
    """Nonland artifact/creature that taps for mana: returns (colours, amount, immediate) or None."""
    f = faces(c)[0]
    tl, txt = f.get('type_line', c['type_line']), f.get('oracle_text', '')
    if is_land(c) or not c.get('produced_mana') or not re.search(r'\bAdd\b', txt):
        return None
    if 'Artifact' not in tl and 'Creature' not in tl:
        return None
    amount = 2 if re.search(r'Add \{[WUBRGC]\}\{[WUBRGC]\}', txt) else 1
    return set(c['produced_mana']), amount, 'Artifact' in tl and 'Creature' not in tl


def pips(c):
    cost = faces(c)[0].get('mana_cost') or c.get('mana_cost', '')
    return Counter(re.findall(r'\{([WUBRG])\}', cost))


def main_type(c):
    tl = c['type_line'].split('//')[0]
    return next((t for t in TYPES if t in tl), 'Other')


def need(p, mv):
    return KARSTEN_99[min(p, 3)][min(max(mv, 1), 5) - 1]


def simulate(deck, cmc, games, rng):
    """deck: list of (kind, cost, mana) for the 99-card library; kinds: land, rock, dork, lramp, other.
    Model: colours ignored (generic mana only); each turn play a land, then cast ramp cheapest first
    with the mana available. Rocks work the turn they land; dorks and land-ramp the turn after."""
    cast_turn, lands4, ramp2, t4_drops, mulls = [], 0, 0, 0, Counter()
    for _ in range(games):
        lib = deck[:]
        rng.shuffle(lib)
        n = 0
        while True:
            hand, rest = lib[:7], lib[7:]
            nl = sum(c[0] == 'land' for c in hand)
            if 2 <= nl <= 5 or n >= 3:
                break
            lib = lib[:]
            rng.shuffle(lib)
            n += 1
        for _ in range(n):  # London mulligan: bottom n cards, lands first if flooded, else priciest spells
            lands = [c for c in hand if c[0] == 'land']
            spells = [c for c in hand if c[0] != 'land']
            drop = lands[0] if len(lands) > 3 or not spells else max(spells, key=lambda c: c[1])
            hand.remove(drop)
            rest.append(drop)
        mulls[n] += 1
        battlefield_lands, online, pending, done, drops, ramp_cast = 0, 0, 0, None, 0, False
        for t in range(1, 9):
            online += pending
            pending = 0
            hand.append(rest.pop(0))
            if t == 4:
                lands4 += battlefield_lands + sum(c[0] == 'land' for c in hand)
            land = next((c for c in hand if c[0] == 'land'), None)
            if land:
                hand.remove(land)
                battlefield_lands += 1
                drops += t <= 4
            mana = battlefield_lands + online
            while True:
                if cmc is not None and done is None and mana >= cmc:
                    done = t
                    break
                opts = sorted((c for c in hand if c[0] in ('rock', 'dork', 'lramp') and c[1] <= mana), key=lambda c: c[1])
                if not opts:
                    break
                c = opts[0]
                hand.remove(c)
                mana -= c[1]
                if t <= 2:
                    ramp_cast = True
                if c[0] == 'rock':
                    online += c[2]
                    mana += c[2]
                else:
                    pending += c[2]
        t4_drops += drops == 4
        ramp2 += ramp_cast
        cast_turn.append(done or 99)
    return cast_turn, lands4 / games, t4_drops / games, ramp2 / games, mulls


def stats(path, games, seed):
    name, header, cards = decklist.parse(path)
    cmdrs = decklist.commanders(path)
    data = scryfall.collection(cards)
    missing = [n for n in cards if n not in data]
    cards = Counter({n: q for n, q in cards.items() if n in data})
    names = list(cards)
    total = sum(cards.values())
    cmd_deck = bool(cmdrs)
    targets = {**{r: t for r, (_, t) in ROLES.items() if t}, **(TARGETS if cmd_deck else TARGETS_60)}
    roles = role_hits(names)
    in_deck = lambda n: n not in cmdrs
    print(f'=== {name}: {total} cards{" (" + ", ".join(cmdrs) + ")" if cmdrs else ""} ===')
    if missing:
        print(f'!! not found on Scryfall: {", ".join(missing)}')

    def flag(count, key):
        lo, hi = targets.get(key, (None, None))
        if lo is None:
            return ''
        return f'  [target {lo}-{hi}: ' + ('LOW' if count < lo else 'HIGH' if count > hi else 'ok') + ']'

    print('\n-- Roles (Scryfall oracle tags; commander excluded) --')
    for r in SHOW:
        cs = sorted(n for n in roles[r] if in_deck(n))
        print(f'{r:13} {len(cs):2}{flag(len(cs), r)}  {", ".join(cs) or "-"}')
    ints = {n for r in ('removal', 'counterspell') for n in roles[r] if in_deck(n)}
    print(f'{"removal+counters":13} {len(ints):2}{flag(len(ints), "removal+counters")}')

    # Mana
    lands = [n for n in names if is_land(data[n])]
    nlands = sum(cards[n] for n in lands)
    producers = {n: mana_producer(data[n]) for n in names if in_deck(n) and mana_producer(data[n])}
    colours = [c for c in 'WUBRG' if c in header] or [c for c in 'WUBRG' if any(c in data[n]['color_identity'] for n in cmdrs)]
    print('\n-- Mana --')
    print(f'lands {nlands}{flag(nlands, "lands")}, mana rocks/dorks {sum(cards[n] for n in producers)}')
    for col in colours:
        srcs = sum(cards[n] for n in lands if col in (data[n].get('produced_mana') or []))
        srcs += sum(cards[n] for n, p in producers.items() if col in p[0])
        worst = None  # (pips, mv, card): heaviest demand, ties broken by the lower MV
        for n in names:
            if is_land(data[n]):
                continue
            p, mv = pips(data[n])[col], int(data[n].get('cmc', 0))
            if p and (worst is None or (p, -mv) > (worst[0], -worst[1])):
                worst = (p, mv, n)
        if not worst:
            print(f'{col}: {srcs} sources, no {col} pips')
            continue
        want = need(worst[0], worst[1]) if cmd_deck else None
        status = '' if want is None else f' (want ~{want}: ' + ('SHORT' if srcs < want else 'ok') + ')'
        print(f'{col}: {srcs} sources; heaviest {col * worst[0]} at MV {worst[1]} ({worst[2]}){status}')
    print('(source thresholds are approximate Karsten-style Commander guidance; fetch/search lands are not counted)')

    # Curve and types
    spells = [n for n in names if in_deck(n) and not is_land(data[n])]
    nsp = sum(cards[n] for n in spells)
    avg = sum(data[n].get('cmc', 0) * cards[n] for n in spells) / max(nsp, 1)
    types = Counter()
    for n in names:
        types[main_type(data[n])] += cards[n]
    curve = Counter()
    for n in spells:
        curve[min(int(data[n].get('cmc', 0)), 7)] += cards[n]
    print('\n-- Curve and types --')
    print(f'average MV of {nsp} nonland cards (excl. commander): {avg:.2f}')
    print('curve ' + '  '.join(f'{k}{"+" if k == 7 else ""}:{curve[k]}' for k in range(8)))
    print('types ' + ', '.join(f'{t} {types[t]}' for t in TYPES if types[t]))

    # Simulation
    lramp = roles['land-ramp']
    lib = []
    for n in names:
        if not in_deck(n):
            continue
        c, p = data[n], producers.get(n)
        for _ in range(cards[n]):
            if is_land(c):
                lib.append(('land', 0, 0))
            elif p:
                lib.append(('rock' if p[2] else 'dork', int(c.get('cmc', 0)), p[1]))
            elif n in lramp and int(c.get('cmc', 0)) >= 2:
                lib.append(('lramp', int(c.get('cmc', 0)), 1))
            else:
                lib.append(('other', int(c.get('cmc', 0)), 0))
    cmc = int(data[cmdrs[0]].get('cmc', 0)) if cmdrs and cmdrs[0] in data else None
    ct, lands4, drops4, ramp2, mulls = simulate(lib, cmc, games, random.Random(seed))
    print(f'\n-- Goldfish ({games} games, seed {seed}) --')
    print('simple model: 7 cards, London mulligan (keep 2-5 lands, keep anything at 4 cards), draw every turn,'
          ' one land per turn, colours ignored, ramp cast cheapest-first; rocks work at once, dorks/land-ramp'
          ' next turn; no tax, no other plays.')
    print(f'mulligans: ' + ', '.join(f'{k}: {mulls[k] / games:.1%}' for k in sorted(mulls)))
    if cmc is not None:
        by = ', '.join(f'T{t} {sum(x <= t for x in ct) / games:.0%}' for t in range(max(2, cmc - 3), cmc + 2))
        print(f'commander (MV {cmc}) castable by turn: {by}  (turns before T{cmc} need ramp)')
    print(f'lands drawn by turn 4 (in hand + played): {lands4:.2f}; all 4 land drops by turn 4: {drops4:.1%}')
    print(f'ramp piece cast by turn 2: {ramp2:.1%}  ({sum(1 for c in lib if c[0] in ("rock", "dork", "lramp"))} ramp cards modelled)')
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--games', type=int, default=10000)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    for p in a.decks:
        stats(p, a.games, a.seed)


if __name__ == '__main__':
    main()
