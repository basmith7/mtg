"""Scores derived from EDHREC data and decklists. Pure: no network, callers pass the data in.

    from mtg import scores
    scores.gems(edhrec.commander(name)['cards'])           # high-lift cards few decks play
    scores.staple_share(nonland_99, edhrec_cards)          # (0.38, [staples])
    scores.overlap(names, {path: names, ...})              # [(path, shared, jaccard)]
    scores.density(names, scryfall.collection(names))      # 0.0-1.0 pairwise interaction
    scores.salt_summary(names, edhrec.salt(names))         # {'avg', 'top', 'over2'}
    scores.table_share({name: patterns.classify(card)})    # share of spells that touch other players
"""
import re

from mtg import decklist

# --- gems, staple share, overlap, density (slices 04-05) ---

BASICS = decklist.BASICS | {'Wastes'} | {'Snow-Covered ' + b for b in decklist.BASICS}


def _keys(names):
    """Lower-cased names plus split/double-faced front faces, for matching EDHREC names to ours."""
    return {n.lower() for n in names} | {n.split('//')[0].strip().lower() for n in names}


def gems(cards, max_inclusion=15, min_decks=20, exclude=()):
    """EDHREC cards under max_inclusion % that at least min_decks decks play, best lift first
    (ties by synergy). exclude: names to leave out (e.g. the deck's own cards), case-insensitive."""
    skip = _keys(exclude)
    hits = [c for c in cards if c['inclusion'] < max_inclusion and c['num_decks'] >= min_decks
            and c['name'].lower() not in skip]
    return sorted(hits, key=lambda c: (-c.get('lift', 0.0), -c.get('synergy', 0.0)))


def staple_share(deck_names, edhrec_cards, threshold=40):
    """(share, [staples]): the fraction of deck_names that EDHREC plays in threshold %+ of this
    commander's decks. deck_names: the 99's nonland cards (the caller drops lands and the commander)."""
    inc = {}
    for c in edhrec_cards:
        for k in _keys([c['name']]):
            inc.setdefault(k, c['inclusion'])
    names = list(deck_names)
    staples = [n for n in names if max(inc.get(k, 0) for k in _keys([n])) >= threshold]
    return (len(staples) / len(names) if names else 0.0), staples


def overlap(deck_names, others):
    """[(path, shared, jaccard)] against each other deck ({path: set of names}), most shared first.
    Basics don't count."""
    basics = {b.lower() for b in BASICS}
    mine = {n.lower() for n in deck_names} - basics
    out = []
    for path, names in others.items():
        theirs = {n.lower() for n in names} - basics
        union = mine | theirs
        shared = len(mine & theirs)
        out.append((path, shared, shared / len(union) if union else 0.0))
    return sorted(out, key=lambda t: (-t[1], -t[2]))


# Card types worth naming in an interaction. 'creature' is left out: nearly every card names it.
_TYPES = {'artifact', 'enchantment', 'instant', 'sorcery', 'planeswalker', 'legendary', 'battle'}
_PLURALS = {'elf': 'elves', 'dwarf': 'dwarves', 'wolf': 'wolves', 'werewolf': 'werewolves',
            'mouse': 'mice', 'fungus': 'fungi', 'sorcery': 'sorceries'}
_CREATE = re.compile(r'\bcreate\b[^.]*?\btokens?\b', re.I)
_COUNTER = re.compile(r'([+-]\d+/[+-]\d+|\b[a-z]+) counters?\b', re.I)
# Words that sit before "counter" without naming a kind ("a counter", "two counters", "counter target").
_NOT_KIND = {'a', 'an', 'the', 'of', 'that', 'those', 'more', 'two', 'three', 'any', 'each', 'and', 'or',
             'its', 'with', 'no', 'put', 'remove', 'target', 'additional', 'many', 'kind', 'x'}


def _text(card):
    """Oracle text (faces joined) with the card's own name replaced, so a card never names itself."""
    text = card.get('oracle_text') or ' // '.join(f.get('oracle_text', '') for f in card.get('card_faces', []))
    name = card.get('name', '')
    for n in sorted({name, *name.split(' // ')} - {''}, key=len, reverse=True):
        text = text.replace(n, 'CARDNAME')
    return text


def _traits(card):
    """(has, keywords): what a card is or makes, lower-case: card types, subtypes, keywords,
    counters it puts, tokens it creates (and the generic 'counter' / 'token')."""
    text = _text(card)
    has = set()
    for face in card.get('type_line', '').lower().split('//'):
        types, _, subtypes = face.partition('—')
        has |= (set(types.split()) & _TYPES) | set(subtypes.split())
    keywords = {k.lower() for k in card.get('keywords', [])}
    has |= keywords
    for m in _CREATE.finditer(text):
        has.add('token')
        has |= {w.lower() for w in re.findall(r'\b[A-Z][a-z]+\b', m.group(0))} - {'create'}
    for m in _COUNTER.finditer(text):
        kind = m.group(1).lower()
        if kind not in _NOT_KIND:
            has |= {'counter', kind + ' counter'}
    return has, keywords


def _mentions(text, vocab, own_keywords):
    """The vocab terms the text names (plurals too). A card's own keywords don't count: every flier's
    text says 'Flying'."""
    low = text.lower()
    out = set()
    for term in vocab - own_keywords:
        forms = {term, term + 's', _PLURALS.get(term, term)}
        if any(re.search(r'(?<![\w+-])' + re.escape(f) + r'(?!\w)', low) for f in forms):
            out.add(term)
    return out


def density(names, data):
    """Mean pairwise interaction over the nonland cards among names (data: {name: Scryfall card}).
    Two cards interact if one's oracle text names a type, subtype, counter, keyword or token the other
    is or makes. Idea from dreliq9/urza (MIT), reimplemented. Rough bands: goodstuff ~0.1, tribal ~0.5."""
    cards = [data[n] for n in dict.fromkeys(names) if n in data and 'Land' not in data[n].get('type_line', '')]
    traits = [_traits(c) for c in cards]
    vocab = set().union(*(h for h, _ in traits))
    said = [_mentions(_text(c), vocab, kw) for c, (_, kw) in zip(cards, traits)]
    pairs = hits = 0
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            pairs += 1
            hits += bool(said[i] & traits[j][0] or said[j] & traits[i][0])
    return hits / pairs if pairs else 0.0


# --- salt and table share (slice 03) ---

SALTY = 2.0  # EDHREC salt score above which a card is called out
TOP_SALT = 3


def salt_summary(names, salt):
    """{'avg', 'top': [(name, s)], 'over2': [names]} for the cards that have a salt score.
    salt: edhrec.salt(names). avg is None when no card has a score."""
    scored = sorted(((n, salt[n]) for n in dict.fromkeys(names) if n in salt), key=lambda x: -x[1])
    return {'avg': sum(s for _, s in scored) / len(scored) if scored else None,
            'top': scored[:TOP_SALT], 'over2': [n for n, s in scored if s > SALTY]}


def table_share(classified):
    """Share of cards with any table-touching tag. classified: {name: patterns.classify(card)} for the
    deck's nonland cards (the caller drops lands); every patterns tag but `extra-turn` touches the table."""
    if not classified:
        return 0.0
    return sum(bool(tags - {'extra-turn'}) for tags in classified.values()) / len(classified)
