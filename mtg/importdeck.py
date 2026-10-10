"""Turn a deck link (Moxfield, Archidekt, MTGGoldfish, plain text, Instagram) into a Deck.

Every reader returns Deck(name, commanders, cards, source) with commanders counted in cards.
Instagram is a best-effort chain (see docs/apis.md); it raises Unsure listing candidates when it
can't pick one confidently.
"""
import difflib
import glob
import html
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field

from . import archidekt, http, moxfield

ROOT = os.path.join(os.path.dirname(__file__), '..')
YT_DLP = os.path.join(ROOT, '.venv', 'bin', 'yt-dlp')
YT_DLP_HELP = 'yt-dlp not found; create it with:  python3 -m venv .venv && .venv/bin/pip install yt-dlp'
SKIP_SECTIONS = {'sideboard', 'maybeboard', 'companion', 'considering', 'tokens'}
DECK_URL = re.compile(r'(?:https?://)?(?:www\.)?(?:moxfield\.com/decks/[\w-]+|archidekt\.com/decks/\d+[\w/-]*'
                      r'|mtggoldfish\.com/deck/\d+)')


@dataclass
class Deck:
    name: str
    commanders: list
    cards: Counter
    source: str = ''
    notes: list = field(default_factory=list)


class Unsure(Exception):
    """Raised when a best-effort lookup has candidates but no confident answer."""


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': http.BROWSER_UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


# ---- sites ---------------------------------------------------------------------------------

def from_moxfield(public_id, url=''):
    d = moxfield.deck(public_id)
    cmdrs = [n for n, _, _, _ in moxfield.board(d, 'commanders')]
    cards = Counter({n: q for n, q, _, _ in moxfield.board(d)})
    for n in cmdrs:
        cards[n] += 1
    return Deck(d['name'], cmdrs, cards, url or f'https://moxfield.com/decks/{public_id}')


def from_archidekt(deck_id, url=''):
    d = archidekt.call('GET', f'/api/decks/{deck_id}/', auth=False)
    out = {c['name'] for c in d['categories'] if not c.get('includedInDeck', True)} | SKIP_SECTIONS
    cmdrs, cards = [], Counter()
    for c in d['cards']:
        cats = {x.lower() for x in c['categories']}
        if cats & {x.lower() for x in out} or c.get('deletedAt'):
            continue
        name = c['card']['oracleCard']['name']
        cards[name] += c['quantity']
        if 'commander' in cats:
            cmdrs.append(name)
    return Deck(d['name'], cmdrs, cards, url or f'https://archidekt.com/decks/{deck_id}')


def from_goldfish(deck_id, url=''):
    page = fetch(f'https://www.mtggoldfish.com/deck/{deck_id}')
    m = re.search(r'<title>(.*?)</title>', page, re.S)
    name = re.sub(r'\s+Deck$', '', html.unescape(m.group(1)).strip()) if m else f'Goldfish {deck_id}'
    deck = from_text(fetch(f'https://www.mtggoldfish.com/deck/download/{deck_id}'), name,
                     url or f'https://www.mtggoldfish.com/deck/{deck_id}', blank_sideboard=True)
    crumb = re.search(r'href="/metagame/commander">Commander</a> /\s*<a href="/archetype/[^"]*">([^<]+)</a>', page)
    if crumb and not deck.commanders:  # downloads don't mark commanders; the breadcrumb names the archetype
        c = html.unescape(crumb.group(1))
        if c in deck.cards:
            deck.commanders = [c]
        else:
            deck.notes.append(f'Goldfish archetype {c!r} is not in the list; commander unknown')
    return deck


# ---- plain text ----------------------------------------------------------------------------

LINE = re.compile(r'^(\d+)x?\s+(.+?)(?:\s+\([A-Za-z0-9]+\)(?:\s+\S+)?)?(?:\s+\*[A-Z]\*)?$')


def from_text(text, name='Imported deck', source='', blank_sideboard=False):
    """'1 Card' lines; 'Commander'/'Deck'/'Sideboard' section headers; sideboard/maybeboard skipped,
    and, with blank_sideboard, a blank line after the main deck starts the sideboard (MTGGoldfish)."""
    section, cmdrs, cards, blank_after_main = 'deck', [], Counter(), False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            blank_after_main = blank_sideboard and (blank_after_main or bool(cards))
            continue
        head = line.rstrip(':').lower()
        if head in SKIP_SECTIONS | {'commander', 'commanders', 'deck', 'mainboard', 'main'}:
            section = 'commander' if head.startswith('commander') else 'deck' if head in {'deck', 'mainboard', 'main'} else 'skip'
            blank_after_main = False
            continue
        if line.startswith(('#', '//')):
            continue
        if line.lower().startswith(('sb:', 'commander:')):
            tag, line = line.split(':', 1)
            line = line.strip()
            section = 'skip-one' if tag.lower() == 'sb' else 'commander-one'
        m = LINE.match(line) or (re.match(r'^()(.+)$', line) if section.endswith('-one') else None)
        if not m:
            continue
        qty, card = int(m.group(1) or 1), m.group(2).strip()
        if section in ('skip', 'skip-one') or (blank_after_main and section == 'deck'):
            continue
        cards[card] += qty
        if section.startswith('commander'):
            cmdrs.append(card)
        if section.endswith('-one'):
            section = 'deck'
    return Deck(name, cmdrs, cards, source)


# ---- dispatch ------------------------------------------------------------------------------

def load(src, bio_link=None):
    if os.path.exists(src):
        return from_text(open(src).read(), os.path.splitext(os.path.basename(src))[0], src)
    if m := re.search(r'moxfield\.com/decks/([\w-]+)', src):
        return from_moxfield(m.group(1), src)
    if m := re.search(r'archidekt\.com/decks/(\d+)', src):
        return from_archidekt(m.group(1), src)
    if m := re.search(r'mtggoldfish\.com/deck/(?:download/)?(\d+)', src):
        return from_goldfish(m.group(1), src)
    if 'instagram.com' in src:
        return from_instagram(src, bio_link)
    return from_text(fetch(src), os.path.basename(urllib.parse.urlparse(src).path) or 'Imported deck', src)


# ---- Instagram -----------------------------------------------------------------------------

def _info(url):
    if not os.path.exists(YT_DLP):
        raise SystemExit(YT_DLP_HELP)
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([YT_DLP, '--write-info-json', '--skip-download', '-q', '-o', f'{tmp}/%(id)s', url],
                           capture_output=True, text=True)
        files = glob.glob(f'{tmp}/*.json')
        if not files:
            raise SystemExit(f'yt-dlp could not read {url}: {r.stderr.strip()[-300:]}')
        return json.load(open(files[0]))


def _words(s):
    return re.findall(r'[a-z0-9]+', s.lower())


def _score(deck_name, caption):
    """1.0 if the deck name appears in the caption, else the share of its words that do (fuzzily)."""
    name, cap = _words(deck_name), _words(caption)
    if not name:
        return 0
    if ' '.join(name) in ' '.join(cap):
        return 1.0
    return sum(bool(difflib.get_close_matches(w, cap, 1, 0.85)) for w in name) / len(name) * 0.9


def _guess_bio_links(info):
    """Instagram hides the bio from us, so guess link-in-bio pages from the account name."""
    handles = {h for h in (info.get('channel'), info.get('uploader'), info.get('uploader_id')) if h and not h.isdigit()}
    handles |= {re.sub(r'[._](mtg|tcg|magic|official)$', '', h, flags=re.I) for h in handles}
    out = []
    for h in sorted({h.lower() for h in handles}):
        for site in ('linktr.ee', 'beacons.ai', 'bio.site', 'linkin.bio'):
            out.append(f'https://{site}/{h}')
    return out


def _profiles(page):
    return (set(re.findall(r'moxfield\.com/users/([\w.-]+)', page)),
            set(re.findall(r'archidekt\.com/u/([\w.-]+)', page)))


def from_instagram(url, bio_link=None):
    info = _info(url)
    caption = info.get('description') or info.get('title') or ''
    print(f'caption: {caption.splitlines()[0] if caption else ""!r} (by {info.get("channel") or info.get("uploader")})')
    if m := DECK_URL.search(caption):
        u = m.group(0) if m.group(0).startswith('http') else 'https://' + m.group(0)
        print('deck link in caption:', u)
        return load(u)
    mox, arc, tried = set(), set(), []
    for link in [bio_link] if bio_link else _guess_bio_links(info):
        try:
            page = fetch(link)
        except Exception:
            continue
        tried.append(link)
        if m := DECK_URL.search(page):
            u = m.group(0) if m.group(0).startswith('http') else 'https://' + m.group(0)
            print('deck link on', link, '->', u)
            return load(u)
        a, b = _profiles(page)
        print(f'bio page {link}: moxfield {sorted(a) or "-"}, archidekt {sorted(b) or "-"}')
        mox |= a
        arc |= b
        if a or b:
            break
    if not (mox or arc):
        raise Unsure('no deck or profile links found. Tried: ' + (', '.join(tried) or 'no bio pages') +
                     '\nPass the account\'s link-in-bio page with --bio-link URL, or the deck URL directly.')
    cands = []  # (score, recency rank, name, url)
    for user in sorted(mox):
        decks = sorted(moxfield.public_decks(user), key=lambda d: d.get('lastUpdatedAtUtc', ''), reverse=True)
        cands += [(_score(d['name'], caption), -i, d['name'], f'https://moxfield.com/decks/{d["publicId"]}')
                  for i, d in enumerate(decks)]
    for user in sorted(arc):
        r = archidekt.call('GET', f'/api/decks/v3/?ownerUsername={urllib.parse.quote(user)}&pageSize=50', auth=False)
        decks = sorted(r['results'], key=lambda d: d.get('updatedAt', ''), reverse=True)
        cands += [(_score(d['name'], caption), -i, d['name'], f'https://archidekt.com/decks/{d["id"]}')
                  for i, d in enumerate(decks)]
    cands.sort(reverse=True)
    best = [c for c in cands if c[0] >= 0.8]
    if best and (len(best) == 1 or best[0][0] - best[1][0] >= 0.2):
        print(f'matched deck {best[0][2].strip()!r} (score {best[0][0]:.2f})')
        return load(best[0][3])
    top = '\n'.join(f'  {s:.2f}  {n}  {u}' for s, _, n, u in cands[:8])
    raise Unsure(f'not confident which deck this is; best candidates:\n{top}\nRe-run with the right URL.')
