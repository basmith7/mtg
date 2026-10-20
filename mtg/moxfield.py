"""Moxfield, read-only (scripted login is blocked). See docs/apis.md."""
from . import http

BASE = 'https://api2.moxfield.com'


def deck(public_id):
    return http.get(f'{BASE}/v2/decks/all/{public_id}')


def public_decks(username):
    return http.get(f'{BASE}/v2/decks/search?authorUserNames={username}&pageSize=100')['data']


def board(deck_json, name='mainboard'):
    """[(card name, quantity, scryfall_id, type_line)] for one board of a deck."""
    return [(n, v['quantity'], v['card']['scryfall_id'], v['card'].get('type_line', ''))
            for n, v in (deck_json.get(name) or {}).items()]
