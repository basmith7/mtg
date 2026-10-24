"""Commander bracket rules: the official bracket, the house verdict, and what makes a combo fast (pure).

    from mtg import brackets
    brackets.is_fast(combo, mv)              # combo: a spellbook combo dict; mv: card name -> mana value or None
    fl = brackets.flags(classified, sb_cards) # {'mld': [names], 'extra-turn': [names], 'goad': ...}
    brackets.official(gcs, fl, combos)       # (2..4, [reasons])
    brackets.house(gcs, fl, combos, max_gc)  # (ok, [reasons])
    brackets.line(official, spellbook, house)
    brackets.pitch(official, house, fl, salt_summary, share)   # a Rule 0 sentence

Official criteria (WotC Commander Brackets; checked against the 2025-10-21 and 2026-02-09 updates): Brackets 1-2
have no Game Changers, Bracket 3 up to three; mass land denial, chained extra turns and early two-card
combos are Bracket 4 territory; a late two-card combo is Bracket 3. Bracket 5 (cEDH) and Bracket 1
(theme) are intent, so they are never inferred. House rules: RULES.md.
"""
from mtg import patterns

FAST_MV = 6  # combo pieces totalling this much mana value or less can land by turn 3-4
OFFICIAL_MAX_GC = 3  # Bracket 3's cap


def total_mv(combo, mv):
    """Sum of the pieces' mana values, or None if any is unknown."""
    mvs = [mv(n) for n in combo['cards']]
    return None if None in mvs else int(sum(mvs))


def is_fast(combo, mv):
    """FAST: pieces total FAST_MV or less, or Spellbook rates it Ruthless or Banned. An unknown mana value
    counts as fast, so it gets looked at."""
    t = total_mv(combo, mv)
    return t is None or t <= FAST_MV or combo['bracket'] in ('Ruthless', 'Banned')


def mana_value(data):
    """card name -> mana value or None, from Scryfall data ({name: card})."""
    def mv(n):  # Spellbook sometimes names one face of a double-faced card
        c = data.get(n) or next((v for k, v in data.items() if n in k.split(' // ')), None)
        return c.get('cmc', 0) if c else None
    return mv


def flags(classified, spellbook_cards=None):
    """{tag: [names]} for every patterns tag. classified: {name: patterns.classify(card)}.
    spellbook_cards: estimate_bracket's 'cards' (or None); a card Spellbook lists takes its `mld` and
    `extra-turn` from there."""
    sb = {c['name']: c for c in spellbook_cards or []}
    out = {t: [] for t in patterns.PATTERNS}
    for name, tags in classified.items():
        c = sb.get(name)
        if c:
            tags = (tags - {'mld', 'extra-turn'}) | {
                t for t, on in (('mld', c['mass_land_denial']), ('extra-turn', c['extra_turn'])) if on}
        for t in tags:
            out[t].append(name)
    return out


def _cards(c):
    return ' + '.join(c['cards'])


def _shared(flags):
    """Problems both the official Bracket 3 and the house rules reject."""
    out = ['mass land denial: ' + ', '.join(flags['mld'])] if flags['mld'] else []
    if len(flags['extra-turn']) > 1:
        out.append('extra-turn chain: ' + ', '.join(flags['extra-turn']))
    return out


def _two(c):
    """'two-card combo', or 'two-card combo (plus the commander)' when Spellbook counts a three-piece combo
    as two cards because one piece is the commander, always available."""
    return 'two-card combo' + (' (plus the commander)' if len(set(c['cards'])) > 2 else '')


def official(gcs, flags, combos):
    """(bracket, [reasons]). gcs: Game Changer names; flags: from flags(); combos: dicts with 'cards',
    'two_card' and 'fast' (spellbook.estimate_bracket combos, 'fast' from is_fast)."""
    two = [c for c in combos if c['two_card']]
    four = [f'{len(gcs)} Game Changers'] if len(gcs) > OFFICIAL_MAX_GC else []
    four += _shared(flags) + [f'fast {_two(c)}: {_cards(c)}' for c in two if c['fast']]
    if four:
        return 4, four
    three = [f'{len(gcs)} Game Changer{"s" * (len(gcs) > 1)}'] if gcs else []
    three += [f'late {_two(c)}: {_cards(c)}' for c in two]
    if three:
        return 3, three
    return 2, ['no Game Changers or two-card combos']


def house(gcs, flags, combos, max_gc):
    """(ok, [reasons]) against RULES.md. combos: dicts with 'cards', 'fast', 'infinite' and 'url'
    (find_combos' included combos, annotated)."""
    out = [f'{len(gcs)} Game Changers (max {max_gc})'] if len(gcs) > max_gc else []
    out += _shared(flags)
    out += [f'fast infinite combo: {_cards(c)} ({c["url"]})' for c in combos if c['fast'] and c['infinite']]
    return not out, out


def line(official, spellbook, house):
    """'bracket: Official B4 (4 Game Changers) · Spellbook R (Ruthless) · House 3.75 ✓'.
    spellbook: estimate_bracket's dict, or a short string such as 'unavailable'."""
    n, why = official
    sb = f'{spellbook["tag"]} ({spellbook["name"]})' if isinstance(spellbook, dict) else spellbook
    return f'bracket: Official B{n} ({"; ".join(why)}) · Spellbook {sb} · House 3.75 {"✓" if house[0] else "✗"}'


THEMES = {'goad': 'goad', 'theft': 'theft', 'donate': 'gift', 'stax': 'stax', 'vote': 'voting', 'coin': 'coin-flip',
          'monarch': 'monarch'}
THEME_MIN = 3  # cards with a tag before it names the deck


def pitch(official, house, flags, salt_summary, share):
    """One plain Rule 0 sentence for the other players, e.g. 'Goad and theft deck, B4 on paper
    (4 Game Changers) but no stax, land wipes or fast combos.' Never names a tool."""
    themes = sorted((t for t in THEMES if len(flags[t]) >= THEME_MIN), key=lambda t: -len(flags[t]))[:2]
    what = (' and '.join(THEMES[t] for t in themes).capitalize() + ' deck' if themes
            else 'Interactive deck' if share >= 0.25 else 'Mostly self-focused deck')
    n, why = official
    fast = any(r.startswith('fast two-card') for r in why)
    present = {'stax': bool(flags['stax']), 'land wipes': bool(flags['mld']),
               'extra-turn chains': len(flags['extra-turn']) > 1, 'fast combos': fast}
    absent = [k for k, v in present.items() if not v]
    has = [k for k, v in present.items() if v]
    out = f'{what}, B{n} on paper ({why[0]})'
    if has:
        out += ' with ' + _join(has)
    elif absent:
        out += ' but no ' + _join(absent, 'or')
    if salt_summary['over2']:
        out += f'; the saltiest card is {salt_summary["top"][0][0]}'
    if not house[0]:
        out += '; it bends our house rules'
    return out + '.'


def _join(xs, word='and'):
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + f' {word} ' + xs[-1]
