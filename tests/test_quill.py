import glob
import json
import os
import pathlib
import unittest

from mtg import quill

DECKS = os.path.join(os.path.dirname(__file__), '..', 'decks')


def primers():
    """Every deck primer in the local working copy (none in a fresh clone)."""
    out = {p: pathlib.Path(p).read_text() for p in glob.glob(os.path.join(DECKS, '**', '*.md'), recursive=True)
           if not p.endswith(('PLAYLOG.md', 'RULES.md'))}
    return out


class FromDeltaTest(unittest.TestCase):
    def test_round_trip_is_a_fixpoint(self):
        found = primers()
        sample = '## How it wins\nAttack with **big** things.\n\n- [[Sol Ring]] first\n- then **this**\n\nThe end.'
        found['sample'] = sample
        for name, md in found.items():
            with self.subTest(name):
                delta = quill.to_delta(md)
                back, dropped = quill.from_delta(delta)
                self.assertEqual(dropped, [])
                self.assertEqual(quill.to_delta(back), delta)

    def test_sample_reads_back_as_markdown(self):
        md = '## How it wins\nAttack with **big** things.\n\n- a bullet'
        self.assertEqual(quill.from_delta(quill.to_delta(md))[0], md)

    def test_unsupported_formatting_keeps_text(self):
        delta = json.dumps({'ops': [
            {'insert': 'Step', 'attributes': {'italic': True}}, {'insert': '\n', 'attributes': {'list': 'ordered'}},
            {'insert': 'Title'}, {'insert': '\n', 'attributes': {'header': 4}},
            {'insert': 'see '}, {'insert': 'here', 'attributes': {'link': 'https://x', 'bold': True}},
            {'insert': '\n'}, {'insert': {'image': 'x.png'}}]})
        md, dropped = quill.from_delta(delta)
        self.assertEqual(md, '- Step\n## Title\nsee **here**')
        self.assertEqual(dropped, ['embed', 'header:4', 'italic', 'link', 'list:ordered'])

    def test_empty(self):
        self.assertEqual(quill.from_delta(''), ('', []))


if __name__ == '__main__':
    unittest.main()
