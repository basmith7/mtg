"""Commander bracket rules: what makes a combo fast (pure: no network).

    from mtg import brackets
    brackets.is_fast(combo, mv)   # combo: a spellbook combo dict; mv: card name -> mana value or None
"""
FAST_MV = 6  # combo pieces totalling this much mana value or less can land by turn 3-4


def total_mv(combo, mv):
    """Sum of the pieces' mana values, or None if any is unknown."""
    mvs = [mv(n) for n in combo['cards']]
    return None if None in mvs else int(sum(mvs))


def is_fast(combo, mv):
    """FAST: pieces total FAST_MV or less, or Spellbook rates it Ruthless or Banned. An unknown mana value
    counts as fast, so it gets looked at."""
    t = total_mv(combo, mv)
    return t is None or t <= FAST_MV or combo['bracket'] in ('Ruthless', 'Banned')
