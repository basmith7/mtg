# 05 — Ravnica: one primer format, Core decks on Archidekt

**Contract:** every Ravnica list exists on Archidekt; primers have one format (`.md` beside the list).

**Steps:**
1. Convert `decks/ravnica/primers_core.py` and `primers_extra.py` `PRIMERS` dicts into
   `<list>.md` files beside each `.txt` (core primers beside `core/*.txt`, extra beside
   `extra/*.txt`; check which primers the existing power decks on Archidekt use and put those
   beside `power/*.txt`). Delete the `.py` files and `upload_decks.py --primers`.
2. Slice 00 recorded which version is live. Rename the headers of the *other* set to
   `# <Name> (Core) | <colors>` (or `(Power)` if the live decks turn out to be Core).
3. Back up nothing (new decks only). `upload_decks.py --folder 1914718 <those 10 files>`.
   Before uploading, check by name that none of them already exists (re-runs must not duplicate).
4. `verify_decks.py decks/ravnica/**/*.txt` → all OK.

**Brian sees:** 10 new "(Core)" decks in the Ravnica folder, with primers.

**Delegated:** nothing else; folder and naming are fixed above.

**Stays green:** the 22 existing Ravnica decks untouched (no `sync` on them).
