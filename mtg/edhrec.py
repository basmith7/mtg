"""EDHREC client (undocumented json.edhrec.com endpoints; see docs/apis.md).

    from mtg import edhrec
    edhrec.commander('Ruric Thar, the Unbowed', theme='burn')['cards']   # flat list of recs
    edhrec.themes('Ruric Thar, the Unbowed')                            # [{'slug', 'name', 'count'}]
    edhrec.average_deck('Ruric Thar, the Unbowed')                      # {'Creature': [(name, qty)], ...}
"""
import gzip
import json
import os
import re
import time
import unicodedata
import urllib.request

from mtg import config, http

BASE = 'https://json.edhrec.com/pages'
CACHE = os.path.join(config.CACHE, 'edhrec')
TTL = 7 * 86400
DELAY = 1.0
_last = 0.0

# Highlight lists. EDHREC removes their cards from the type lists, so keep them, but only as a fallback section.
HIGHLIGHTS = {'New Cards', 'Top Cards', 'High Lift Cards'}


def slug(name):
    """'Ruric Thar, the Unbowed' -> 'ruric-thar-the-unbowed'. Split cards use the front face only."""
    name = name.split('//')[0]
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    name = name.replace("'", '').replace('’', '')
    return re.sub(r'[^a-z0-9]+', '-', name).strip('-')


def _fetch(path):
    """GET a page, cached on disk for TTL seconds, ~1 request/sec to EDHREC."""
    global _last
    f = os.path.join(CACHE, path.replace('/', '__') + '.json')
    if os.path.exists(f) and time.time() - os.path.getmtime(f) < TTL:
        return json.load(open(f))
    time.sleep(max(0, DELAY - (time.time() - _last)))
    try:
        data = http.get(f'{BASE}/{path}.json')
    finally:
        _last = time.time()
    if '_raw' in data:  # a 200 that wasn't JSON (e.g. an error page): don't cache it
        raise ValueError(f'EDHREC returned non-JSON for {path}')
    os.makedirs(CACHE, exist_ok=True)
    json.dump(data, open(f + '.tmp', 'w'))
    os.replace(f + '.tmp', f)
    return data


def _page(name, theme=None, budget=None):
    path = f'commanders/{slug(name)}'
    for part in (theme, budget):
        if part:
            path += '/' + slug(part)
    return _fetch(path)


def _cards(page):
    out = []
    lists = page['container']['json_dict']['cardlists']
    for lst in sorted(lists, key=lambda l: l['header'] in HIGHLIGHTS):   # type lists first
        for c in lst['cardviews']:
            if any(o['name'] == c['name'] for o in out):
                continue
            pot = c.get('potential_decks') or 0
            out.append({'name': c['name'], 'section': lst['header'], 'num_decks': c.get('num_decks', 0),
                        'potential_decks': pot, 'inclusion': 100 * c.get('num_decks', 0) / pot if pot else 0.0,
                        'synergy': c.get('synergy', 0.0), 'lift': c.get('lift', 0.0),
                        'trend_zscore': c.get('trend_zscore', 0.0)})
    return out


def commander(name, theme=None, budget=None):
    """Commander page. budget: 'budget' or 'expensive'. Returns dict with name, theme, num_decks,
    themes, similar, and cards (flat list: name, section, inclusion %, synergy, lift, trend_zscore, num_decks, potential_decks)."""
    page = _page(name, theme, budget)
    cards = _cards(page)
    return {'name': page['header'], 'theme': theme, 'num_decks': max((c['potential_decks'] for c in cards), default=0),
            'themes': _themes(page), 'similar': page.get('similar', []), 'cards': cards}


def _themes(page):
    return [{'slug': t['slug'], 'name': t['value'], 'count': t['count']} for t in page.get('tag_counts', [])]


def themes(name):
    """Themes with deck counts for a commander, most popular first."""
    return sorted(_themes(_page(name)), key=lambda t: -t['count'])


def average_deck(name):
    """EDHREC's average decklist: {'Creature': [(card, qty), ...], ...}, commander under 'Commander'."""
    deck = _fetch(f'average-decks/{slug(name)}')['deck']
    out = {k: [tuple(c) for c in v] for k, v in deck['cards'].items()}
    out['Commander'] = [tuple(c) for c in deck.get('commander_v2', [])]
    return out


# EDHREC's salt scores (0-4, from its yearly player vote), read from MTGJSON's AtomicCards, which carries
# them as `edhrecSaltiness` for every card: one 52 MB download a week instead of a page per card.
MTGJSON_ATOMIC = 'https://mtgjson.com/api/v5/AtomicCards.json.gz'
SALT_FILE = os.path.join(CACHE, 'salt.json')


def _salt_table():
    """{card name: salt} for every card, rebuilt from MTGJSON when older than TTL. Double-faced and split
    cards are stored under both the full 'A // B' name and the front face."""
    if os.path.exists(SALT_FILE) and time.time() - os.path.getmtime(SALT_FILE) < TTL:
        return json.load(open(SALT_FILE))
    req = urllib.request.Request(MTGJSON_ATOMIC, headers={'User-Agent': http.BROWSER_UA})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(gzip.decompress(resp.read()))['data']
    table = {}
    for name, faces in data.items():
        s = faces[0].get('edhrecSaltiness')
        if s is not None:
            table[name] = s
            table.setdefault(name.split(' // ')[0], s)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(table, open(SALT_FILE + '.tmp', 'w'))
    os.replace(SALT_FILE + '.tmp', SALT_FILE)
    return table


def salt(names):
    """{name: salt score} for the names EDHREC has a score for (basics and new cards may have none)."""
    table = _salt_table()
    return {n: table[n] for n in names if n in table}
