"""Finding a commander: underplayed commanders by mechanic, and challenge-deck rolls.

    from mtg import discovery, profile
    discovery.mechanics_for(profile.enjoys('brian'))      # ['control-swap']
    discovery.candidates(['goad'], exclude={'Karazikar, the Eye Tyrant'}, colours='BR')
    discovery.challenge(random.Random(3))                 # {'text': 'Challenge: ...', 'query': 'atag:dragon f:commander not:universesbeyond'}

Everything comes from Scryfall searches (`edhrec_rank` rides along on each card); no EDHREC calls.
"""
from . import scryfall
from .cards import front

COMMANDER = 'is:commander'
LEGAL = 'f:commander'
NO_UB = 'not:universesbeyond'  # house rule: Universes Beyond only when the player's profile allows it


def legal(allow_ub=False):
    """The Scryfall terms every discovery and challenge query carries."""
    return LEGAL if allow_ub else f'{LEGAL} {NO_UB}'

# Oracle-text queries, each ANDed with COMMANDER and legal(). Counts probed live are in the slice file.
# kw:monarch is wrong: it matched thousands of commanders, so monarch is an oracle search.
MECHANICS = {
    'control-swap': '(o:"target opponent gains control" or o:"target player gains control" '
                    'or o:"exchange control" or o:"under the control of an opponent")',
    'goad': 'o:goad',
    'vote': '(o:"will of the council" or o:vote)',
    'coin': 'o:"flip a coin"',
    'monarch': 'o:monarch',
    'each-player': 'o:"each player"',
    'chaos': 'o:"at random"',
}

# Words in a profile's "enjoys" bullets that point at each mechanic (lower case, substring match).
KEYWORDS = {
    'control-swap': ('control', 'play for other', 'donate', 'works for the table', 'give away', 'gift'),
    'goad': ('goad', 'attack each other', 'forced combat'),
    'vote': ('vote', 'council', 'politic'),
    'coin': ('coin', 'luck', 'gamble'),
    'monarch': ('monarch', 'initiative'),
    'each-player': ('each player', 'group hug', 'symmetric', 'everyone gets'),
    'chaos': ('random', 'chaos', 'weird'),
}

# Art tags (atag:), each probed at 100-2500 Commander-legal cards on 2026-10-24: enough for a deck, few
# enough to be a challenge (sword, tree and eye matched 3000+ and were dropped).
ART_TAGS = ['dragon', 'cat', 'dog', 'moon', 'sun', 'skull', 'ship', 'castle', 'ocean', 'lightning', 'snow',
            'owl', 'bird', 'horse', 'spider', 'angel', 'demon', 'wolf', 'frog', 'rat', 'mushroom', 'book',
            'skeleton', 'crown', 'waterfall', 'ghost', 'tentacle', 'octopus', 'bat']
# Flavour-text words (ft:), each 130-850 Commander-legal cards on 2026-10-24.
FLAVOUR_WORDS = ['moon', 'blood', 'dream', 'shadow', 'storm', 'king', 'gold', 'song', 'fire', 'death']
YEARS = range(1995, 2026)
KINDS = ('commander', 'art', 'flavour', 'year')


def mechanics_for(enjoys):
    """Mechanic names whose keywords appear in any of the profile's enjoys bullets."""
    text = ' '.join(enjoys).lower()
    return [m for m, words in KEYWORDS.items() if any(w in text for w in words)]


def query(mechanic, colours=None, allow_ub=False):
    """The Scryfall query for a mechanic's commanders, optionally within a colour identity ('BR')."""
    q = f'{MECHANICS[mechanic]} {COMMANDER} {legal(allow_ub)}'
    return f'{q} id<={colours}' if colours else q


def candidates(mechanics, exclude=(), colours=None, allow_ub=False):
    """[(name, [mechanics], edhrec_rank, identity)] for commanders with any of the mechanics, least played first
    (highest Scryfall edhrec_rank; unranked ones first of all). exclude: names to skip (front faces match)."""
    skip = set(map(front, exclude))
    found = {}
    for m in mechanics:
        for c in scryfall.search(query(m, colours, allow_ub)):
            if front(c['name']) in skip:
                continue
            entry = found.setdefault(c['name'], [c, []])
            entry[1].append(m)
    rows = [(name, ms, c.get('edhrec_rank'), ''.join(x for x in 'WUBRG' if x in c['color_identity']))
            for name, (c, ms) in found.items()]
    rows.sort(key=lambda r: (-(r[2] or float('inf')), r[0]))
    return rows


def challenge(rng, kinds=None, exclude=(), allow_ub=False):
    """Roll a challenge deck: {'text', 'query'}, where query is the Scryfall search bounding the card pool.
    kinds: some of KINDS (default all). Every roll comes from rng, so the same seed gives the same challenge
    while Scryfall's data doesn't change."""
    kind = rng.choice(list(kinds or KINDS))
    if kind == 'commander':
        mech = rng.choice(sorted(MECHANICS))
        pick = rng.choice(candidates([mech], exclude, allow_ub=allow_ub)[:10])
        name, ident = pick[0], pick[3] or 'C'
        return {'text': f'Challenge: build {name}, one of the least-played {mech} commanders',
                'query': f'id<={ident} {legal(allow_ub)}'}
    if kind == 'art':
        tag = rng.choice(ART_TAGS)
        pool, rule = f'atag:{tag} {legal(allow_ub)}', f'only cards whose art shows a {tag}'
    elif kind == 'flavour':
        word = rng.choice(FLAVOUR_WORDS)
        pool, rule = f'ft:{word} {legal(allow_ub)}', f'only cards whose flavour text says "{word}"'
    else:
        year = rng.choice(YEARS)
        pool, rule = f'year:{year} {legal(allow_ub)}', f'only cards printed in {year}\'s sets'
    skip = set(map(front, exclude))
    leaders = sorted(c['name'] for c in scryfall.search(f'{pool} is:commander') if front(c['name']) not in skip)
    name = rng.choice(leaders)
    return {'text': f'Challenge: build {name} with {rule}', 'query': pool}
