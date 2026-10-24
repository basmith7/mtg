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

## Done (2026-10-24): go

Spike, Forge 2.0.15 on OpenJDK 25 (`/usr/bin/java`, no system packages), Krenko (goblins), Talrand
(spells), Phage (voltron), Lathril (elves), `-n 5 -c 600 -q`:
- **Starts on JDK 25** with `forge.sh`'s flags, no extra `--add-opens` (only `sun.misc.Unsafe`
  deprecation warnings). Card DB loads in ~6 s.
- **5 games in 144 s wall; games took 17.1, 22.2, 23.2, 28.2, 47.2 s** (mean 27.6 s).
- **Draws: 0/5.** Wins: Talrand 2, Lathril 2, Krenko 1, Phage 0.
- **Unsupported cards: 4** (Krenko 1, Talrand 1, Lathril 2), all modal/transform DFCs written `A // B`;
  after `card_name` uses the front face, 0. A follow-up `forge_sim.py` run (n=2) reported none.
- Kill criteria not met. Fixture: `tests/fixtures/forge_sim_4pod.txt` (real run, noise lines trimmed).
- Not verified: a split card (`Fire // Ice`) loading in a sim; Forge's RAM at 4 GB `-Xmx` beyond this pod.
