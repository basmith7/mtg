"""Decklist text files.

Format: an optional header line '# Deck Name | COLORS' (e.g. '# Boros Legion | RW'), then
'4 Card Name' lines. Later '# key: value' lines are metadata: '# source:' is the deck's Archidekt URL and
'# updated:' the site version the list was last pulled from or pushed as. Commander decks add
'Commander: Card Name' lines; the commander is also listed as '1 Card Name' so the count is 100.
Other lines are ignored.
"""
import os
from collections import Counter

BASICS = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest'}


def parse(path):
    """Return (name, colors, Counter{card: qty})."""
    name, colors, cards = os.path.splitext(os.path.basename(path))[0], '', Counter()
    seen = False  # only the first line may be a header; later '#' lines are comments
    for line in open(path):
        line = line.strip()
        if line.startswith('#') and not seen:
            head = line.lstrip('# ').split('|')
            name = head[0].strip()
            colors = head[1].strip() if len(head) > 1 else ''
        if line:
            seen = True
        if line.startswith('#'):
            continue
        if line and line[0].isdigit():
            qty, card = line.split(' ', 1)
            cards[card.strip()] += int(qty)
    return name, colors, cards


def commanders(path):
    """Names from the file's 'Commander: Card Name' lines."""
    return [line.split(':', 1)[1].strip() for line in map(str.strip, open(path)) if line.lower().startswith('commander:')]


def meta(path, key):
    """The value on the file's '# key: value' line, if any."""
    for line in map(str.strip, open(path)):
        if line.lower().startswith(f'# {key}:'):
            return line.split(':', 1)[1].strip()


def set_meta(path, key, value):
    """Write a '# key: value' line, replacing the old one or adding it after the header."""
    lines = open(path).read().split('\n')
    new = f'# {key}: {value}'
    at = next((i for i, l in enumerate(lines) if l.strip().lower().startswith(f'# {key}:')), None)
    if at is None:
        lines.insert(1 if lines[0].startswith('#') else 0, new)
    else:
        lines[at] = new
    with open(path, 'w') as f:
        f.write('\n'.join(lines))


def render(name, colors, commanders, cards, source=None, updated=None):
    """The decklist text for parse() to read back: header, metadata, Commander lines, cards."""
    lines = [f'# {name} | {colors}']
    lines += [f'# {k}: {v}' for k, v in (('source', source), ('updated', updated)) if v]
    lines += [f'Commander: {c}' for c in commanders]
    lines += [f'{q} {c}' for c, q in sorted(cards.items())]
    return '\n'.join(lines) + '\n'
