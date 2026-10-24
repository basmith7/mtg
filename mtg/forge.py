"""Forge (Card-Forge/forge) AI-vs-AI pods of our own decks.

Forge is a free Java Magic engine; its desktop jar has a headless `sim` mode
(`SimulateMatch.java`). It lives outside the repo, unpacked under `home()`; see docs/forge.md.
Its AI plays combo and politics badly, so results are a rough read on a deck, never a verdict.
"""
import os
import re
import subprocess
import zipfile
from collections import Counter

from . import config

LABEL = 'Forge AI play: rough; it plays combo and politics badly'
DECK_DIR = os.path.join(config.CACHE, 'forge')
# forge.sh's java flags; Forge 2.0.15 starts on OpenJDK 25 without extra --add-opens.
JAVA_FLAGS = ['-Xmx4096m', '-Dio.netty.tryReflectionSetAccessible=true', '-Dfile.encoding=UTF-8']

_RESULT = re.compile(r'Game Result: Game \d+ ended in (?:a Draw!|\d+ ms\. Ai\(\d+\)-(.+?) has won!)')
_UNSUPPORTED = re.compile(r'An unsupported card was requested: "(.+?)"')


def home():
    """Forge's unpacked release: `FORGE_HOME` or ~/.local/share/forge."""
    return os.environ.get('FORGE_HOME') or os.path.expanduser('~/.local/share/forge')


def deck_name(name):
    """Letters, digits and single spaces: Forge prints it back as `Ai(n)-<name>`."""
    return ' '.join(re.sub(r'[^A-Za-z0-9 ]+', ' ', name).split())


def card_name(card, split):
    """Forge's name for one of our card names. Forge keeps `A // B` only for split cards
    (Fire // Ice); modal, transforming and adventure cards go by their front face."""
    return card if ' // ' not in card or card in split else card.split(' // ')[0]


def to_dck(name, commanders, cards, split=frozenset()):
    """Forge .dck text for a Commander deck. `cards` is a Counter that may include the commanders;
    `split` is the set of split-card names (`split_cards()`)."""
    main = Counter(cards)
    for c in commanders:
        if main[c]:
            main[c] -= 1
    lines = ['[metadata]', f'Name={deck_name(name)}', '[Commander]']
    lines += [f'1 {card_name(c, split)}' for c in commanders]
    lines.append('[Main]')
    lines += [f'{q} {card_name(c, split)}' for c, q in sorted(main.items()) if q > 0]
    return '\n'.join(lines) + '\n'


def split_cards():
    """Names of split cards (`A // B`) in Forge's card database."""
    names = set()
    with zipfile.ZipFile(os.path.join(home(), 'res', 'cardsfolder', 'cardsfolder.zip')) as z:
        for entry in z.namelist():
            text = z.read(entry).decode('utf-8', 'replace')
            if 'AlternateMode:Split' in text:
                faces = [l[5:].strip() for l in text.splitlines() if l.startswith('Name:')]
                names.add(' // '.join(faces))
    return names


def jar():
    found = sorted(f for f in os.listdir(home())
                   if f.startswith('forge-gui-desktop-') and f.endswith('-jar-with-dependencies.jar'))
    if not found:
        raise FileNotFoundError(f'no forge-gui-desktop jar in {home()}; see docs/forge.md')
    return os.path.join(home(), found[-1])


def run(dcks, n, seconds):
    """Play `n` Commander games between the `.dck` files (all in one directory); return the output.

    Forge calls a game a draw after `seconds`; the process is killed if the run overruns that.
    """
    dirs = {os.path.dirname(os.path.abspath(d)) for d in dcks}
    if len(dirs) != 1:
        raise ValueError('Forge reads every deck from one directory (-D)')
    cmd = ['java', *JAVA_FLAGS, '-jar', jar(), 'sim', '-D', dirs.pop(), '-d', *map(os.path.basename, dcks),
           '-f', 'Commander', '-n', str(n), '-c', str(seconds), '-q']
    proc = subprocess.run(cmd, cwd=home(), capture_output=True, text=True, timeout=n * (seconds + 60) + 120)
    return proc.stdout + proc.stderr


def parse(text):
    """{'games', 'wins': Counter{deck: n}, 'draws', 'unsupported': [card names]} from `run` output."""
    wins, draws, games = Counter(), 0, 0
    for m in _RESULT.finditer(text):
        games += 1
        if m.group(1):
            wins[m.group(1)] += 1
        else:
            draws += 1
    return {'games': games, 'wins': wins, 'draws': draws,
            'unsupported': sorted(set(_UNSUPPORTED.findall(text)))}
