#!/usr/bin/env python3
"""Show who this checkout is set up for, and check the setup works (never prints the password).

    scripts/whoami.py

Prints the player (MTG_PLAYER) and whether players/<player>.md exists, the Archidekt account, and the
name of each configured folder (which also proves the login works). Exits 1 if anything is missing.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtg import archidekt, config

ROOT = os.path.join(os.path.dirname(__file__), '..')
FOLDERS = {'ARCHIDEKT_DECKS_FOLDER': 'decks you play (default for upload and pull)',
           'ARCHIDEKT_IDEAS_FOLDER': "other people's lists and ideas",
           'ARCHIDEKT_ARCHIVE_FOLDER': 'retired decks (archive, never delete)'}


def main():
    ok = True
    player = config.get('MTG_PLAYER', required=False)
    profile = os.path.join('players', f'{player}.md') if player else None
    if not player:
        ok = False
        print('player:   MTG_PLAYER not set in .env')
    else:
        found = os.path.exists(os.path.join(ROOT, profile))
        ok &= found
        print(f"player:   {player}  ({profile}{'' if found else ' missing: copy another profile'})")
    print(f"archidekt: {config.get('ARCHIDEKT_USERNAME', required=False) or 'ARCHIDEKT_USERNAME not set'}, "
          f"password {'set' if config.get('ARCHIDEKT_PASSWORD', required=False) else 'not set (1Password fallback)'}")
    for key, meaning in FOLDERS.items():
        fid = config.get(key, required=False)
        if not fid:
            ok &= key != 'ARCHIDEKT_DECKS_FOLDER'
            print(f'  {key}: not set ({meaning})')
            continue
        print(f"  {key}: {fid} = \"{archidekt.folder(int(fid))['name']}\" ({meaning})")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
