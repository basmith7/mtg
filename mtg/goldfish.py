"""Mana maths and a goldfish simulation for a decklist (pure: no network).

    from mtg import goldfish
    goldfish.simulate(library, commander_mv, games, random.Random(1))
"""
import re
from collections import Counter

# Coloured sources wanted in a 99-card deck for {pips} of one colour on a card of MV {mv}.
# Approximate, from memory of Frank Karsten's Commander guidance (about 90% on curve); NOT verified
# against his article. Treat as a rough flag, not a verdict. Index: pips -> list for MV 1,2,3,4,5+.
KARSTEN_99 = {1: [19, 16, 14, 13, 12], 2: [99, 24, 21, 19, 17], 3: [99, 99, 28, 25, 22]}


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


def need(p, mv):
    return KARSTEN_99[min(p, 3)][min(max(mv, 1), 5) - 1]


def simulate(deck, cmc, games, rng):
    """deck: list of (kind, cost, mana) for the 99-card library; kinds: land, rock, dork, lramp, other.
    Model: colours ignored (generic mana only); each turn play a land, then cast ramp cheapest first
    with the mana available. Rocks work the turn they land; dorks and land-ramp the turn after."""
    cast_turn, lands4, ramp2, t4_drops, mulls = [], 0, 0, 0, Counter()
    for _ in range(games):
        lib = deck[:]
        rng.shuffle(lib)
        n = 0
        while True:
            hand, rest = lib[:7], lib[7:]
            nl = sum(c[0] == 'land' for c in hand)
            if 2 <= nl <= 5 or n >= 3:
                break
            lib = lib[:]
            rng.shuffle(lib)
            n += 1
        for _ in range(n):  # London mulligan: bottom n cards, lands first if flooded, else priciest spells
            lands = [c for c in hand if c[0] == 'land']
            spells = [c for c in hand if c[0] != 'land']
            drop = lands[0] if len(lands) > 3 or not spells else max(spells, key=lambda c: c[1])
            hand.remove(drop)
            rest.append(drop)
        mulls[n] += 1
        battlefield_lands, online, pending, done, drops, ramp_cast = 0, 0, 0, None, 0, False
        for t in range(1, 9):
            online += pending
            pending = 0
            hand.append(rest.pop(0))
            if t == 4:
                lands4 += battlefield_lands + sum(c[0] == 'land' for c in hand)
            land = next((c for c in hand if c[0] == 'land'), None)
            if land:
                hand.remove(land)
                battlefield_lands += 1
                drops += t <= 4
            mana = battlefield_lands + online
            while True:
                if cmc is not None and done is None and mana >= cmc:
                    done = t
                    break
                opts = sorted((c for c in hand if c[0] in ('rock', 'dork', 'lramp') and c[1] <= mana), key=lambda c: c[1])
                if not opts:
                    break
                c = opts[0]
                hand.remove(c)
                mana -= c[1]
                if t <= 2:
                    ramp_cast = True
                if c[0] == 'rock':
                    online += c[2]
                    mana += c[2]
                else:
                    pending += c[2]
        t4_drops += drops == 4
        ramp2 += ramp_cast
        cast_turn.append(done or 99)
    return cast_turn, lands4 / games, t4_drops / games, ramp2 / games, mulls
