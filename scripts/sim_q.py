#!/usr/bin/env python3
"""Goldfish Monte Carlo for the Q, Stacking the Deck list: how often Q triggers, how many copies it casts,
and how fast the backup combos land.

Deck-specific: card roles below are hand-coded for decks/commander/q.txt. Generic mana only
(colours ignored), no opponents' interaction, Q never dies. Q's exiled cards ("the pool") can be
copied by exiling a spare hand card; each turn the leftover mana and spare cards are spent on copies
("cashing in"): mana makers first, a wheel when the hand is empty, then the priciest affordable card.

    scripts/sim_q.py decks/commander/q.txt [--games N] [--no-q] [--blank "Card Name" ...]
"""
import argparse
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import decklist, scryfall

Q = 'Q, Stacking the Deck'
ROCKS = {'Sol Ring': 2, 'Arcane Signet': 1, 'Mind Stone': 1, 'Thought Vessel': 1,
         'Thran Dynamo': 3}
MEDALLION = 'Ruby Medallion'
WHEELS = {'Wheel of Fortune', 'Reforge the Soul', 'Magus of the Wheel'}
ONE_SHOTS = ['Twinflame', 'Heat Shimmer', 'Electroduplicate']  # copy target creature (Q) once
ENGINES = ["Conjurer's Closet", 'Splinter Twin', 'Helm of the Host', 'Panharmonicon', 'Molten Echoes',
           'Flameshadow Conjuring', 'Mirror March']
BIRGI, KILN = 'Birgi, God of Storytelling // Harnfel, Horn of Bounty', 'Storm-Kiln Artist'
DEPLOY = ['Combat Celebrant', 'Fable of the Mirror-Breaker // Reflection of Kiki-Jiki', BIRGI, KILN, 'Guttersnipe']
EQUIP_HELM = 5
RITUALS = {'Seething Song': lambda g: 5, "Jeska's Will": lambda g: 4,  # assumes 4 cards in an opponent's hand
           "Brass's Bounty": lambda g: g.lands}
KEEP = set(ENGINES + ONE_SHOTS + DEPLOY) | WHEELS | {'Dualcaster Mage', MEDALLION}  # never exiled as fodder
BIG_TURN = 15  # copies in one turn that we call "went off"


def combos(st):
    """(label, slots, extra mana, ok) where slots are tuples of alternative card names."""
    sn, cel = st['bf_since'], 'Combat Celebrant'
    creature_out = st['q_out'] or any(st['bf'][c] for c in st['creatures'])
    return [
        ('combat', [(cel,), ('Helm of the Host',)], EQUIP_HELM, True),
        ('combat', [(cel,), ('Splinter Twin',)], 0, sn.get(cel, 99) < st['t']),
        ('combat', [(cel,)], 0, st['fable_turn'] <= st['t'] - 2),
        ('dualcaster', [('Dualcaster Mage',), ('Heat Shimmer',)], 0, st['t'] >= 3 or creature_out),
        ('dualcaster', [('Dualcaster Mage',), ('Twinflame', 'Electroduplicate')], 0, creature_out),
    ]


class Game:
    def __init__(self, cards, data, rng, use_q):
        self.data, self.rng, self.use_q = data, rng, use_q
        lib = [c for c in cards if c != Q]
        n = 0
        while True:
            rng.shuffle(lib)
            hand = lib[:7]
            lands = sum(self.land(c) for c in hand)
            if 2 <= lands <= 5 or n >= 3:
                break
            n += 1
        self.hand, self.lib = hand, lib[7:]
        for _ in range(n):  # London mulligan: bottom lands if flooded, else priciest spell
            ls = [c for c in self.hand if self.land(c)]
            sp = [c for c in self.hand if not self.land(c)]
            drop = ls[0] if len(ls) > 3 or not sp else max(sp, key=self.mv)
            self.hand.remove(drop)
            self.lib.append(drop)
        self.st = {'bf': Counter(), 'bf_since': {}, 'q_out': False, 'fable_turn': 99, 't': 0,
                   'creatures': {c for c in data if 'Creature' in data[c]['type_line']}}
        self.pool, self.lands, self.rock_mana, self.mana = [], 0, 0, 0
        self.q_turn, self.triggers, self.win, self.copies, self.best_turn = None, 0, None, 0, 0
        self.q_on = {'Splinter Twin': False, 'Helm of the Host': False}
        self.electro_fb = False

    def land(self, c):
        return c in self.data and 'Land' in self.data[c]['type_line'].split('//')[0]

    def mv(self, c):
        return int(self.data[c]['cmc']) if c in self.data else 0

    def cost(self, c):
        red = 'R' in (self.data[c].get('colors') or self.data[c].get('card_faces', [{}])[0].get('colors') or [])
        return max(1, self.mv(c) - 1) if red and self.st['bf'][MEDALLION] else self.mv(c)

    def fodder(self, exclude=()):
        """Hand cards that can be exiled to Q's pool ability: lands first, then anything not reserved."""
        rest = list(self.hand)
        for c in exclude:
            if c in rest:
                rest.remove(c)
        return sorted(rest, key=lambda c: (not self.land(c), self.mv(c)))

    def pay_pool(self, n, exclude=()):
        for c in self.fodder(exclude)[:n]:
            self.hand.remove(c)

    def put(self, c):
        self.st['bf'][c] += 1
        self.st['bf_since'].setdefault(c, self.st['t'])
        if c in ROCKS:
            self.rock_mana += ROCKS[c]
            self.mana += ROCKS[c]
        if c.startswith('Fable'):
            self.st['fable_turn'] = min(self.st['fable_turn'], self.st['t'])

    def source(self, c):
        """Cheapest way to get card c this turn: ('bf', 0), ('hand', cost), ('pool', cost) or None."""
        if self.st['bf'][c]:
            return 'bf', 0
        if c in self.hand:
            return 'hand', self.cost(c)
        if c in self.pool:
            return 'pool', self.cost(c)
        return None

    def try_cast(self, c, allow_pool=True, keep=()):
        """Cast permanent c from hand or Q's pool if affordable. Returns True on success."""
        src = self.source(c)
        if not src or src[0] == 'bf' or (src[0] == 'pool' and not allow_pool) or src[1] > self.mana:
            return False
        if src[0] == 'pool' and not self.fodder(keep):
            return False
        self.mana -= src[1]
        if src[0] == 'hand':
            self.hand.remove(c)
        else:
            self.pay_pool(1, keep)
        return True

    def check_combo(self):
        if self.win:
            return False
        for label, slots, extra, ok in combos(self.st):
            if not ok:
                continue
            need, pieces, pool_uses = extra, [], 0
            for alts in slots:
                best = None
                for c in alts:
                    s = self.source(c)
                    if s and (best is None or (s[0] == 'pool', s[1]) < (best[1][0] == 'pool', best[1][1])):
                        best = (c, s)
                if best is None:
                    break
                c, (where, cost) = best
                need += cost
                if where == 'hand':
                    pieces.append(c)
                pool_uses += where == 'pool'
            else:
                if need <= self.mana and len(self.fodder(pieces)) >= pool_uses:
                    self.win = (self.st['t'], label)
                    return True
        return False

    def q_enters(self, nontoken):
        bf = self.st['bf']
        n = 1
        if nontoken:
            n += bf['Molten Echoes'] + bf['Flameshadow Conjuring']
            for _ in range(bf['Mirror March']):
                while self.rng.random() < 0.5:
                    n += 1
        n *= 2 if bf['Panharmonicon'] else 1
        for _ in range(n):
            self.triggers += 1
            self.rng.shuffle(self.lib)
            while self.lib:
                c = self.lib.pop(0)
                if not self.land(c):
                    self.pool.append(c)
                    break

    def draw(self, n=1):
        for _ in range(n):
            if self.lib:
                self.hand.append(self.lib.pop(0))

    def turn(self, t):
        self.st['t'] = t
        if t > 1:
            self.draw()
        land = next((c for c in self.hand if self.land(c)), None)
        if land:
            self.hand.remove(land)
            self.lands += 1
        self.mana = self.lands + self.rock_mana
        if 'Sol Ring' in self.hand:
            self.try_cast('Sol Ring') and self.put('Sol Ring')
        q_cost = 4
        for c in sorted((c for c in self.hand if c in ROCKS), key=self.mv):
            if self.st['q_out'] or not self.use_q or self.mana - self.mv(c) + ROCKS[c] >= q_cost or self.mana < q_cost:
                self.try_cast(c) and self.put(c)
        self.check_combo()
        if self.use_q and not self.st['q_out'] and self.mana >= q_cost:
            self.mana -= q_cost
            self.st['q_out'], self.q_turn = True, t
            self.st['bf_since'][Q] = t
            self.q_enters(True)
            self.check_combo()
        # copy rocks out of Q's pool with spare lands
        for c in [c for c in self.pool if c in ROCKS]:
            while any(self.land(h) for h in self.hand) and self.cost(c) <= self.mana and ROCKS[c] >= self.cost(c):
                self.pay_pool(1)
                self.mana -= self.cost(c)
                self.put(c)
        if not self.st['q_out']:
            return self.develop()
        q_unsick = self.st['bf_since'][Q] < t
        holds_twin = bool(self.source('Combat Celebrant'))
        for c in ENGINES:
            if self.st['bf'][c] and c not in self.q_on:
                continue
            if c == 'Splinter Twin':
                if not self.q_on[c] and not holds_twin and self.try_cast(c):
                    self.q_on[c] = True
                if self.q_on[c] and q_unsick:
                    self.q_enters(False)
            elif c == 'Helm of the Host':
                if not self.q_on[c] and (self.st['bf'][c] or self.cost(c) + EQUIP_HELM <= self.mana) \
                        and 'Combat Celebrant' not in self.hand:
                    if self.st['bf'][c] or self.try_cast(c):
                        self.st['bf'][c] = 1
                        if self.mana >= EQUIP_HELM:
                            self.mana -= EQUIP_HELM
                            self.q_on[c] = True
                if self.q_on[c]:
                    self.q_enters(False)
            elif self.try_cast(c):
                self.put(c)
        hold = 1 if self.source('Dualcaster Mage') else 0
        for c in ONE_SHOTS:
            if c in self.hand and sum(o in self.hand for o in ONE_SHOTS) > hold and self.try_cast(c, allow_pool=False):
                self.q_enters(False)
                if c == 'Electroduplicate':
                    self.electro_fb = True
        if self.electro_fb and self.mana >= 4 and not hold:
            self.mana -= 4
            self.electro_fb = False
            self.q_enters(False)
        self.develop()
        self.check_combo()
        self.cash_in()
        if self.st['bf']["Conjurer's Closet"]:
            self.q_enters(True)

    def cash_in(self):
        """Spend leftover mana and spare hand cards on copies of pool cards."""
        n = 0
        while n < 40:
            spare = [c for c in self.fodder() if self.land(c) or c not in KEEP]
            opts = [c for c in set(self.pool) if self.cost(c) <= self.mana]
            if not spare or not opts:
                break
            ramp = [c for c in opts if c in RITUALS and RITUALS[c](self) > self.cost(c)
                    or c in ROCKS and ROCKS[c] >= self.cost(c)]
            wheels = [c for c in opts if c in WHEELS] if len(spare) <= 1 and len(self.lib) >= 10 else []
            if ramp:
                c = ramp[0]
            elif wheels:
                c = wheels[0]
            else:
                c = max(opts, key=lambda c: (c not in RITUALS, self.mv(c)))
                if c in RITUALS:
                    break  # a mana-negative ritual isn't worth a card
            self.hand.remove(spare[0])
            self.mana -= self.cost(c)
            n += 1
            self.mana += self.st['bf'][BIRGI]
            if self.st['bf'][KILN] and self.data[c]['type_line'].split(' //')[0] in ('Instant', 'Sorcery'):
                self.mana += 1
            if c in RITUALS:
                self.mana += RITUALS[c](self)
            elif c in WHEELS:
                self.hand = []
                self.draw(7)
            elif c in ONE_SHOTS:
                self.q_enters(False)
            elif any(t in self.data[c]['type_line'] for t in ('Artifact', 'Creature', 'Enchantment')):
                self.put(c)
        self.copies += n
        self.best_turn = max(self.best_turn, n)

    def develop(self):
        for c in sorted(DEPLOY + [MEDALLION], key=self.mv):
            if not self.st['bf'][c] and self.try_cast(c, allow_pool=False):
                self.put(c)
        if len(self.hand) <= 2:
            for c in WHEELS:
                if self.try_cast(c):
                    self.lib.extend(self.hand)
                    self.hand = []
                    self.draw(7)
                    if c == 'Magus of the Wheel':
                        self.put(c)
                    break


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('deck')
    ap.add_argument('--games', type=int, default=20000)
    ap.add_argument('--turns', type=int, default=10)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--no-q', action='store_true', help='never cast Q (baseline)')
    ap.add_argument('--blank', action='append', default=[], help='replace this card with a vanilla spell')
    a = ap.parse_args()
    _, _, counts = decklist.parse(a.deck)
    cards = [c for c, n in counts.items() for _ in range(n)]
    data = scryfall.collection(sorted(set(cards) - {Q}))
    for b in a.blank:
        cards[cards.index(b)] = f'(blank {b})'
        data[f'(blank {b})'] = {'cmc': 3, 'type_line': 'Sorcery', 'colors': ['R']}
    rng = random.Random(a.seed)
    T = a.turns
    trig = [[0] * a.games for _ in range(T + 1)]
    copies = [[0] * a.games for _ in range(T + 1)]
    best, q_by, win_by, how = [], Counter(), Counter(), Counter()
    for g in range(a.games):
        game = Game(cards, data, rng, not a.no_q)
        for t in range(1, T + 1):
            game.turn(t)
            trig[t][g], copies[t][g] = game.triggers, game.copies
        best.append(game.best_turn)
        if game.q_turn:
            q_by[game.q_turn] += 1
        if game.win:
            win_by[game.win[0]] += 1
            how[game.win[1]] += 1
    G = a.games
    print(f'{G} goldfish games, {T} turns, draw from T2, no interaction, Q never dies'
          + (' (Q never cast)' if a.no_q else ''))
    print(' turn   Q out   Q triggers  >=2 trig  >=4 trig   copies cast  >=5 copies   combo won')
    q_cum = win_cum = 0
    for t in range(1, T + 1):
        q_cum += q_by[t]
        win_cum += win_by[t]
        tr, cp = trig[t], copies[t]
        print(f'  T{t:<3} {q_cum / G:6.1%}   {sum(tr) / G:8.2f}    {sum(x >= 2 for x in tr) / G:6.1%}    '
              f'{sum(x >= 4 for x in tr) / G:6.1%}    {sum(cp) / G:8.2f}     {sum(x >= 5 for x in cp) / G:6.1%}'
              f'     {win_cum / G:6.1%}')
    print(f'biggest single turn of copies by T{T}: mean {sum(best) / G:.1f}; '
          + ', '.join(f'>={k}: {sum(b >= k for b in best) / G:.0%}' for k in (3, 5, 8, BIG_TURN)))
    total = sum(how.values())
    if total:
        print('combo routes (share of wins): ' + ', '.join(f'{k} {v / total:.0%}' for k, v in how.most_common()))


if __name__ == '__main__':
    main()
