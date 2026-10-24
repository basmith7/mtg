# 10 Forge pods (experiment)

**Contract:** `scripts/forge_sim.py a.txt b.txt c.txt d.txt -n 10` plays the player's own decks against
each other with Forge's AI, offline, and reports a rough win share. Never at the player's table.

**Spike first (outside the repo):**
- Download the latest Forge release (`forge-installer-*.tar.bz2` from Card-Forge/forge releases;
  2.0.15 on 2026-09-28) and unpack under `~/.local/share/forge`. Java: OpenJDK 25 is installed; no
  system packages.
- Hand-convert 4 decks to `.dck` and run `sim -d a.dck b.dck c.dck d.dck -f Commander -n 5 -c 600 -q`
  (flags from `SimulateMatch.java`: `-d`, `-D`, `-n`, `-f`, `-c` seconds per game, `-s`, `-q`).
- Measure: starts on JDK 25 (with the launcher's `--add-opens`)? seconds per game, draws ("Stopping
  slow match as draw"), cards Forge can't load (`Could not load deck`, unsupported-card warnings).

**Kill if:** it needs another JDK as a system install; ≥50% draws at `-c 600`; more than 5 unsupported
cards per deck. Record evidence and stop.

**Ship (if alive):**
- `mtg/forge.py`: `to_dck(name, commanders, cards) -> str` (pure; `[metadata] Name=`, `[Commander]`,
  `[Main]`), `home()` (`FORGE_HOME` env or `~/.local/share/forge`), `run(dcks, n, seconds) -> str`,
  `parse(text) -> {'games', 'wins': Counter, 'draws', 'unsupported'}` (lines `Game Result: Game N
  ended in X ms. Ai(i)-<deck> has won!` / `ended in a Draw!`). `.dck` files go to `config.CACHE/forge`.
- Output labelled "Forge AI play: rough; it plays combo and politics badly".
- Tests: `tests/test_forge.py` golden `.dck` for partners and `A // B` names; `parse` on
  `tests/fixtures/forge_sim_4pod.txt` captured from the spike.
- `docs/apis.md` (or a short `docs/forge.md`), ARCHITECTURE.md.

**Checkpoint:** go / no-go with the spike numbers.
**Delegated:** timeout default, deck name mangling.
