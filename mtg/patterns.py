"""Oracle-text patterns: what a card does to the table (pure: no network).

    from mtg import patterns
    patterns.classify(card)   # card: a Scryfall card dict -> frozenset of tags, e.g. {'mld'}

Tags: `mld` (mass land denial), `extra-turn`. Regexes are a fallback and a cross-check: where
Commander Spellbook flags a card (`spellbook.estimate_bracket`), its flags win.
"""
import re

from mtg import scryfall

PATTERNS = {
    'mld': r"(destroy|exile) all [^.]*\blands\b|return all lands|sacrifices? (all|\w+) lands|lands don't untap"
           r"|nonbasic lands are mountains",
    'extra-turn': r'takes? an extra turn|extra turn after this one',
}
_RE = {tag: re.compile(p, re.I) for tag, p in PATTERNS.items()}


def classify(card):
    """frozenset of tags whose pattern matches the card's oracle text (all faces)."""
    text = scryfall.oracle_text(card)
    return frozenset(tag for tag, rx in _RE.items() if rx.search(text))
