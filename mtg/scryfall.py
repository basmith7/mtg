"""Scryfall: card data and prices. https://scryfall.com/docs/api"""
import time
import urllib.parse

from . import http

BASE = 'https://api.scryfall.com'
HEADERS = {'User-Agent': 'brian-mtg-tools/1.0'}


def search(query, unique='cards', **params):
    """Yield every card matching a Scryfall search query (follows pagination)."""
    url = f'{BASE}/cards/search?' + urllib.parse.urlencode({'q': query, 'unique': unique, **params})
    while url:
        page = http.get(url, headers=HEADERS, backoff=2)
        yield from page['data']
        url = page.get('next_page')
        time.sleep(0.1)


def named(name):
    return http.get(f'{BASE}/cards/named?' + urllib.parse.urlencode({'exact': name}), headers=HEADERS)


def cheapest_usd(name):
    """Lowest paper USD price across all printings (nonfoil, else foil), or None."""
    best = None
    try:
        for p in search(f'!"{name}" game:paper', unique='prints', order='usd', dir='asc'):
            v = p['prices'].get('usd') or p['prices'].get('usd_foil')
            if v and (best is None or float(v) < best):
                best = float(v)
    except http.urllib.error.HTTPError:
        return None
    return best


def oracle_text(card):
    """Oracle text, joining faces for split/double-faced cards."""
    return card.get('oracle_text') or ' // '.join(f.get('oracle_text', '') for f in card.get('card_faces', []))


def set_pool(set_codes):
    """Every distinct non-token card printed in any of the given sets."""
    query = '(' + ' or '.join(f'e:{s}' for s in set_codes) + ') -t:token'
    return list(search(query, order='name'))


# Every Ravnica set and Ravnica-only product, as used for the guild decks.
RAVNICA_SETS = ['rav', 'gpt', 'dis', 'rtr', 'gtc', 'dgm', 'grn', 'rna', 'war', 'mkm', 'rvr', 'clu', 'gk1', 'gk2']


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
