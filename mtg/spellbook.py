"""Commander Spellbook: combos a decklist contains (public API, no auth)."""
from . import http

API = 'https://backend.commanderspellbook.com'
BRACKET_TAGS = {'C': 'Core', 'E': 'Exhibition', 'O': 'Oddball', 'P': 'Powerful', 'S': 'Spicy', 'R': 'Ruthless',
                'B': 'Banned'}


def _combo(v, deck_names):
    """Flatten an API variant. `missing` = pieces not in the deck (empty for included combos)."""
    cards = [u['card']['name'] for u in v['uses'] for _ in range(u['quantity'])]
    feats = [p['feature'] for p in v['produces']]
    main = [f['name'] for f in feats if f['status'] != 'H'] or [f['name'] for f in feats]
    return {
        'id': v['id'],
        'cards': cards,
        'missing': [c for c in dict.fromkeys(cards) if c not in deck_names],
        'results': main,
        'bracket': BRACKET_TAGS.get(v['bracketTag'], v['bracketTag']),
        'prerequisites': ' '.join(filter(None, [v['easyPrerequisites'], v['notablePrerequisites']])),
        'templates': [r['template']['name'] for r in v['requires']],
        'description': v['description'],
        'url': f'https://commanderspellbook.com/combo/{v["id"]}/',
    }


def find_combos(commanders, cards):
    """commanders, cards: lists of card names (cards = the 99, or any list; commanders may repeat there).
    Returns {'included': [...], 'almost': [...]} of combo dicts (id, cards, missing, results, bracket,
    prerequisites, templates, description, url). `almost` is missing exactly one card, in colour identity."""
    names = set(commanders) | set(cards)
    body = {'commanders': [{'card': c} for c in commanders],
            'main': [{'card': c} for c in cards if c not in commanders]}
    r = http.request('POST', f'{API}/find-my-combos', body)['results']
    return {'included': [_combo(v, names) for v in r['included']],
            'almost': [_combo(v, names) for v in r['almostIncluded']]}
