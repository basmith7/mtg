"""Mana maths and a goldfish simulation for a decklist (pure: no network).

    from mtg import goldfish
    lib = [goldfish.Card('land', 0, 1, frozenset('R'), {}), ...]   # the 99-card library
    goldfish.simulate(lib, goldfish.Cost(5, {'B': 1, 'R': 2}), games, random.Random(1))
    goldfish.sources_needed(pips=2, mv=3)
"""
import re
from collections import Counter, namedtuple
from functools import lru_cache
from itertools import combinations
from math import comb

# One library entry. kind: land, rock, dork, lramp, other. amount: mana it adds once online.
# produces: colours it adds (WUBRG, C for colourless). pips: {colour: count} in its cost.
Card = namedtuple('Card', 'kind mv amount produces pips')
Cost = namedtuple('Cost', 'mv pips')

DECK, HAND, LANDS = 99, 7, 41  # LANDS: Karsten's assumed 99-card land count (mana rocks as partial lands)
TURNS = 12


def faces(c):
    return c.get('card_faces') or [c]


def is_land(c):
    return 'Land' in c['type_line'].split('//')[0]


def mana_producer(c):
    """Nonland artifact/creature that taps for mana: returns (colours, amount, immediate) or None."""
    f = faces(c)[0]
    tl, txt = f.get('type_line', c['type_line']), f.get('oracle_text', '')
    if is_land(c) or not c.get('produced_mana') or not re.search(r'\bAdd\b', txt):
        return None
    if 'Artifact' not in tl and 'Creature' not in tl:
        return None
    if re.search(r'(Sacrifice|Exile)[^.\n]*: Add|Add[^.\n]*\. (Sacrifice|Exile)', txt):
        return None  # one-shot or sacrifice-outlet mana (Lotus Petal, Spirit Guides, Ashnod's Altar)
    amount = 2 if re.search(r'Add \{[WUBRGC]\}\{[WUBRGC]\}', txt) else 1
    return set(c['produced_mana']), amount, 'Artifact' in tl and 'Creature' not in tl


def pips(c):
    cost = faces(c)[0].get('mana_cost') or c.get('mana_cost', '')
    return Counter(re.findall(r'\{([WUBRG])\}', cost))


# -- Source counts ------------------------------------------------------------------------------------

def p_on_curve(sources, p, mv, lands=LANDS):
    """P(>= p coloured sources among the cards seen by turn mv | >= mv lands seen). 99-card deck, 7-card
    hand, a draw every turn including the first (multiplayer), no mulligans: a hypergeometric."""
    n, other = HAND + mv, lands - sources
    hit = enough = 0
    for k in range(min(sources, n) + 1):
        for j in range(min(other, n - k) + 1):
            if k + j < mv:
                continue
            w = comb(sources, k) * comb(other, j) * comb(DECK - lands, n - k - j)
            enough += w
            hit += w if k >= p else 0
    return hit / enough if enough else 0.0


@lru_cache(maxsize=None)
def sources_needed(pips, mv, lands=LANDS):
    """Fewest coloured sources for `pips` symbols of one colour on a spell of MV `mv` to be castable on
    turn mv with probability >= 89 + mv percent (Karsten's per-MV consistency target), conditional on
    having drawn mv lands. Computed here by `p_on_curve` (no mulligans), not copied from Karsten; his
    published 99-card table, which also models mulligans, is compared in specs/deck-tools/slices/06-goldfish.md.
    Returns None when even an all-source mana base misses the target."""
    mv, target = max(mv, pips, 1), (89 + min(max(mv, pips, 1), 7)) / 100
    for s in range(pips, lands + 1):
        if p_on_curve(s, pips, mv, lands) >= target:
            return s
    return None


# -- Goldfish -----------------------------------------------------------------------------------------

def can_pay(cost, sources):
    """cost: Cost; sources: list of colour sets, one per mana. Hall's condition: every set of the
    cost's colours has at least as many sources that make one of them as it has pips."""
    if len(sources) < cost.mv:
        return False
    cols = [c for c, n in cost.pips.items() if n]
    for r in range(1, len(cols) + 1):
        for sub in combinations(cols, r):
            if sum(1 for s in sources if s & set(sub)) < sum(cost.pips[c] for c in sub):
                return False
    return True


def pay(cost, sources):
    """Remove the mana spent on cost from sources (caller checked can_pay). Each pip takes the least
    flexible source that still leaves the rest of the cost payable; generic takes the least flexible rest."""
    pool, left = sorted(sources, key=len), Counter(cost.pips)
    for col in list(left.elements()):
        left[col] -= 1
        rest = Cost(sum(left.values()), left)
        pick = next((i for i, s in enumerate(pool) if col in s and can_pay(rest, pool[:i] + pool[i + 1:])),
                    None)
        pool.pop(pick)
    for _ in range(cost.mv - sum(cost.pips.values())):
        pool.pop(0)
    return pool


def keepable(hand):
    """2-5 lands, and either 3+ lands or a spell of MV <= 2 the hand's lands can pay for."""
    lands = [c.produces for c in hand if c.kind == 'land']
    if not 2 <= len(lands) <= 5:
        return False
    return len(lands) >= 3 or any(c.kind != 'land' and c.mv <= 2 and can_pay(Cost(c.mv, c.pips), lands)
                                  for c in hand)


def simulate(deck, commander, games, rng):
    """deck: list of Card for the library; commander: Cost or None.
    Model: London mulligan to 4 (keepable() decides), a draw every turn, one land per turn (the first in
    hand), then ramp cheapest first with the coloured mana available. Rocks work the turn they land, dorks
    and land-ramp the turn after; land-ramp fetches a land making one of the colours already out. The
    commander is cast as soon as it can be; it is then removed the same turn, and recast at MV + 2.
    Returns {keep7, cast_by, recast_by, mulls, lands4, drops4, ramp2}; cast_by[t] / recast_by[t] are the
    share of games with a cast by turn t (t = 1..TURNS)."""
    cast, recast, keep7, lands4, drops4, ramp2, mulls = Counter(), Counter(), 0, 0, 0, 0, Counter()
    for _ in range(games):
        lib = deck[:]
        rng.shuffle(lib)
        n = 0
        while not keepable(lib[:7]) and n < 3:
            rng.shuffle(lib)
            n += 1
        hand, rest = lib[:7], lib[7:]
        for _ in range(n):  # bottom n: a land if flooded (or nothing else), else the priciest spell
            ls = [c for c in hand if c.kind == 'land']
            spells = [c for c in hand if c.kind != 'land']
            drop = ls[0] if len(ls) > 3 or not spells else max(spells, key=lambda c: c.mv)
            hand.remove(drop)
            rest.append(drop)
        mulls[n] += 1
        keep7 += n == 0
        board, pending, first, second, drops, ramp_cast = [], [], None, None, 0, False
        for t in range(1, TURNS + 1):
            board += pending
            pending = []
            hand.append(rest.pop(0))
            if t == 4:
                lands4 += sum(c.kind == 'land' for c in hand) + drops
            land = next((c for c in hand if c.kind == 'land'), None)
            if land:
                hand.remove(land)
                board.append(land.produces)
                drops += t <= 4
            mana = board[:]
            while True:
                if commander and first is None and can_pay(commander, mana):
                    first, mana = t, None
                    break
                if commander and first is not None and first < t and second is None:
                    taxed = Cost(commander.mv + 2, commander.pips)
                    if can_pay(taxed, mana):
                        second = t
                        mana = pay(taxed, mana)
                opts = sorted((c for c in hand if c.kind in ('rock', 'dork', 'lramp')
                               and can_pay(Cost(c.mv, c.pips), mana)), key=lambda c: c.mv)
                if not opts:
                    break
                c = opts[0]
                hand.remove(c)
                mana = pay(Cost(c.mv, c.pips), mana)
                ramp_cast |= t <= 2
                made = [c.produces] * c.amount
                if c.kind == 'lramp':
                    made = [frozenset().union(*board) or frozenset('C')]
                if c.kind == 'rock':
                    board += made
                    mana += made
                else:
                    pending += made
        drops4 += drops == 4
        ramp2 += ramp_cast
        if first:
            cast[first] += 1
        if second:
            recast[second] += 1
    upto = lambda ctr: {t: sum(ctr[x] for x in range(1, t + 1)) / games for t in range(1, TURNS + 1)}
    return {'keep7': keep7 / games, 'cast_by': upto(cast), 'recast_by': upto(recast), 'mulls': mulls,
            'lands4': lands4 / games, 'drops4': drops4 / games, 'ramp2': ramp2 / games}
