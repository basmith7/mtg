"""Card roles (ramp, draw, removal...) from Scryfall oracle tags (`otag:`), cached per card.

    from mtg import roles
    roles.role_hits(names)   # {'ramp': {...}, 'draw': {...}, ...}

Tags are crowd-sourced and a bit noisy, so each role query also excludes lands and overlapping roles.
Answers are cached per card in ~/.cache/mtg/deck_stats_roles.json.
"""
import json
import os
import time

from mtg import config, http, scryfall

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
    'removal+counters': (8, 10),  # RULES.md
    'lands': (35, 37),            # Commander; 60-card decks get 22-26 instead
}
TARGETS_60 = {'lands': (22, 26), 'removal+counters': (6, 10)}
SHOW = ['ramp', 'draw', 'removal', 'counterspell', 'board-wipe', 'tutor', 'protection', 'recursion']

CACHE = os.path.join(config.CACHE, 'deck_stats_roles.json')


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
