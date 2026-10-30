import unittest
from unittest import mock

from mtg import printings, scryfall


def printing(name='Counterspell', id='x', released='2020-01-01', **kw):
    """A Scryfall printing: a plain modern-frame English card unless kw says otherwise."""
    return {'name': name, 'id': id, 'released_at': released, 'lang': 'en', 'set': 'abc', 'set_name': 'Some Set',
            'set_type': 'expansion', 'frame': '2015', 'border_color': 'black', 'type_line': 'Instant', **kw}


def best(*cards, names=('Counterspell',)):
    with mock.patch.object(scryfall, 'search', return_value=iter(cards)):
        return printings.best(list(names))


class BestTest(unittest.TestCase):
    def test_styles_rank_fanciest_readable_first(self):
        styles = [  # best first, per the player's picks
            printing(id='extended', frame_effects=['extendedart']),
            printing(id='borderless-showcase', border_color='borderless', frame_effects=['showcase']),
            printing(id='etched', frame_effects=['etched']),
            printing(id='inverted', frame_effects=['inverted']),
            printing(id='retro', frame='1997'),
            printing(id='2003', frame='2003'),
            printing(id='regular'),
        ]
        for i in range(len(styles) - 1):  # each beats every style below it
            for worse in styles[i + 1:]:
                self.assertEqual(best(worse, styles[i]), {'Counterspell': [styles[i]['id'], worse['id']]})

    def test_hard_to_read_and_universes_beyond_printings_are_never_picked(self):
        blocked = [
            printing(id='ub', promo_types=['universesbeyond']),
            printing(id='star-trek', set='trc'),
            printing(id='secret-lair', set_name='Secret Lair Drop'),
            printing(id='plain-borderless', border_color='borderless'),
            printing(id='full-art', full_art=True),
            printing(id='future', frame='future'),
            printing(id='textless', textless=True),
            printing(id='japanese', lang='ja'),
            printing(id='joke', set_type='funny'),
        ]
        self.assertEqual(best(*blocked, printing(id='regular')), {'Counterspell': ['regular']})
        self.assertEqual(best(*blocked), {})

    def test_lands_may_be_plain_borderless_or_full_art(self):
        land = dict(name='Island', type_line='Basic Land — Island')
        got = best(printing(id='regular', **land), printing(id='full-art', full_art=True, **land),
                   names=['Island'])
        self.assertEqual(got['Island'][0], 'full-art')

    def test_newest_printing_wins_within_a_style_and_only_a_few_are_kept(self):
        got = best(*[printing(id=f'y{y}', released=f'{y}-01-01') for y in range(2010, 2016)])
        self.assertEqual(got, {'Counterspell': ['y2015', 'y2014', 'y2013']})

    def test_a_card_with_the_name_only_on_its_back_face_is_not_a_printing(self):
        got = best(printing(name='Emeritus of Truce // Swords to Plowshares', id='other', frame_effects=['extendedart']),
                   printing(name='Swords to Plowshares', id='real'), names=['Swords to Plowshares'])
        self.assertEqual(got, {'Swords to Plowshares': ['real']})

    def test_front_face_name_finds_a_double_faced_card(self):
        got = best(printing(name='Fire // Ice', id='fi'), names=['Fire'])
        self.assertEqual(got, {'Fire': ['fi']})


if __name__ == '__main__':
    unittest.main()
