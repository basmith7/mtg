"""Account settings: the environment, else the gitignored .env in the main checkout (see .env.example).

Linked worktrees read the main checkout's .env, so a fresh worktree needs no setup. Never print values.
"""
import functools
import os
import subprocess

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@functools.cache
def env_file():
    """Path of .env at the main checkout's root (the parent of the shared .git dir)."""
    try:
        common = subprocess.run(['git', '-C', _REPO, 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                capture_output=True, text=True, check=True).stdout.strip()
        return os.path.join(os.path.dirname(common), '.env')
    except (OSError, subprocess.CalledProcessError):
        return os.path.join(_REPO, '.env')


def _file_values(path):
    out = {}
    if os.path.exists(path):
        for line in open(path):
            key, sep, value = line.strip().partition('=')
            if sep and not key.startswith('#'):
                out[key.strip()] = value.strip().strip('"\'')
    return out


def get(key, required=True):
    value = os.environ.get(key) or _file_values(env_file()).get(key)
    if not value and required:
        raise KeyError(f'{key} is not set: add it to the environment or {env_file()} (see .env.example)')
    return value
