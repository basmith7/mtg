"""Player profiles: players/<player>.md (taste, preferences, play log). See players/README.md."""
import os

PLAYERS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'players')


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
