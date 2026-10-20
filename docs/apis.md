# MTG APIs

Most of this was worked out in October 2026 while organizing an Archidekt account and building
decks. **Only Scryfall has a documented public API.** Archidekt and Moxfield are
the sites' own private APIs, found by reading their web bundles; they can change without notice.
If an endpoint stops working, re-derive it (see "Finding endpoints" at the bottom).

| Service | What we use it for | Auth | Stability |
|---|---|---|---|
| Scryfall | Card data, oracle text, legality, search | None | Public, documented |
| Archidekt | Your decks (the canonical copy), folders, primers | JWT (login) | Private, undocumented |
| Moxfield | Reading public decks | None for public data; login blocked | Private, undocumented |
| Commander Spellbook | Combos a decklist contains or is one card from | None | Public, OpenAPI schema |
| EDHREC | Card inclusion % and synergy per commander, themes, average decks | None | Private JSON, undocumented |
| MTGGoldfish | Reading decklists out of articles | None | Scraping |

Python clients for all of these live in `mtg/` (see the README).

---

## Scryfall — `https://api.scryfall.com`

Docs: <https://scryfall.com/docs/api>. Send `User-Agent` **and** `Accept: application/json`
(requests without `Accept` get HTTP 400). Keep to ~10 requests/sec; on HTTP 429 back off and retry.
The limit is per machine, so several agents running checkers at once hit 429s.

- `GET /cards/search?q=<query>&unique=cards|prints&order=usd&dir=asc` — full Scryfall search syntax.
  Paginated: follow `next_page` until absent.
- `GET /cards/named?exact=<name>` — one card. `fuzzy=` also works.
- Useful card fields: `name`, `mana_cost`, `type_line`, `oracle_text` (or `card_faces[].oracle_text` for
  split/DFC cards), `color_identity`, `rarity`, `legalities`, `prices.usd`, `id` (Scryfall UUID).
- `POST /cards/collection` (75 names a request) accepts a double-faced card's front-face name, and
  `scryfall.collection()` returns such cards under both the full and the front name, so looping over its
  values gives duplicates. Cards not yet released aren't there (EDHREC has no page for them either).

**The Scryfall UUID is the join key across sites:** Moxfield exposes it as `card.scryfall_id`,
Archidekt as `card.uid`.

---

## Archidekt — `https://archidekt.com`

Account settings come from `mtg/config.py`: the environment, else the gitignored `.env` in the main
checkout (keys in `.env.example`): `ARCHIDEKT_USERNAME` and `ARCHIDEKT_PASSWORD`. Without a password the client reads it from the 1Password
item `ARCHIDEKT_OP_ITEM`, which prompts.

### Auth
- `POST /api/rest-auth/login/` `{"username", "password"}` → `access_token`, `refresh_token`.
  Send `Authorization: JWT <access_token>` on every call. `archidekt.login()` returns nothing on
  success; an authenticated call (`scripts/whoami.py`) is the check.
- `POST /api/rest-auth/token/refresh/` `{"refresh": <refresh_token>}` → new `access`. Use this when a
  call returns 401 — don't log in again needlessly (the client does this).
- The client caches tokens in `~/.config/mtg/archidekt-session.json` (mode 600, outside the repo).
- Never print the password or read `.env` into the transcript.

### Reading
- `GET /api/decks/{id}/` — full deck: `name`, `deckFormat`, `description`, `hasPrimer`, `parentFolder`,
  `categories[]` (with `includedInDeck`), `cards[]` (each: `quantity`, `categories[]`, `modifier`,
  `card.id` = Archidekt card id, `card.uid` = Scryfall id, `card.oracleCard.name`, `deletedAt`), and
  `createdAt` / `updatedAt` (ISO timestamps; `updatedAt` moves on any edit, which `sync` uses to spot site
  edits since the last pull). Public decks need no auth.
- `GET /api/decks/v3/?ownerUsername=<username>&pageSize=50&page=N` — list decks.
- `GET /api/decks/folderTree/` — folder hierarchy. `GET /api/decks/folders/{id}/?pageSize=100` — folder
  contents (`decks[]`, `subfolders`, `count`, `next`; pages with `&page=N`). `pageSize=100` isn't honoured
  (60 a page), so follow `next`; `archidekt.folder()` does.
- `GET /api/collection/<user id>/v2/?game=1&page=N&pageSize=100` — collection entries (`quantity`, `foil`,
  `card.uid`, `card.id`). Paginated by `totalPages`.
- **Card ids.** Adding a card to a deck needs Archidekt's own card id.
  - `POST /api/cards/massDeckEdit/` `{"parser": "archidekt", "current": <deck text>, "edit": <new text>}`:
    the parser behind the deck editor's "Import cards" box (found 2026-10-20 in the deck page bundle).
    It diffs two pasted lists and returns `toAdd` / `toRemove` (each with the full `card`, the printing
    the site picks), `categories` from `# Category` lines, `syntaxErrors` and `cardErrors`. It only
    parses; the page then saves through `modifyCards/v2`. Accepts `2x`, `(SET) 123`, front-face names.
    A 100-card list resolves in one ~1 s request. `archidekt.resolve(names)` uses it with `current: ""`.
  - `GET /api/cards/v2/?uids=<scryfall id>,...` — bulk lookup by Scryfall id, 60 a page (follow `next`).
    `name=` with a comma-joined list returns nothing.
  - `GET /api/cards/v2/?exact=true&name=<name>` — one name, every printing. **Rate-limited hard (HTTP
    429)**, ~1 request/sec, and needs the full `A // B` name for double-faced cards. No longer used.
- `GET /api/decks/tags/v2/?q=<text>` — search the fixed list of deck tags (id + name).

### Writing
- **Create a deck:** `POST /api/decks/v2/` with
  `{"name", "deckFormat", "description": "", "private": false, "unlisted": false, "theorycrafted": false,
  "parentFolder": <folder id>, "extras": {"commanders": [], "forceCardsToSingleton": false, "game": null,
  "cardPackage": null}, "cards": []}`. Cards sent here are **ignored**; add them separately.
  Returns the new deck `id`. Don't rely on `parentFolder` here; move the deck with `massUpdate` afterwards.
- **Add cards:** `PATCH /api/decks/{id}/modifyCards/v2/` with `{"cards": [{"action": "add", "cardid": <archidekt id>,
  "categories": ["Creature"], "patchId": "p0", "modifications": {"quantity": 4, "modifier": "Normal",
  "customCmc": null, "companion": false, "flippedDefault": false, "label": ",#656565"}}]}`.
  One call can carry the whole deck. Categories are created on demand; "Commander", "Sideboard" and
  "Maybeboard" are special (Maybeboard is excluded from the deck count). `modifier` can be "Foil".
- **Remove cards:** same endpoint, `"action": "remove"`, with the same fields plus `"deckRelationId": <the deck
  card entry's top-level "id" from GET /api/decks/{id}/>` (not `card.id`, which is still sent as `cardid`).
  The card's current `categories` and `modifications` (incl. `quantity`) go along. The response looks like
  `{"add": [], "createdCategories": []}`.
- **Change quantity/category in place:** `"action": "modify"` (found in the `_app` bundle's `prepareSave`:
  the web UI sends `modify` for any existing entry and `add` for new ones) with `deckRelationId`, `cardid`, and
  the new `categories` and `modifications.quantity`. Verified 2026-10-09; no remove + re-add needed.
  Add, modify and remove can share a request, but the client sends them as separate calls.
- **Rename / description / primer:** `PATCH /api/decks/{id}/update/` with `{"name"}` or
  `{"description": <Quill delta JSON string>, "hasPrimer": true}`. The update endpoint **ignores**
  `parentFolder`. Primers written on the site use more of Quill than `mtg/quill.py`'s markdown holds
  (h1/h3/h4, italic, colour, background, code, links, ordered lists, indents, image embeds; seen in 14
  of 62 Commander decks on 2026-10-20), so `sync` leaves an unchanged primer alone.
- **Move decks or rename folders:** `PATCH /api/massUpdate/` with
  `{"items": [{"type": "deck"|"folder", "id": N, "patch": {"parentFolder": F}}]}` (also `{"name"}`,
  `{"private"}` for folders).
- **Create a folder:** `POST /api/decks/folders/` `{"name", "private", "parentFolder"}`. Returns non-JSON;
  re-read `folderTree` to get the id.
- **Tag a deck:** `POST /api/decks/tagRelations/` `{"deck", "tag": <tag id>, "position"}`.
- Deleting (not used yet): `POST /api/decks/folders/deleteItems/`.

### Descriptions and primers
Descriptions are **Quill delta** JSON stored as a string: `{"ops": [{"insert": "text"}, ...]}`.
- Bold: `{"insert": "x", "attributes": {"bold": true}}`.
- Heading: text op, then `{"insert": "\n", "attributes": {"header": 2}}`.
- Bullet: text op, then `{"insert": "\n", "attributes": {"list": "bullet"}}`.
- `[[Card Name]]` inside text renders as a card link with hover image.
- A primer is the description with `hasPrimer: true`; it shows pinned beside the list.
`mtg/quill.py` converts a light markdown (`## `, `- `, `**bold**`) to this format.

### Deck formats
`deckFormat` ids: 1 Standard, 2 Modern, 3 Commander, 4 Legacy, 5 Vintage, 6 Pauper, 7 Custom,
8 Frontier, 9 Future Standard, 10 Penny, 11 1v1 Commander, 12 Duel Commander, 13 Brawl,
14 Oathbreaker, 15 Pioneer, 16 Historic, 17 Pauper EDH, 18 Alchemy, 19 Explorer, 20 Historic Brawl,
21 Gladiator, 22 Premodern, 23 PreDH, 24 Timeless, 25 Canlander, 26 Competitive Brawl.

### Folders
Each player's folder ids live in their `.env` (`ARCHIDEKT_*_FOLDER`, see `.env.example`); the folder id
is the number in its URL. `scripts/whoami.py` prints their names.

---

## Moxfield — `https://api2.moxfield.com`

**Scripted login is blocked** (`POST /v1/account/token` returns a bare 400, likely a captcha), so we only read public data.
The `v3` deck endpoint sits behind Cloudflare; `v2` works with a normal browser `User-Agent`.

- `GET /v2/decks/all/{publicId}` — a deck. Boards: `commanders`, `mainboard`, `sideboard`, `maybeboard`,
  each `{name: {quantity, card: {name, scryfall_id, type_line, ...}}}`.
- `GET /v2/decks/search?authorUserNames=<username>&pageSize=100` — a user's **public** decks.
- `GET /v1/users/<username>` — profile (shows `collectionVisibility`).
- `GET /v1/collections/search/{collectionId}?pageNumber=N&pageSize=100&sortType=cardName&sortDirection=ascending`
  — a collection shared by link. Entries have `quantity`, `isFoil`,
  `card.scryfall_id`. Paginated by `totalPages`.

The third-party `moxfield-api` npm package only wraps the public deck/search/card endpoints; it adds
nothing over the above.

---

## Commander Spellbook — `https://backend.commanderspellbook.com`

Public, no auth. OpenAPI schema (Swagger) at `/schema/`; client is `mtg/spellbook.py`. Checked 2026-10-09.

- `POST /find-my-combos` with `{"commanders": [{"card": "Name"}], "main": [{"card": "Name", "quantity": 1}]}`
  (`text/plain` decklist bodies also work). Use exact card names; list the commander under `commanders` only.
  The response is paginated, but `results` is one object holding all the lists:
  `included` (combos fully in the deck), `almostIncluded` (missing one card, within the deck's colours),
  plus `...ByAddingColors`, `...ByChangingCommanders` variants and `identity`.
- Each variant (combo) has: `id` (page is `https://commanderspellbook.com/combo/<id>/`), `uses[]`
  (`card.name`, `quantity`, `zoneLocations`, `mustBeCommander`), `requires[]` (non-card templates such as
  "a creature"), `produces[]` (`feature.name`, `feature.status`, e.g. "Infinite damage"),
  `bracketTag`, `easyPrerequisites`, `notablePrerequisites`, `manaNeeded`, `manaValueNeeded`,
  `description` (steps), `popularity`, `legalities`, `prices`.
- `produces` includes helper features (`status` `H`, e.g. "Infinite creature ETB") alongside the headline
  ones (`S` standalone); the client shows non-helper results. Feature names beginning "Infinite" are how
  `check_commander.py` spots infinite combos.
- `bracketTag`: C Core, E Exhibition, O Oddball, P Powerful, S Spicy, R Ruthless, B Banned (Spellbook's
  own tiers, not the same as the house "B3.75"). No mana values come back; the checker gets them from Scryfall.
- Combo names in `uses` are sometimes a face name only; `uses` can also list a combo's commander.
- Cheap to call (one request per deck, ~1 s); no rate limit hit so far.
## EDHREC — `https://json.edhrec.com/pages`

No auth, no documentation; these are the JSON files the edhrec.com site loads (found 2026-10-09).
Browser `User-Agent` works; the client keeps ~1 request/sec and caches responses 7 days in `~/.cache/mtg/edhrec/`.
Slugs: lowercase ASCII, accents stripped, apostrophes dropped, other punctuation to `-`
(`Ruric Thar, the Unbowed` -> `ruric-thar-the-unbowed`; `Fire // Ice` front face only for commanders).

- `/commanders/{slug}.json` — the commander page.
- `/commanders/{slug}/{theme}.json` — a theme (slugs from `tag_counts`, e.g. `burn`, `stax`, `ramp`).
- `/commanders/{slug}/budget.json`, `/expensive.json` — budget variants. (Combined theme+budget paths were not tried.)
- `/average-decks/{slug}.json` — average decklist: `deck.cards` = `{Type: [[name, qty], ...]}`,
  `deck.commander_v2`. Same page-level keys as the commander page.
- `/cards/{slug}.json` — one card: `container.json_dict.card` (`num_decks`, `potential_decks`, `salt`,
  `prices`, `color_identity`...) plus cardlists of related cards.

Commander page shape: top-level `tag_counts` (`[{slug, value, count}]` = themes), `budget_counts`,
`bracket_counts`, `similar` (commander names), `panels` (combos, mana curve), `header`, and
`container.json_dict.cardlists[]`: `{header, tag, cardviews[]}`. Headers: `New Cards`, `Top Cards`,
`High Lift Cards`, then `Creatures`, `Instants`, `Sorceries`, `Utility Artifacts`, `Enchantments`,
`Planeswalkers`, `Utility Lands`, `Mana Artifacts`, `Lands`. Each cardview: `name`, `slug`, `num_decks`,
`potential_decks`, `synergy` (fraction, -1..1), `lift`, `trend_zscore`. There is no inclusion field:
**inclusion = num_decks / potential_decks**.

Gotchas: the highlight lists (`Top Cards` etc.) *remove* their cards from the type lists, so merge them
(`mtg/edhrec.py` does, preferring the type list). Each list is capped (~50 creatures), so a card absent from
the lists is not necessarily rare in the deck. Basics appear in `Lands`.

---

## MTGGoldfish — `https://www.mtggoldfish.com`

No API. Articles embed decks as `<ins class="widget-deck-placeholder" data-id="N">`.
- `GET /deck/download/{id}` — plain-text decklist ("4 Card Name", blank line before sideboard).
- `GET /deck/{id}` — the deck page (name in `<title>`). Commander downloads don't mark the commander
  (all 100 cards are plain lines); the breadcrumb `/archetype/...` link on the page names it.

---

## Instagram, Linktree, yt-dlp (deck links from reels)

Instagram has no usable API without login (`/api/v1/users/web_profile_info/` returns "require_login",
and the plain profile HTML hides the bio). What works (2026-10-09, `scripts/import_deck.py`):
- `.venv/bin/yt-dlp --write-info-json --skip-download -o 'dir/%(id)s' <reel url>` gives `description` (the
  caption), `channel` (handle, e.g. `unmagical.mtg`) and `uploader` (display name). yt-dlp isn't installed
  system-wide: `python3 -m venv .venv && .venv/bin/pip install yt-dlp` (`.venv/` is git-ignored).
- The bio link isn't exposed, so we guess `linktr.ee/<handle>` (also beacons.ai, bio.site, with
  `.mtg`/`_mtg` suffixes stripped); beacons.ai returns 403 to scripts. `--bio-link` overrides the guess.
- A Linktree page embeds `__NEXT_DATA__`; its `"url":"..."` entries include `moxfield.com/users/<name>`.
- `GET /v2/decks/search?authorUserNames=<name>` (Moxfield) and `/api/decks/v3/?ownerUsername=<name>`
  (Archidekt) list that person's decks; names are matched against the caption, most recent first.
  Example: reel `Dd67dxZkSQF` ("54 FERAL HOGS DECKLIST...") -> linktr.ee/unmagical -> Moxfield user
  `willy` -> deck "54 Feral Hogs" (`t9G16DLc5EO0uYOuDftBIQ`).
- Archidekt's `GET /api/decks/{id}/` needs no auth for public decks (`auth=False` in the client).

---

## Finding endpoints again

Archidekt is a Next.js app. Fetch a page (deck, folder, collection), collect its
`/_next/static/...js` bundles, and grep for `super.get(`, `super.post(`, `super.patch(` and `"/api/`.
Page-specific features (folders, collection import) live in bundles that only load on that page, so
fetch the relevant page first. That's how `massUpdate`, `modifyCards/v2` and `token/refresh` were found.
The deck-editing actions (`add`/`modify`/`remove`) are in `_app-*.js`, in `prepareSave` / `makeSaveRequest`.
Collection CSV import (`/api/collection/upload/v2/`, form upload) and text import
(`/api/collection/textImport/`) exist but haven't been exercised.
