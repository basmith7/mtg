"""Archidekt client (private API; see docs/apis.md).

Logs in once via 1Password, caches the JWT in ~/.config/mtg/archidekt-session.json, and renews it
with the refresh token, so Brian only gets a 1Password prompt when the refresh token has expired too.
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse

from . import http

BASE = 'https://archidekt.com'
USERNAME = 'basmith7'
USER_ID = 309724
OP_ITEM = '727iygg5qogmtfsx7mfphyubbi'
SESSION = os.path.expanduser('~/.config/mtg/archidekt-session.json')
TYPES = ['Land', 'Creature', 'Planeswalker', 'Battle', 'Artifact', 'Enchantment', 'Instant', 'Sorcery']
FORMATS = {'standard': 1, 'modern': 2, 'commander': 3, 'legacy': 4, 'vintage': 5, 'pauper': 6, 'custom': 7,
           'pioneer': 15, 'historic': 16, 'brawl': 13, 'oathbreaker': 14, 'premodern': 22}


def _save(session):
    os.makedirs(os.path.dirname(SESSION), exist_ok=True)
    fd = os.open(SESSION, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(session, f)


def login():
    """Full login. Pipes the password from 1Password; never prints it."""
    pw = subprocess.run(['op', 'item', 'get', OP_ITEM, '--fields', 'password', '--reveal'],
                        capture_output=True, text=True, check=True).stdout.strip()
    r = http.request('POST', f'{BASE}/api/rest-auth/login/', {'username': USERNAME, 'password': pw})
    _save({'access': r['access_token'], 'refresh': r.get('refresh_token')})


def refresh():
    """Renew the access token without a password. Returns False if the refresh token is dead."""
    s = json.load(open(SESSION))
    try:
        r = http.request('POST', f'{BASE}/api/rest-auth/token/refresh/', {'refresh': s['refresh']})
    except urllib.error.HTTPError:
        return False
    s['access'] = r['access']
    s['refresh'] = r.get('refresh', s['refresh'])
    _save(s)
    return True


def call(method, path, body=None, auth=True):
    if auth and not os.path.exists(SESSION):
        login()
    for attempt in range(2):
        hdrs = {'Authorization': 'JWT ' + json.load(open(SESSION))['access']} if auth else {}
        try:
            return http.request(method, BASE + path, body, headers=hdrs)
        except urllib.error.HTTPError as e:
            if e.code != 401 or not auth or attempt:
                raise RuntimeError(f'{method} {path}: HTTP {e.code} {e.read()[:300]!r}') from None
            if not refresh():
                login()


# ---- reading -------------------------------------------------------------------------------

def deck(deck_id):
    return call('GET', f'/api/decks/{deck_id}/')


def folder_tree():
    return call('GET', '/api/decks/folderTree/')


def folder(folder_id):
    return call('GET', f'/api/decks/folders/{folder_id}/?pageSize=100')


def my_decks():
    out, page = [], 1
    while True:
        r = call('GET', f'/api/decks/v3/?ownerUsername={USERNAME}&pageSize=50&page={page}')
        out += r['results']
        if not r.get('next'):
            return out
        page += 1


def collection():
    out, page = [], 1
    while True:
        r = call('GET', f'/api/collection/{USER_ID}/v2/?game=1&page={page}&pageSize=100')
        out += r['results']
        if page >= r['totalPages']:
            return out
        page += 1
        time.sleep(0.6)


def search_tags(text):
    return call('GET', '/api/decks/tags/v2/?' + urllib.parse.urlencode({'q': text}), auth=False)


# ---- card ids ------------------------------------------------------------------------------

_ID_CACHE = os.path.join(os.path.dirname(__file__), '..', 'cache', 'archidekt_card_ids.json')
_SKIP_SETS = {'plst', 'sld', 'pmei', 'prm'}


def card_id(name):
    """Archidekt card id for a card name (cached; the lookup endpoint rate-limits hard)."""
    cache = json.load(open(_ID_CACHE)) if os.path.exists(_ID_CACHE) else {}
    if name in cache:
        return cache[name]
    res = call('GET', '/api/cards/v2/?exact=true&name=' + urllib.parse.quote(name), auth=False)['results']
    res = [c for c in res if c['oracleCard']['name'] == name] or res
    if not res:
        raise KeyError(f'Archidekt has no card named {name!r}')
    cache[name] = next((c for c in res if c['edition']['editioncode'] not in _SKIP_SETS), res[0])['id']
    os.makedirs(os.path.dirname(_ID_CACHE), exist_ok=True)
    json.dump(cache, open(_ID_CACHE, 'w'))
    time.sleep(1.1)
    return cache[name]


# ---- writing -------------------------------------------------------------------------------

def create_folder(name, parent, private=False):
    call('POST', '/api/decks/folders/', {'name': name, 'private': private, 'parentFolder': parent})
    found = []

    def walk(node):
        if node['name'] == name:
            found.append(node['id'])
        for child in node.get('children') or []:
            walk(child)
    walk(folder_tree())
    return found[-1]


def create_deck(name, fmt='custom', folder_id=None):
    d = call('POST', '/api/decks/v2/', {
        'name': name, 'deckFormat': FORMATS.get(fmt, fmt), 'description': '', 'private': False,
        'unlisted': False, 'theorycrafted': False, 'parentFolder': folder_id,
        'extras': {'commanders': [], 'forceCardsToSingleton': False, 'game': None, 'cardPackage': None},
        'cards': []})
    if folder_id:
        move([d['id']], folder_id)
    return d['id']


def add_cards(deck_id, cards):
    """cards: iterable of (archidekt_card_id, quantity, category, foil?)."""
    adds = [{'action': 'add', 'cardid': cid, 'categories': [cat], 'patchId': f'p{i}',
             'modifications': {'quantity': q, 'modifier': 'Foil' if foil else 'Normal', 'customCmc': None,
                               'companion': False, 'flippedDefault': False, 'label': ',#656565'}}
            for i, (cid, q, cat, foil) in enumerate(cards)]
    return call('PATCH', f'/api/decks/{deck_id}/modifyCards/v2/', {'cards': adds})


def update(deck_id, **fields):
    """Rename (name=...), or set a primer (description=<quill json>, hasPrimer=True)."""
    return call('PATCH', f'/api/decks/{deck_id}/update/', fields)


def move(deck_ids, folder_id):
    return call('PATCH', '/api/massUpdate/',
                {'items': [{'type': 'deck', 'id': i, 'patch': {'parentFolder': folder_id}} for i in deck_ids]})


def tag(deck_id, tag_id, position=0):
    return call('POST', '/api/decks/tagRelations/', {'deck': deck_id, 'tag': tag_id, 'position': position})
