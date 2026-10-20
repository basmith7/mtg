"""Moxfield, read-only (scripted login is blocked). See docs/apis.md."""
import time

from . import config, http

BASE = 'https://api2.moxfield.com'


def deck(public_id):
    return http.get(f'{BASE}/v2/decks/all/{public_id}')


def public_decks(username=None):
    username = username or config.get('MOXFIELD_USERNAME')
    return http.get(f'{BASE}/v2/decks/search?authorUserNames={username}&pageSize=100')['data']


def collection(collection_id=None):
    """A collection shared by link (readable without login); default MOXFIELD_COLLECTION_ID."""
    collection_id = collection_id or config.get('MOXFIELD_COLLECTION_ID')
    out, page = [], 1
    while True:
        r = http.get(f'{BASE}/v1/collections/search/{collection_id}?sortType=cardName&sortDirection=ascending'
                     f'&pageNumber={page}&pageSize=100')
        out += r['data']
        if page >= r['totalPages']:
            return out
        page += 1
        time.sleep(0.5)


def board(deck_json, name='mainboard'):
    """[(card name, quantity, scryfall_id, type_line)] for one board of a deck."""
    return [(n, v['quantity'], v['card']['scryfall_id'], v['card'].get('type_line', ''))
            for n, v in (deck_json.get(name) or {}).items()]
