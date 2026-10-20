#!/usr/bin/env python3
"""Validate and price decklists.

    scripts/check_decks.py decks/ravnica/power/*.txt
    scripts/check_decks.py --pool cache/pool.json --owned decks/ravnica/spare_cards.json \\
        --proxy-at 1 --lists out/ decks/ravnica/extra/*.txt

Checks: 60 cards, max 4 copies of non-basics, colors within the header's colors, and (with --pool)
that every card is in the card pool. Prices each card at its cheapest printing on Scryfall, cached in
cache/prices.json (delete it to re-price).

--owned  JSON {card name: qty} of spare cards; they're used before buying, allocated across decks
         in the order given so two decks never claim the same physical copy.
--proxy-at N  split purchases: cards priced >= $N go on the proxy list, the rest on the buy list.
--lists DIR   write buy.txt and proxy.txt there.
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import decklist, scryfall

PRICES = os.path.join(os.path.dirname(__file__), '..', 'cache', 'prices.json')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--pool')
    ap.add_argument('--owned')
    ap.add_argument('--proxy-at', type=float)
    ap.add_argument('--lists')
    a = ap.parse_args()

    pool = {}
    if a.pool:
        for c in json.load(open(a.pool)):
            pool[c['name']] = c
            pool.setdefault(c['name'].split(' // ')[0], c)
    owned = Counter(json.load(open(a.owned))) if a.owned else Counter()
    prices = json.load(open(PRICES)) if os.path.exists(PRICES) else {}

    def price(name):
        if prices.get(name) is None:
            prices[name] = scryfall.cheapest_usd(name)
        return prices[name] or 0.0

    buy, proxy, grand = Counter(), Counter(), 0.0
    for path in a.decks:
        name, colors, cards = decklist.parse(path)
        problems, cost = [], 0.0
        for card, q in cards.items():
            c = pool.get(card) if pool else None
            if pool and not c:
                problems.append(f'not in pool: {card}')
            if c and colors and not set(c.get('color_identity', [])) <= set(colors):
                problems.append(f'off-color: {card}')
            if card not in decklist.BASICS and q > 4:
                problems.append(f'more than 4: {card}')
            need = q - min(q, owned[card])
            owned[card] -= q - need
            if need and card not in decklist.BASICS:
                p = price(card)
                cost += p * need
                (proxy if a.proxy_at is not None and p >= a.proxy_at else buy)[card] += need
        total = sum(cards.values())
        if total != 60:
            problems.append(f'{total} cards')
        grand += cost
        print(f'{name:34} {total} cards  to acquire ${cost:7.2f}' + ''.join(f'\n   !! {p}' for p in problems))
    json.dump(prices, open(PRICES, 'w'))

    buy_cost = sum(price(k) * q for k, q in buy.items())
    print(f'\nTotal ${grand:.2f}  (buy {sum(buy.values())} cards ${buy_cost:.2f}'
          + (f' | proxy {sum(proxy.values())} cards, worth ${grand - buy_cost:.2f} real)' if a.proxy_at is not None else ')'))
    if a.lists:
        os.makedirs(a.lists, exist_ok=True)
        for fname, items in (('buy.txt', buy), ('proxy.txt', proxy)):
            with open(os.path.join(a.lists, fname), 'w') as f:
                for k, q in sorted(items.items()):
                    f.write(f'{q} {k}\n')


if __name__ == '__main__':
    main()
