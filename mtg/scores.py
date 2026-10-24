"""Scores derived from EDHREC data and decklists. Pure: no network, callers pass the data in.

    from mtg import scores
    scores.gems(edhrec.commander(name)['cards'])           # high-lift cards few decks play
"""

# --- gems, staple share, overlap, density (slices 04-05) ---


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
