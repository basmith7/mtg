# 08 — Delete merged branches, flip public

1. List `git branch -r --merged origin/master`; expect the 12 approved
   (`deck-review-tunes`, `deck/ruric-thar`, `deck/xantcha`, `feat/archidekt-sync`, `feat/deck-stats`,
   `feat/deck-toolkit`, `feat/edhrec`, `feat/import-deck`, `feat/playlog`, `feat/skill`,
   `feat/spellbook`, `ruric-tune-and-stats` — re-count; anything unmerged or unexpected, ask).
   Delete each by name (Brian approved deleting the merged branches; the earlier "11" was a miscount of these 12): `git push origin --delete <b>`. Delete merged local branches too.
2. Preflight: this spec's PR merged; fresh clone into a temp dir runs
   `python3 -m unittest discover tests` and `scripts/check_commander.py --help` without `.env`.
3. **Ask Brian** (one-way door, not yet approved): flip to public. On yes:
   `gh repo edit basmith7/mtg --visibility public --accept-visibility-change-consequences`.
4. Then `close-spec` and `architecture-doc`.
