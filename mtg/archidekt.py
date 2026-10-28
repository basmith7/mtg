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

from . import config, decklist, http, printings, quill

BASE = 'https://archidekt.com'
SESSION = os.path.expanduser('~/.config/mtg/archidekt-session.json')
TYPES = ['Land', 'Creature', 'Planeswalker', 'Battle', 'Artifact', 'Enchantment', 'Instant', 'Sorcery']
FORMATS = {'commander': 3, 'custom': 7}  # Archidekt's deckFormat ids


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

def deck_id_of(ref):
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


# ---- card ids ------------------------------------------------------------------------------

def resolve(names):
    """{name: (Archidekt card id, type category, picked?)} for card names, at the printing mtg.printings
    picks (fancy but readable, never Universes Beyond) where it can.

    Archidekt adds cards by its own id. The picked printings are looked up by Scryfall id; a card whose
    picks Archidekt lacks goes through the parser behind the deck editor's "Import cards" box
    (massDeckEdit), which takes a pasted list, returns the printing the site itself picks, and accepts
    front-face names; those come back with picked False. Raises KeyError listing every card it can't find.
    """
    names = list(dict.fromkeys(names))
    if not names:
        return {}
    picks = printings.best(names)
    by_uid = _by_uid([u for us in picks.values() for u in us])
    out = {}
    for n in names:
        card = next((by_uid[u] for u in picks.get(n, []) if u in by_uid), None)
        if card:
            out[n] = (card['id'], _category(card), True)
    rest = [n for n in names if n not in out]
    if rest:
        r = call('POST', '/api/cards/massDeckEdit/', {'parser': 'archidekt', 'current': '',
                                                      'edit': ''.join(f'1 {n}\n' for n in rest)})
        if r['syntaxErrors'] or r['cardErrors']:
            raise KeyError('; '.join(r['syntaxErrors'] + r['cardErrors']))
        found = {e['name']: e['card'] for e in r['toAdd']}
        out.update({n: (found[n]['id'], _category(found[n]), False) for n in rest})
    return {n: out[n] for n in names}


def _category(card):
    return next((t for t in TYPES if t in card['oracleCard']['types']), 'Other')


def _by_uid(uids):
    """{Scryfall id: Archidekt card} for the ids Archidekt has, 60 a request."""
    out = {}
    for i in range(0, len(uids), 60):
        url = f"/api/cards/v2/?uids={','.join(uids[i:i + 60])}"
        while url:
            if out or i:
                time.sleep(1)  # Archidekt rate-limits quickly
            r = call('GET', url)
            out.update({c['uid']: c for c in r['results']})
            url = r.get('next') and urllib.parse.urlsplit(r['next'])._replace(scheme='', netloc='').geturl()  # http://, not BASE
    return out


# ---- writing -------------------------------------------------------------------------------

def create_deck(name, fmt='custom', folder_id=None):
    d = call('POST', '/api/decks/v2/', {
        'name': name, 'deckFormat': FORMATS[fmt], 'description': '', 'private': False,
        'unlisted': False, 'theorycrafted': False, 'parentFolder': folder_id,
        'extras': {'commanders': [], 'forceCardsToSingleton': False, 'game': None, 'cardPackage': None},
        'cards': []})
    if folder_id:
        move([d['id']], folder_id)
    return d['id']


def add_cards(deck_id, cards):
    """cards: iterable of (archidekt_card_id, quantity, categories list, foil?)."""
    adds = [{'action': 'add', 'cardid': cid, 'categories': cats, 'patchId': f'p{i}',
             'modifications': {'quantity': q, 'modifier': 'Foil' if foil else 'Normal', 'customCmc': None,
                               'companion': False, 'flippedDefault': False, 'label': ',#656565'}}
            for i, (cid, q, cats, foil) in enumerate(cards)]
    return call('PATCH', f'/api/decks/{deck_id}/modifyCards/v2/', {'cards': adds}) if adds else {}


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


def is_commander(entry):
    return 'commander' in map(str.lower, entry['categories'])


def export(d):
    """A deck JSON as a decklist: {name, commanders, cards (Counter), primer (markdown), dropped
    (primer formatting markdown can't hold, see quill.from_delta)}."""
    main = main_cards(d)
    primer, dropped = quill.from_delta(d.get('description') or '')
    return {'name': d['name'],
            'commanders': [c for c, es in main.items() if any(map(is_commander, es))],
            'cards': Counter({c: sum(e['quantity'] for e in es) for c, es in main.items()}),
            'primer': primer, 'dropped': dropped}


class Refused(Exception):
    """sync would overwrite something on the site; nothing was written."""


def sync(path, primer=True, dry_run=False, force=False, reprint=False):
    """Make the deck on a decklist's '# source:' line match the file. Returns a summary dict.

    New cards get the printing mtg.printings picks; with reprint, so do existing cards on another
    printing (re-added in their categories and foil, so a printing chosen on the site is lost). Existing cards keep their
    categories (only Commander membership is enforced); Maybeboard,
    Sideboard and not-in-deck categories on the site are left alone. Renames the deck to the file's
    '# Name' header. With primer, the '.md' beside the file replaces the site primer if they differ.
    Resolves every new card id before writing anything, and backs up the deck JSON.

    Unless force, raises Refused before writing if the site deck changed since the version on the
    file's '# updated:' line (or the file has none), or if a changed primer would flatten site
    formatting markdown can't hold; a dry run reports both instead. After a push that matches, the
    file's '# updated:' line gets the new version.
    """
    deck_id = deck_id_of(decklist.meta(path, 'source') or '')
    if not deck_id:
        raise ValueError(f'{path} has no Archidekt # source: line')
    d = deck(deck_id)
    name, _, want = decklist.parse(path)
    rename = open(path).readline().startswith('#') and name != d['name']
    cmdrs = decklist.commanders(path)
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
        if e['quantity'] != q or is_commander(e) != (c in cmdrs):
            mod.append((e, c, q))
    # Card ids and categories for what's added or moved; an unknown card fails here, before any write.
    cards = resolve([c for c, _ in add] + [c for e, c, _ in mod if is_commander(e) != (c in cmdrs)]
                    + ([c for c in want if c in have and len(have[c]) == 1] if reprint else []))
    # Reprint only to a picked printing: the site's own pick may be the Universes Beyond one.
    moving = {id(e) for e, _, _ in mod}
    reprints = [(c, have[c][0]) for c in want if reprint and len(have.get(c, [])) == 1 and id(have[c][0]) not in moving
                and cards[c][2] and have[c][0]['card']['id'] != cards[c][0]]
    cat = lambda c: 'Commander' if c in cmdrs else cards[c][1]
    mod = [(e, q, [cat(c)] if is_commander(e) != (c in cmdrs) else None) for e, c, q in mod]
    site_md, dropped = quill.from_delta(d.get('description') or '')
    md = os.path.splitext(path)[0] + '.md'
    text = open(md).read() if primer and os.path.exists(md) else None
    if text is not None and quill.to_delta(text) == quill.to_delta(site_md):
        text = None
    summary = {'url': url(deck_id),
               'removed': sorted(e['card']['oracleCard']['name'] for e in rm),
               'added': [f'{q} {c}' for c, q in add],
               'changed': [f"{e['card']['oracleCard']['name']}: {e['quantity']} -> {q}" if e['quantity'] != q
                           else f"{e['card']['oracleCard']['name']}: -> {k[0]}" for e, q, k in mod],
               'reprinted': sorted(c for c, _ in reprints),
               'renamed': name if rename else None, 'primer': text is not None, 'match': None,
               'stale': decklist.meta(path, 'updated') != d['updatedAt'],
               'primer_loses': dropped if text is not None else []}
    if dry_run:
        return summary
    if not force and summary['stale']:
        raise Refused(f"{url(deck_id)} changed on the site since this file was pulled or pushed: pull it "
                      f"(scripts/pull.py {deck_id}) and redo the change, or force")
    if not force and summary['primer_loses']:
        raise Refused(f"the new primer would drop the site primer's {', '.join(dropped)} formatting; "
                      f"skip the primer or force")
    backups = os.path.join(config.CACHE, 'backups')
    os.makedirs(backups, exist_ok=True)
    summary['backup'] = os.path.join(backups, f"{deck_id}-{datetime.datetime.now():%Y%m%d-%H%M%S-%f}.json")
    json.dump(d, open(summary['backup'], 'w'))
    remove_cards(deck_id, rm + [e for _, e in reprints])
    modify_cards(deck_id, mod)
    add_cards(deck_id, [(cards[c][0], q, [cat(c)], False) for c, q in add]
              + [(cards[c][0], e['quantity'], e['categories'], e.get('modifier') == 'Foil') for c, e in reprints])
    if rename:
        update(deck_id, name=name)
    if text is not None:
        update(deck_id, description=quill.to_delta(text), hasPrimer=True)
    after = deck(deck_id)
    got = {c: sum(e['quantity'] for e in es) for c, es in main_cards(after).items()}
    summary['match'] = got == dict(want)
    if summary['match']:
        decklist.set_meta(path, 'updated', after['updatedAt'])
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
