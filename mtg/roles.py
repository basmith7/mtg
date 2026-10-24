"""Card roles (ramp, draw, removal...) from Scryfall oracle tags (`otag:`), cached per card.

    from mtg import roles
    roles.role_hits(names)   # {'ramp': {...}, 'draw': {...}, ...}

Tags are crowd-sourced and a bit noisy, so each role query also excludes lands and overlapping roles.
Answers are cached per card in ~/.cache/mtg/deck_stats_roles.json.
"""
import json
import os

from mtg import config, http, scryfall
from mtg.cards import front

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


def role_hits(names):
    """{role: set(names)} using the per-card cache; queries only uncached names."""
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    for role, (suffix, _) in ROLES.items():
        known = cache.setdefault(role, {})
        todo = [n for n in names if n not in known]
        if todo:
            hit = set(scryfall.matching(todo, suffix))
            known.update({n: n in hit for n in todo})
            os.makedirs(os.path.dirname(CACHE), exist_ok=True)
            json.dump(cache, open(CACHE, 'w'))  # save per role so a rate-limit crash can resume
    return {r: {n for n in names if cache[r].get(n)} for r in ROLES}


def role_of(name):
    """The card's first role in SHOW order (from the role_hits cache), or None."""
    hits = role_hits([name])
    return next((r for r in SHOW if name in hits[r]), None)


def alternatives(card, identity, n=3, exclude=()):
    """Up to n other Commander-legal cards in colour identity `identity` (e.g. 'WU') with the same role
    as `card`, most played first after leaving out `exclude` (the deck's cards and the commander's
    staples, so what's left is the less obvious pick), Game Changers and joke sets. [] if no role."""
    role = role_of(card)
    if role is None:
        return []
    skip = {x.lower() for x in exclude} | {card.lower()}
    q = f'{ROLES[role][0]} id<={identity or "C"} f:commander -is:gamechanger not:funny'
    out = []
    try:
        for c in scryfall.search(q, order='edhrec', dir='asc'):
            if c['name'].lower() not in skip and front(c['name']).lower() not in skip:
                out.append(c['name'])
                if len(out) == n:
                    break
    except http.urllib.error.HTTPError as e:  # 404: no card matches
        if e.code != 404:
            raise
    return out
