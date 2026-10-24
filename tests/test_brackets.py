import unittest

from mtg import brackets

MV = {'Thassa\'s Oracle': 2, 'Demonic Consultation': 1, 'Big A': 4, 'Big B': 3}.get
NONE = {'mld': [], 'extra-turn': []}


def combo(cards, bracket='Powerful'):
    return {'cards': cards, 'bracket': bracket}


def gcs(n):
    return [f'GC {i}' for i in range(n)]


def two_card(fast):
    return {'cards': ['A', 'B'], 'two_card': True, 'fast': fast}


class FastTest(unittest.TestCase):
    def test_cheap_pieces_are_fast(self):
        self.assertTrue(brackets.is_fast(combo(["Thassa's Oracle", 'Demonic Consultation']), MV))

    def test_seven_mana_powerful_combo_is_not_fast(self):
        self.assertFalse(brackets.is_fast(combo(['Big A', 'Big B']), MV))

    def test_ruthless_is_fast_whatever_it_costs(self):
        self.assertTrue(brackets.is_fast(combo(['Big A', 'Big B'], 'Ruthless'), MV))

    def test_unknown_mana_value_counts_as_fast(self):
        self.assertTrue(brackets.is_fast(combo(['Big A', 'Mystery Card']), MV))
        self.assertIsNone(brackets.total_mv(combo(['Big A', 'Mystery Card']), MV))


class OfficialTest(unittest.TestCase):
    def test_three_game_changers_is_bracket_3(self):
        self.assertEqual(brackets.official(gcs(3), NONE, [])[0], 3)

    def test_four_game_changers_is_bracket_4(self):
        self.assertEqual(brackets.official(gcs(4), NONE, []), (4, ['4 Game Changers']))

    def test_mass_land_denial_is_bracket_4(self):
        self.assertEqual(brackets.official([], {**NONE, 'mld': ['Armageddon']}, [])[0], 4)

    def test_fast_two_card_combo_is_bracket_4_late_one_bracket_3(self):
        self.assertEqual(brackets.official([], NONE, [two_card(True)])[0], 4)
        self.assertEqual(brackets.official([], NONE, [two_card(False)])[0], 3)

    def test_one_extra_turn_card_is_not_a_chain(self):
        self.assertEqual(brackets.official([], {**NONE, 'extra-turn': ['Time Warp']}, [])[0], 2)


class HouseTest(unittest.TestCase):
    def test_four_game_changers_pass_at_max_4(self):
        self.assertEqual(brackets.house(gcs(4), NONE, [], 4), (True, []))
        self.assertFalse(brackets.house(gcs(5), NONE, [], 4)[0])

    def test_mass_land_denial_fails(self):
        self.assertFalse(brackets.house([], {**NONE, 'mld': ['Armageddon']}, [], 4)[0])

    def test_two_extra_turn_cards_fail(self):
        self.assertFalse(brackets.house([], {**NONE, 'extra-turn': ['Time Warp', 'Temporal Mastery']}, [], 4)[0])

    def test_fast_infinite_combo_fails_but_fast_finite_does_not(self):
        c = {'cards': ['A', 'B'], 'fast': True, 'infinite': True, 'url': 'u'}
        self.assertFalse(brackets.house([], NONE, [c], 4)[0])
        self.assertTrue(brackets.house([], NONE, [{**c, 'infinite': False}], 4)[0])


class FlagsTest(unittest.TestCase):
    def test_spellbook_flags_win_over_patterns(self):
        classified = {'Armageddon': frozenset({'mld'}), 'Winter Orb': frozenset(), 'Time Warp': frozenset({'extra-turn'})}
        sb = [{'name': 'Armageddon', 'mass_land_denial': False, 'extra_turn': False},
              {'name': 'Winter Orb', 'mass_land_denial': True, 'extra_turn': False}]
        self.assertEqual(brackets.flags(classified, sb), {'mld': ['Winter Orb'], 'extra-turn': ['Time Warp']})


class LineTest(unittest.TestCase):
    def test_line_shows_all_three_labels(self):
        sb = {'tag': 'R', 'name': 'Ruthless'}
        self.assertEqual(brackets.line((4, ['4 Game Changers']), sb, (True, [])),
                         'bracket: Official B4 (4 Game Changers) · Spellbook R (Ruthless) · House 3.75 ✓')
        self.assertIn('Spellbook unavailable', brackets.line((2, ['x']), 'unavailable', (False, ['y'])))


if __name__ == '__main__':
    unittest.main()
