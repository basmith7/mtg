# MTG APIs

Everything here was worked out on 2026-10-03 while organizing Brian's Archidekt and building
the Ravnica guild decks. **Only Scryfall has a documented public API.** Archidekt and Moxfield are
the sites' own private APIs, found by reading their web bundles; they can change without notice.
If an endpoint stops working, re-derive it (see "Finding endpoints" at the bottom).

| Service | What we use it for | Auth | Stability |
|---|---|---|---|
| Scryfall | Card data, oracle text, prices, set searches | None | Public, documented |
| Archidekt | Brian's decks, folders, tags, primers, collection | JWT (login) | Private, undocumented |
| Moxfield | Reading Brian's public decks and shared collection | None for public data; login blocked | Private, undocumented |
| EDHREC | Card inclusion % and synergy per commander, themes, average decks | None | Private JSON, undocumented |
| MTGGoldfish | Reading decklists out of articles | None | Scraping |

Python clients for all of these live in `mtg/` (see the README).

---

## Scryfall — `https://api.scryfall.com`

Docs: <https://scryfall.com/docs/api>. Send `User-Agent` **and** `Accept: application/json`
(requests without `Accept` get HTTP 400). Keep to ~10 requests/sec; on HTTP 429 back off and retry.

- `GET /cards/search?q=<query>&unique=cards|prints&order=usd&dir=asc` — full Scryfall search syntax.
  Paginated: follow `next_page` until absent.
  - Every card from a set list: `q=(e:rav or e:gtc or ...) -t:token`, `unique=cards`.
  - Cheapest printing of a card: `q=!"Card Name" game:paper`, `unique=prints`, `order=usd`, `dir=asc`,
    then take the lowest `prices.usd` (fall back to `prices.usd_foil`).
- `GET /cards/named?exact=<name>` — one card. `fuzzy=` also works.
- Useful card fields: `name`, `mana_cost`, `type_line`, `oracle_text` (or `card_faces[].oracle_text` for
  split/DFC cards), `color_identity`, `rarity`, `legalities`, `prices.usd`, `id` (Scryfall UUID).
- Prices are TCGplayer market prices, updated daily. Shipping is not included.

**The Scryfall UUID is the join key across sites:** Moxfield exposes it as `card.scryfall_id`,
Archidekt as `card.uid`.

---

## Archidekt — `https://archidekt.com`

Brian's account: username `basmith7`, user id `309724`. Password is in 1Password item
`727iygg5qogmtfsx7mfphyubbi` ("archidekt.com").

### Auth
- `POST /api/rest-auth/login/` `{"username", "password"}` → `access_token`, `refresh_token`.
  Send `Authorization: JWT <access_token>` on every call.
- `POST /api/rest-auth/token/refresh/` `{"refresh": <refresh_token>}` → new `access`. Use this when a
  call returns 401 — **don't log in again**: every `op` call pops a 1Password prompt for Brian.
- The client caches tokens in `~/.config/mtg/archidekt-session.json` (mode 600, outside the repo).
- Never print the password. Pipe it from `op` straight into the login request.

### Reading
- `GET /api/decks/{id}/` — full deck: `name`, `deckFormat`, `description`, `hasPrimer`, `parentFolder`,
  `categories[]` (with `includedInDeck`), `cards[]` (each: `quantity`, `categories[]`, `modifier`,
  `card.id` = Archidekt card id, `card.uid` = Scryfall id, `card.oracleCard.name`). Public decks need no auth.
- `GET /api/decks/v3/?ownerUsername=basmith7&pageSize=50&page=N` — list decks.
- `GET /api/decks/folderTree/` — folder hierarchy. `GET /api/decks/folders/{id}/?pageSize=100` — folder
  contents (`decks[]`, `subfolders`, `count`).
- `GET /api/collection/309724/v2/?game=1&page=N&pageSize=100` — collection entries (`quantity`, `foil`,
  `card.uid`, `card.id`). Paginated by `totalPages`.
- `GET /api/cards/v2/?exact=true&name=<name>` — card lookup → every printing with its Archidekt `id`.
  **Rate-limited hard (HTTP 429):** keep ~1 request/sec and back off. Cache name→id. (Filtering by `uid`
  is ignored by this endpoint.)
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
  `parentFolder`.
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

### Brian's folders (2026-10-03)
Home `440408` → Commander `1914431` (played online), Paper `1914435` → Ravnica Guilds `1914718`,
Lists & Ideas `1914436`, Archive `1914437` (private). Deck names follow
"Commander – Theme or nickname (B#)".

---

## Moxfield — `https://api2.moxfield.com`

Brian's username: `basmith7` (1Password item `h7ki37e64em43rpjrxa3ltljna`). **Scripted login is
blocked** (`POST /v1/account/token` returns a bare 400, likely a captcha), so we only read public data.
The `v3` deck endpoint sits behind Cloudflare; `v2` works with a normal browser `User-Agent`.

- `GET /v2/decks/all/{publicId}` — a deck. Boards: `commanders`, `mainboard`, `sideboard`, `maybeboard`,
  each `{name: {quantity, card: {name, scryfall_id, type_line, ...}}}`.
- `GET /v2/decks/search?authorUserNames=basmith7&pageSize=100` — Brian's **public** decks.
- `GET /v1/users/basmith7` — profile (shows `collectionVisibility`).
- `GET /v1/collections/search/{collectionId}?pageNumber=N&pageSize=100&sortType=cardName&sortDirection=ascending`
  — a collection shared by link. Brian's: `cujOu-wx10SVgh_nMlHdXg`. Entries have `quantity`, `isFoil`,
  `card.scryfall_id`. Paginated by `totalPages`.

The third-party `moxfield-api` npm package only wraps the public deck/search/card endpoints; it adds
nothing over the above.

---

## EDHREC — `https://json.edhrec.com/pages`

No auth, no documentation; these are the JSON files the edhrec.com site loads (found 2026-10-09).
Browser `User-Agent` works; the client keeps ~1 request/sec and caches responses 7 days in `cache/edhrec/`.
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
- `GET /deck/{id}` — the deck page (name in `<title>`).

---

## Finding endpoints again

Archidekt is a Next.js app. Fetch a page (deck, folder, collection), collect its
`/_next/static/...js` bundles, and grep for `super.get(`, `super.post(`, `super.patch(` and `"/api/`.
Page-specific features (folders, collection import) live in bundles that only load on that page, so
fetch the relevant page first. That's how `massUpdate`, `modifyCards/v2` and `token/refresh` were found.
The deck-editing actions (`add`/`modify`/`remove`) are in `_app-*.js`, in `prepareSave` / `makeSaveRequest`.
Collection CSV import (`/api/collection/upload/v2/`, form upload) and text import
(`/api/collection/textImport/`) exist but haven't been exercised.
