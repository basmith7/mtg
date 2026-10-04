"""Moxfield, read-only (scripted login is blocked). See docs/apis.md."""
import time

from . import http

BASE = 'https://api2.moxfield.com'
USERNAME = 'basmith7'
COLLECTION_ID = 'cujOu-wx10SVgh_nMlHdXg'  # shared by link; readable without login


def deck(public_id):
    return http.get(f'{BASE}/v2/decks/all/{public_id}')


def public_decks(username=USERNAME):
    return http.get(f'{BASE}/v2/decks/search?authorUserNames={username}&pageSize=100')['data']


def collection(collection_id=COLLECTION_ID):
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
