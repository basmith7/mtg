"""Scryfall card dicts and card names: the small facts every tool needs (pure: no network).

    from mtg import cards
    cards.front('Fire // Ice')     # 'Fire'
    cards.oracle_text(card)        # faces joined for split and double-faced cards
    cards.is_land(card)            # by the front face's type line
"""


def front(name):
    """The front face of a split, modal or double-faced card name ('A // B' -> 'A'); other names unchanged."""
    return name.split(' // ')[0]


def oracle_text(card):
    """Oracle text, joining faces for split/double-faced cards."""
    return card.get('oracle_text') or ' // '.join(f.get('oracle_text', '') for f in card.get('card_faces', []))


def is_land(card):
    """A land by its front face (a modal land-back like Valakut Awakening is a spell)."""
    return 'Land' in card.get('type_line', '').split('//')[0]
