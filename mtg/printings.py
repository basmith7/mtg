"""Which printing of a card to put on Archidekt: the fanciest one that is still easy to read, never
Universes Beyond.

Brian's taste (2026-10-27), the default for every player: special frames, but not ones that bury the
rules text. Each Scryfall printing gets a
style rank (best first) or is blocked:
    extended art > borderless (showcase frame or dark title bar) or full art > etched > other showcase or
    dark title bar > retro (1993/1997 frame) > 2003 frame > the regular modern frame.
Blocked: Universes Beyond, Secret Lair, joke and digital sets, non-English, textless, the Future Sight
frame, and for non-lands plain borderless and full art (both put text over busy art; lands have no
text to read). Ties go to the newest printing.
"""
from . import scryfall
from .cards import front

UB_SETS = {'trc'}  # Universes Beyond sets Scryfall doesn't tag yet: Star Trek Commander (2026-10)
BLOCKED_SET_TYPES = {'funny', 'memorabilia', 'token', 'minigame', 'alchemy', 'treasure_chest'}
QUERY = 'lang:en -is:digital not:universesbeyond'
KEEP = 3  # candidates per card, best first, in case Archidekt lacks the top one


def rank(c):
    """Style rank of a Scryfall printing (0 best), or None if it's blocked."""
    if (c.get('lang') != 'en' or c.get('digital') or c.get('textless') or c.get('oversized')
            or 'universesbeyond' in (c.get('promo_types') or []) or c['set'] in UB_SETS
            or c.get('set_type') in BLOCKED_SET_TYPES or 'Secret Lair' in c.get('set_name', '')
            or c.get('frame') == 'future'):
        return None
    fx = set(c.get('frame_effects') or [])
    borderless = c.get('border_color') == 'borderless'
    if 'Land' not in c.get('type_line', ''):
        if borderless and not fx & {'showcase', 'inverted'}:
            return None
        if c.get('full_art') and not (borderless and 'inverted' in fx):
            return None
    if 'extendedart' in fx:
        return 0
    if borderless or c.get('full_art'):
        return 1
    if 'etched' in fx:
        return 2
    if fx & {'showcase', 'inverted'}:
        return 3
    return {'1993': 4, '1997': 4, '2003': 5}.get(c.get('frame'), 6)


def best(names):
    """{name: [Scryfall ids of its KEEP best printings, best first]}; names with none allowed are left out."""
    by_name = {}
    for c in scryfall.search_names(names, QUERY, unique='prints'):
        r = rank(c)
        if r is not None:
            by_name.setdefault(c['name'], []).append((r, c['released_at'], c['id']))
    out = {}
    for n in dict.fromkeys(names):
        # Exact name or front face: a search for one face also finds other cards with that back face.
        hits = by_name.get(n) or next((v for k, v in by_name.items() if front(k) == front(n)), None)
        if hits:
            hits = sorted(sorted(hits, key=lambda h: h[1], reverse=True), key=lambda h: h[0])  # newest within a rank
            out[n] = [i for _, _, i in hits[:KEEP]]
    return out
