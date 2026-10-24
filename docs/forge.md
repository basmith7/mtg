# Forge

[Forge](https://github.com/Card-Forge/forge) (GPL) is a free Java Magic engine with a rules engine
and an AI. `scripts/forge_sim.py` uses its headless `sim` mode to play the player's own decks against
each other offline. Its AI plays combo and politics badly: a pod result is a sparring read, never a
power verdict, and never at the player's table. Checked 2026-10-24 with Forge 2.0.15.

## Install (per machine, outside the repo)

- Unpack `forge-installer-<version>.tar.bz2` from the GitHub releases into `~/.local/share/forge`
  (or set `FORGE_HOME`). About 470 MB. No system packages: 2.0.15 starts on OpenJDK 25
  (`/usr/bin/java`) with `forge.sh`'s flags and no extra `--add-opens`.
- Add `forge.profile.properties` there with `userDir=./user/` and `cacheDir=./cache/`, or Forge
  creates `~/.forge` and `~/.cache/forge`.

## `sim` mode

`java -jar forge-gui-desktop-<v>-jar-with-dependencies.jar sim -D <dir> -d a.dck b.dck … -f Commander
-n <games> -c <seconds> -q`, run from the Forge directory. Flags come from `SimulateMatch.java`.

- `-d` names are file names inside `-D`; without `-D` Forge looks in its own user deck folder.
- Each game prints `Game Result: Game N ended in X ms. Ai(i)-<deck name> has won!`, or `Stopping slow
  match as draw` then `Game Result: Game N ended in a Draw! Took X ms.` when `-c` runs out.
- Cards Forge cannot resolve print `An unsupported card was requested: "<name>"` and are left out of
  the deck; the game still runs.
- Card names: Forge keeps `A // B` only for split cards (`AlternateMode:Split` in
  `res/cardsfolder/cardsfolder.zip`); modal, transforming and adventure cards go by their front face.
  `mtg/forge.py` converts our names.
- Stdout is large (AI warnings, unassigned-set notes); `forge.parse` reads only the lines above.

## Spike numbers (2026-10-24)

Krenko (goblins), Talrand (spells), Phage (voltron), Lathril (elves), `-n 5 -c 600`: see
`specs/deck-tools/slices/10-forge.md`.
