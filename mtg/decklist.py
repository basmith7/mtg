"""Decklist text files.

Format: an optional header line '# Deck Name | COLORS' (e.g. '# Boros Legion | RW'), then
'4 Card Name' lines; later '#' lines (e.g. '# source: <url>') are comments. Commander decks add
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
