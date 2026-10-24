"""Oracle-text patterns: what a card does to the table (pure: no network).

    from mtg import patterns
    patterns.classify(card)   # card: a Scryfall card dict -> frozenset of tags, e.g. {'mld'}

Regexes are a fallback and a cross-check: where Commander Spellbook flags a card
(`spellbook.estimate_bracket`), its `mld` and `extra-turn` flags win. Scryfall's `otag:stax` and
`otag:land-destruction` match nothing (probed 2026-10-24), so these regexes own the rest.
"""
import re

PATTERNS = {
    'mld': r"(destroy|exile) all [^.]*\blands\b|return all lands|sacrifices? (all|\w+) lands|lands don't untap"
           r"|nonbasic lands are mountains",
    'extra-turn': r'takes? an extra turn|extra turn after this one',
    'stax': r"can't untap|don't untap|doesn't untap|each player can't|can't attack you unless"
            r"|(?<!this spell )costs? \{\d+\} more",
    'theft': r'\bgain control of|you control enchanted (creature|permanent|artifact)|exchange control',
    'donate': r'(target|an) (opponent|player) gains control|enters under the control of an opponent',
    'goad': r'\bgoad|attack (each combat|this turn) if able|a player other than you',
    'vote': r'\bvotes?\b',
    'coin': r'\bflips? (a|two|\w+) coins?',
    'monarch': r'\bmonarch\b',
    'each-opponent': r'each opponent|target opponent|each player',
}
_RE = {tag: re.compile(p, re.I) for tag, p in PATTERNS.items()}


def classify(card):
    """frozenset of tags whose pattern matches the card's oracle text (all faces)."""
    text = card.get('oracle_text') or ' // '.join(f.get('oracle_text', '') for f in card.get('card_faces', []))
    return frozenset(tag for tag, rx in _RE.items() if rx.search(text))
