"""Scryfall: card data. https://scryfall.com/docs/api"""
import time
import urllib.parse

from . import http
from .cards import front

BASE = 'https://api.scryfall.com'
HEADERS = {'User-Agent': 'mtg-tools (github.com/basmith7/mtg)'}


def search(query, unique='cards', **params):
    """Yield every card matching a Scryfall search query (follows pagination)."""
    url = f'{BASE}/cards/search?' + urllib.parse.urlencode({'q': query, 'unique': unique, **params})
    while url:
        page = http.get(url, headers=HEADERS, backoff=2)
        yield from page['data']
        url = page.get('next_page')
        time.sleep(0.1)


def collection(names):
    """{name: card} for many card names, 75 per request. Missing names are left out.
    Split and double-faced cards are looked up by their front name, so 'Fire // Ice' works too."""
    names, out = list(names), {}
    for i in range(0, len(names), 75):
        r = http.request('POST', f'{BASE}/cards/collection', headers=HEADERS,
                         body={'identifiers': [{'name': front(n)} for n in names[i:i + 75]]})
        for c in r['data']:
            out[c['name']] = c
            out.setdefault(front(c['name']), c)
        time.sleep(0.1)
    return out


def matching(names, query):
    """The names (in order) that the Scryfall query also matches, by full name or front face: one search
    per chunk of names ANDed with the query. Scryfall truncates queries around 1000 characters, so
    chunks stay under 800."""
    names, hit = list(names), set()
    chunk, size = [], 0
    for n in names + [None]:
        term = f'!"{front(n)}"' if n else ''
        if chunk and (n is None or size + len(term) > 800):
            try:
                hit |= {x for c in search(f'({" or ".join(chunk)}) ({query})') for x in (c['name'], front(c['name']))}
            except http.urllib.error.HTTPError as e:  # 404: nothing in this chunk matches
                if e.code != 404:
                    raise
            chunk, size = [], 0
        if n:
            chunk.append(term)
            size += len(term) + 4
    return [n for n in names if n in hit or front(n) in hit]


def ub_only(names):
    """The names whose every printing is Universes Beyond (e.g. Fallout cards, but not Sol Ring)."""
    names = list(names)
    normal = set(matching(names, 'not:universesbeyond'))
    return [n for n in names if n not in normal]


def color_identity(names):
    """Combined colour identity of some cards, in WUBRG order (e.g. 'UR')."""
    data = collection(names)
    ident = set().union(*(data[c]['color_identity'] for c in names if c in data))
    return ''.join(c for c in 'WUBRG' if c in ident)
