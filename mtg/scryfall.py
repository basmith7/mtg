"""Scryfall: card data. https://scryfall.com/docs/api"""
import time
import urllib.parse

from . import http

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


def oracle_text(card):
    """Oracle text, joining faces for split/double-faced cards."""
    return card.get('oracle_text') or ' // '.join(f.get('oracle_text', '') for f in card.get('card_faces', []))


def collection(names):
    """{name: card} for many card names, 75 per request. Missing names are left out.
    Split and double-faced cards are looked up by their front name, so 'Fire // Ice' works too."""
    names, out = list(names), {}
    for i in range(0, len(names), 75):
        r = http.request('POST', f'{BASE}/cards/collection', headers=HEADERS,
                         body={'identifiers': [{'name': n.split(' // ')[0]} for n in names[i:i + 75]]})
        for c in r['data']:
            out[c['name']] = c
            out.setdefault(c['name'].split(' // ')[0], c)
        time.sleep(0.1)
    return out


def ub_only(names):
    """The names whose every printing is Universes Beyond (e.g. Fallout cards, but not Sol Ring)."""
    names, has_normal = list(names), set()
    chunk, size = [], 0
    for n in names + [None]:  # Scryfall truncates queries around 1000 characters, so chunk by length
        term = f'!"{n.split(" // ")[0]}"' if n else ''
        if chunk and (n is None or size + len(term) > 800):
            q = '(' + ' or '.join(chunk) + ') not:universesbeyond'
            try:
                has_normal |= {name for c in search(q) for name in (c['name'], c['name'].split(' // ')[0])}
            except http.urllib.error.HTTPError as e:  # 404: none of this chunk has a normal printing
                if e.code != 404:
                    raise
            chunk, size = [], 0
        if n:
            chunk.append(term)
            size += len(term) + 4
    return [n for n in names if n not in has_normal and n.split(' // ')[0] not in has_normal]


def color_identity(names):
    """Combined colour identity of some cards, in WUBRG order (e.g. 'UR')."""
    data = collection(names)
    ident = set().union(*(data[c]['color_identity'] for c in names if c in data))
    return ''.join(c for c in 'WUBRG' if c in ident)
