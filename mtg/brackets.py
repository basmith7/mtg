"""Commander bracket rules: the official bracket, the house verdict, and what makes a combo fast (pure).

    from mtg import brackets
    brackets.is_fast(combo, mv)              # combo: a spellbook combo dict; mv: card name -> mana value or None
    fl = brackets.flags(classified, sb_cards) # {'mld': [names], 'extra-turn': [names]}
    brackets.official(gcs, fl, combos)       # (2..4, [reasons])
    brackets.house(gcs, fl, combos, max_gc)  # (ok, [reasons])
    brackets.line(official, spellbook, house)

Official criteria (WotC Commander Brackets; checked against the 2025-10-21 and 2026-02-09 updates): Brackets 1-2
have no Game Changers, Bracket 3 up to three; mass land denial, chained extra turns and early two-card
combos are Bracket 4 territory; a late two-card combo is Bracket 3. Bracket 5 (cEDH) and Bracket 1
(theme) are intent, so they are never inferred. House rules: RULES.md.
"""
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


def flags(classified, spellbook_cards=None):
    """{'mld': [names], 'extra-turn': [names]} for a deck. classified: {name: patterns.classify(card)}.
    spellbook_cards: estimate_bracket's 'cards' (or None); a card Spellbook lists takes its flags from there."""
    sb = {c['name']: c for c in spellbook_cards or []}
    out = {'mld': [], 'extra-turn': []}
    for name, tags in classified.items():
        c = sb.get(name)
        if c:
            tags = {t for t, on in (('mld', c['mass_land_denial']), ('extra-turn', c['extra_turn'])) if on}
        for t in out:
            if t in tags:
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


def official(gcs, flags, combos):
    """(bracket, [reasons]). gcs: Game Changer names; flags: from flags(); combos: dicts with 'cards',
    'two_card' and 'fast' (spellbook.estimate_bracket combos, 'fast' from is_fast)."""
    two = [c for c in combos if c['two_card']]
    four = [f'{len(gcs)} Game Changers'] if len(gcs) > OFFICIAL_MAX_GC else []
    four += _shared(flags) + [f'fast two-card combo: {_cards(c)}' for c in two if c['fast']]
    if four:
        return 4, four
    three = [f'{len(gcs)} Game Changer{"s" * (len(gcs) > 1)}'] if gcs else []
    three += [f'late two-card combo: {_cards(c)}' for c in two]
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
