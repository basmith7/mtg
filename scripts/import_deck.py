#!/usr/bin/env python3
"""Turn a deck link into a deck.txt (format: mtg/decklist.py).

    scripts/import_deck.py https://moxfield.com/decks/t9G16DLc5EO0uYOuDftBIQ -o decks/commander/hogs.txt
    scripts/import_deck.py https://archidekt.com/decks/27270377 --name "Ruric Thar"
    scripts/import_deck.py https://www.mtggoldfish.com/deck/7978067
    scripts/import_deck.py my_list.txt            # or a URL to a plain text list
    scripts/import_deck.py https://www.instagram.com/reel/Dd67dxZkSQF/ [--bio-link https://linktr.ee/x]

Prints the deck to stdout, or writes it with -o. The summary goes to stderr. Colours come from the
commanders' colour identity (Scryfall), or from all cards for non-Commander lists. Instagram needs
yt-dlp in .venv/ (python3 -m venv .venv && .venv/bin/pip install yt-dlp) and is best effort: when it
can't tell which deck the post is about it lists candidates and stops.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import importdeck, scryfall


def colors(deck):
    data = scryfall.collection(deck.commanders or deck.cards)
    ident = set().union(*(data[c]['color_identity'] for c in (deck.commanders or deck.cards) if c in data))
    return ''.join(c for c in 'WUBRG' if c in ident)


def render(deck, cols):
    lines = [f'# {deck.name} | {cols}']
    if deck.source:
        lines.append(f'# source: {deck.source}')
    lines += [f'Commander: {c}' for c in deck.commanders]
    lines += [f'{q} {c}' for c, q in sorted(deck.cards.items())]
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('source', help='Moxfield/Archidekt/MTGGoldfish/Instagram URL, text-list URL, or file path')
    ap.add_argument('-o', '--out', help='write the deck here (default: stdout)')
    ap.add_argument('--name', help='deck name for the header (default: the source deck name)')
    ap.add_argument('--bio-link', help='Instagram only: the account\'s link-in-bio page (Linktree etc.)')
    a = ap.parse_args()
    try:
        deck = importdeck.load(a.source, a.bio_link)
    except importdeck.Unsure as e:
        sys.exit(f'import_deck: {e}')
    if a.name:
        deck.name = a.name
    deck.name = deck.name.replace('|', '-').strip()  # '|' separates the colours in the header
    cols = colors(deck)
    total = sum(deck.cards.values())
    print(f'source: {deck.source}\ndeck: {deck.name} | {cols or "colourless"} | {total} cards, '
          f'{len(deck.cards)} unique | commanders: {", ".join(deck.commanders) or "none"}', file=sys.stderr)
    for n in deck.notes:
        print('note:', n, file=sys.stderr)
    if deck.commanders and total != 100:
        print(f'warning: Commander list has {total} cards, not 100', file=sys.stderr)
    text = render(deck, cols)
    if a.out:
        with open(a.out, 'w') as f:
            f.write(text)
        print('wrote', a.out, file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
