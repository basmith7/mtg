"""Archidekt client (private API; see docs/apis.md).

Logs in once with ARCHIDEKT_USERNAME and ARCHIDEKT_PASSWORD from mtg.config (the password falls back to
the 1Password item ARCHIDEKT_OP_ITEM, which prompts), caches the JWT in ~/.config/mtg/archidekt-session.json,
and renews it with the refresh token.
"""
import datetime
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
from collections import Counter

from . import config, decklist, http, quill, scryfall

BASE = 'https://archidekt.com'
SESSION = os.path.expanduser('~/.config/mtg/archidekt-session.json')
SEEN = os.path.expanduser('~/.cache/mtg/archidekt-seen.json')  # {deck id: updatedAt we last pulled or pushed}
TYPES = ['Land', 'Creature', 'Planeswalker', 'Battle', 'Artifact', 'Enchantment', 'Instant', 'Sorcery']
FORMATS = {'standard': 1, 'modern': 2, 'commander': 3, 'legacy': 4, 'vintage': 5, 'pauper': 6, 'custom': 7,
           'pioneer': 15, 'historic': 16, 'brawl': 13, 'oathbreaker': 14, 'premodern': 22}


def _save(session):
    os.makedirs(os.path.dirname(SESSION), exist_ok=True)
    fd = os.open(SESSION, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(session, f)


def _password():
    """ARCHIDEKT_PASSWORD from mtg.config, else the 1Password item ARCHIDEKT_OP_ITEM. Never print it."""
    pw = config.get('ARCHIDEKT_PASSWORD', required=False)
    if pw:
        return pw
    item = config.get('ARCHIDEKT_OP_ITEM')
    return subprocess.run(['op', 'item', 'get', item, '--fields', 'password', '--reveal'],
                          capture_output=True, text=True, check=True).stdout.strip()


def login():
    """Full login; never prints the password."""
    pw = _password()
    r = http.request('POST', f'{BASE}/api/rest-auth/login/',
                     {'username': config.get('ARCHIDEKT_USERNAME'), 'password': pw})
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

def deck_id(ref):
    """A deck id from an id or an archidekt.com/decks/<id> URL (None if it's neither)."""
    ref = str(ref)
    if ref.isdigit():
        return int(ref)
    m = re.search(r'archidekt\.com/decks/(\d+)', ref)
    return int(m.group(1)) if m else None


def url(deck_id):
    return f'{BASE}/decks/{deck_id}'


def deck(deck_id):
    return call('GET', f'/api/decks/{deck_id}/')


def folder_tree():
    return call('GET', '/api/decks/folderTree/')


def folder(folder_id):
    """The folder JSON, with every page of its 'decks' merged in."""
    f, page = call('GET', f'/api/decks/folders/{folder_id}/?pageSize=100'), 1
    while f.get('next'):
        page += 1
        f['decks'] += call('GET', f'/api/decks/folders/{folder_id}/?pageSize=100&page={page}')['decks']
        f['next'] = None if len(f['decks']) >= f['count'] else f['next']
    return f


def my_decks():
    out, page, user = [], 1, config.get('ARCHIDEKT_USERNAME')
    while True:
        r = call('GET', f'/api/decks/v3/?ownerUsername={user}&pageSize=50&page={page}')
        out += r['results']
        if not r.get('next'):
            return out
        page += 1


def collection():
    out, page, user_id = [], 1, config.get('ARCHIDEKT_USER_ID')
    while True:
        r = call('GET', f'/api/collection/{user_id}/v2/?game=1&page={page}&pageSize=100')
        out += r['results']
        if page >= r['totalPages']:
            return out
        page += 1
        time.sleep(0.6)


def search_tags(text):
    return call('GET', '/api/decks/tags/v2/?' + urllib.parse.urlencode({'q': text}), auth=False)


# ---- categories ----------------------------------------------------------------------------

# ---- card ids ------------------------------------------------------------------------------

def resolve(names):
    """{name: (Archidekt card id, type category)} for card names, in one request.

    Archidekt adds cards by its own id. This asks the parser behind the deck editor's "Import cards"
    box (massDeckEdit), which takes a pasted list and returns each card with the printing the site
    itself picks; it accepts front-face names. Raises KeyError listing every card it can't find.
    """
    names = list(dict.fromkeys(names))
    if not names:
        return {}
    r = call('POST', '/api/cards/massDeckEdit/', {'parser': 'archidekt', 'current': '',
                                                  'edit': ''.join(f'1 {n}\n' for n in names)})
    if r['syntaxErrors'] or r['cardErrors']:
        raise KeyError('; '.join(r['syntaxErrors'] + r['cardErrors']))
    found = {e['name']: e['card'] for e in r['toAdd']}
    return {n: (found[n]['id'], next((t for t in TYPES if t in found[n]['oracleCard']['types']), 'Other'))
            for n in names}


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


def _entry_mods(e, quantity=None):
    return {'quantity': quantity or e['quantity'], 'modifier': e.get('modifier') or 'Normal',
            'customCmc': e.get('customCmc'), 'companion': bool(e.get('companion')),
            'flippedDefault': bool(e.get('flippedDefault')), 'label': e.get('label') or ',#656565'}


def _patch(deck_id, action, entries, categories=None, quantities=None):
    cards = [{'action': action, 'cardid': e['card']['id'], 'categories': (categories or {}).get(i, e['categories']),
              'patchId': f'{action[0]}{i}', 'deckRelationId': e['id'],
              'modifications': _entry_mods(e, (quantities or {}).get(i))} for i, e in enumerate(entries)]
    return call('PATCH', f'/api/decks/{deck_id}/modifyCards/v2/', {'cards': cards}) if cards else {}


def remove_cards(deck_id, entries):
    """entries: the deck's own card entries (from deck(id)['cards'])."""
    return _patch(deck_id, 'remove', entries)


def modify_cards(deck_id, changes):
    """changes: iterable of (deck card entry, new quantity, new categories list or None to keep them)."""
    changes = list(changes)
    return _patch(deck_id, 'modify', [e for e, _, _ in changes],
                  {i: c for i, (_, _, c) in enumerate(changes) if c}, {i: q for i, (_, q, _) in enumerate(changes)})


SIDE = {'Maybeboard', 'Sideboard'}


def main_cards(d):
    """{card name: [entries]} for a deck JSON's main entries. Maybeboard, Sideboard, any category the
    deck marks not included (Archidekt's own flag; 'Tokens' etc. can be real in-deck categories) and
    deleted entries are left out, so sync never touches them. Category names compare case-insensitively."""
    side = {c.lower() for c in SIDE} | {c['name'].lower() for c in d.get('categories', [])
                                        if not c.get('includedInDeck', True)}
    out = {}
    for e in d['cards']:
        if not e.get('deletedAt') and not side & {c.lower() for c in e['categories']}:
            out.setdefault(e['card']['oracleCard']['name'], []).append(e)
    return out


def export(d):
    """A deck JSON as a decklist: {name, commanders, cards (Counter), primer (markdown), dropped
    (primer formatting markdown can't hold, see quill.from_delta)}."""
    main = main_cards(d)
    primer, dropped = quill.from_delta(d.get('description') or '')
    return {'name': d['name'],
            'commanders': [c for c, es in main.items() if any('commander' in map(str.lower, e['categories']) for e in es)],
            'cards': Counter({c: sum(e['quantity'] for e in es) for c, es in main.items()}),
            'primer': primer, 'dropped': dropped}


def compare(decklist_path, d):
    """How a decklist file (and the .md primer beside it) differs from a deck JSON."""
    _, _, want = decklist.parse(decklist_path)
    site = export(d)
    have = site['cards']
    md = os.path.splitext(decklist_path)[0] + '.md'
    local = open(md).read() if os.path.exists(md) else ''
    if not local and not site['primer']:
        primer = 'none'
    elif not site['primer'] or not local:
        primer = 'site only' if site['primer'] else 'local only'
    else:
        primer = 'same' if quill.to_delta(local) == quill.to_delta(site['primer']) else 'differs'
    return {'missing_on_site': sorted(want.keys() - have.keys()),
            'extra_on_site': sorted(have.keys() - want.keys()),
            'qty_diffs': sorted(f'{c}: {want[c]} here, {have[c]} on site' for c in want.keys() & have.keys()
                                if want[c] != have[c]),
            'commanders_match': sorted(decklist.commanders(decklist_path)) == sorted(site['commanders']),
            'primer': primer}


def mark_seen(d):
    """Record the deck's updatedAt: the local copy now matches this version of the site deck."""
    seen = json.load(open(SEEN)) if os.path.exists(SEEN) else {}
    seen[str(d['id'])] = d['updatedAt']
    os.makedirs(os.path.dirname(SEEN), exist_ok=True)
    with open(SEEN, 'w') as f:
        json.dump(seen, f)


def is_stale(d):
    """True if the site deck changed since we last pulled or pushed it (or we never did)."""
    seen = json.load(open(SEEN)) if os.path.exists(SEEN) else {}
    return seen.get(str(d['id'])) != d['updatedAt']


class Refused(Exception):
    """sync would overwrite something on the site; nothing was written."""


def sync(deck_id, decklist_path, primer_path=None, dry_run=False, rename=True, force=False):
    """Make a deck's main list match a decklist file. Returns a summary dict.

    Existing cards keep their categories (only Commander membership is enforced); Maybeboard,
    Sideboard and not-in-deck categories on the site are left alone. Renames only if the file has a
    '# Name' header. The primer is written only if it differs from the site's. Resolves every new card
    id before writing anything, and backs up the deck JSON.

    Unless force, raises Refused before writing if the site deck changed since it was last pulled or
    pushed (is_stale), or if a changed primer would flatten site formatting markdown can't hold.
    A dry run reports both in the summary instead.
    """
    d = deck(deck_id)
    name, _, want = decklist.parse(decklist_path)
    rename = rename and open(decklist_path).readline().startswith('#')
    cmdrs = decklist.commanders(decklist_path)
    have = main_cards(d)
    rm, mod, add = [], [], []
    for c, entries in have.items():
        if c not in want:
            rm += entries
    for c, q in want.items():
        entries = have.get(c, [])
        if len(entries) > 1:  # split across printings/categories: rebuild as one entry
            rm += entries
            entries = []
        if not entries:
            add.append((c, q))
            continue
        e = entries[0]
        if e['quantity'] != q or ('Commander' in e['categories']) != (c in cmdrs):
            mod.append((e, c, q))
    # Card ids and categories for what's added or moved; an unknown card fails here, before any write.
    cards = resolve([c for c, _ in add] + [c for e, c, _ in mod if ('Commander' in e['categories']) != (c in cmdrs)])
    cat = lambda c: 'Commander' if c in cmdrs else cards[c][1]
    mod = [(e, q, [cat(c)] if c in cards else None) for e, c, q in mod]
    site_md, dropped = quill.from_delta(d.get('description') or '')
    primer = open(primer_path).read() if primer_path else None
    if primer is not None and quill.to_delta(primer) == quill.to_delta(site_md):
        primer = None
    summary = {'removed': sorted(e['card']['oracleCard']['name'] for e in rm),
               'added': [f'{q} {c}' for c, q in add],
               'changed': [f"{e['card']['oracleCard']['name']}: {e['quantity']} -> {q}" if e['quantity'] != q
                           else f"{e['card']['oracleCard']['name']}: -> {k[0]}" for e, q, k in mod],
               'renamed': name if rename and name != d['name'] else None,
               'primer': primer is not None, 'dry_run': dry_run, 'match': None,
               'stale': is_stale(d), 'primer_loses': dropped if primer is not None else []}
    if dry_run:
        return summary
    if not force and summary['stale']:
        raise Refused(f"{url(deck_id)} changed on the site since it was last pulled or pushed: pull it first "
                      f"(scripts/pull_deck.py {deck_id}), or force")
    if not force and summary['primer_loses']:
        raise Refused(f"the new primer would drop the site primer's {', '.join(dropped)} formatting; "
                      f"skip the primer or force")
    new = [(cards[c][0], q, cat(c), False) for c, q in add]
    backups = os.path.expanduser('~/.cache/mtg-backups')
    os.makedirs(backups, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    json.dump(d, open(os.path.join(backups, f'archidekt-{deck_id}-{stamp}.json'), 'w'))
    summary['backup'] = os.path.join(backups, f'archidekt-{deck_id}-{stamp}.json')
    remove_cards(deck_id, rm)
    modify_cards(deck_id, mod)
    if new:
        add_cards(deck_id, new)
    if summary['renamed']:
        update(deck_id, name=name)
    if primer is not None:
        update(deck_id, description=quill.to_delta(primer), hasPrimer=True)
    after = deck(deck_id)
    got = {c: sum(e['quantity'] for e in es) for c, es in main_cards(after).items()}
    summary['match'] = got == dict(want)
    if summary['match']:
        mark_seen(after)
    return summary


def update(deck_id, **fields):
    """Rename (name=...), or set a primer (description=<quill json>, hasPrimer=True)."""
    return call('PATCH', f'/api/decks/{deck_id}/update/', fields)


def archive(deck_ids):
    """Move decks to the player's archive folder (ARCHIDEKT_ARCHIVE_FOLDER). Archive rather than delete."""
    return move(deck_ids, int(config.get('ARCHIDEKT_ARCHIVE_FOLDER')))


def move(deck_ids, folder_id):
    return call('PATCH', '/api/massUpdate/',
                {'items': [{'type': 'deck', 'id': i, 'patch': {'parentFolder': folder_id}} for i in deck_ids]})


def tag(deck_id, tag_id, position=0):
    return call('POST', '/api/decks/tagRelations/', {'deck': deck_id, 'tag': tag_id, 'position': position})
