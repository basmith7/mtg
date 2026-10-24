"""Player profiles: players/<player>.md (taste, preferences, play log). See players/README.md."""
import os
import re

PLAYERS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'players')
FIELDS = ('Result', 'Fun', 'Flopped', 'Change')


def render_entry(date, deck, result='', fun='', flopped='', change=''):
    """One play-log block in the profile's format: '### date — deck', then a bullet per field.
    Empty fields read 'not given', as the hand-written entries do."""
    values = (result, fun, flopped, change)
    return '\n'.join([f'### {date} — {deck}'] + [f'- {k}: {v or "not given"}' for k, v in zip(FIELDS, values)]) + '\n'


def add_entry(player, entry, players_dir=PLAYERS):
    """Insert a rendered entry into the profile's '## Play log', below the format template, keeping
    entries newest first by the latest date in each heading (a backfilled older game goes further
    down). Raises ValueError if the profile has no play log."""
    path = os.path.join(players_dir, f'{player}.md')
    lines = open(path).read().split('\n')
    try:
        at = next(i for i, l in enumerate(lines) if l.strip() == '## Play log') + 1
    except StopIteration:
        raise ValueError(f'{path} has no "## Play log" section') from None
    while at < len(lines) and not lines[at].startswith(('###', '## ')):
        if lines[at].startswith('```'):  # skip the fenced format template
            at = next(i for i in range(at + 1, len(lines)) if lines[i].startswith('```'))
        at += 1
    mine = _latest(entry.split('\n', 1)[0])
    while at < len(lines) and lines[at].startswith('### ') and _latest(lines[at]) > mine:
        at = next((i for i in range(at + 1, len(lines)) if lines[i].startswith(('###', '## '))), len(lines))
    while at > 0 and not lines[at - 1].strip():
        at -= 1
    lines[at:at] = [''] + entry.rstrip('\n').split('\n')
    with open(path, 'w') as f:
        f.write('\n'.join(lines))


def _latest(heading):
    """The latest YYYY-MM-DD in a play-log heading ('' if none)."""
    return max(re.findall(r'\d{4}-\d{2}-\d{2}', heading), default='')


def enjoys(player, players_dir=PLAYERS):
    """The bullets under the profile's '## What <player> enjoys' heading, one string per bullet
    (wrapped lines joined). [] if the profile has no such section."""
    bullets, inside = [], False
    with open(os.path.join(players_dir, f'{player}.md')) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('#'):
            inside = line.startswith('## What') and 'enjoys' in line
            continue
        if not inside:
            continue
        text = line.strip()
        if text.startswith(('- ', '* ')):
            bullets.append(text[2:].strip())
        elif text and bullets and line[:1].isspace():
            bullets[-1] += ' ' + text
    return bullets
