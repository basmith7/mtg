# 08 Primer extras and the challenger review

**Contract:** primers gain a signature turn, a mulligan guide and a politics note; a fresh-eyes subagent
reviews every deck before it is pushed. Docs and skill only, no code.

- `RULES.md` primer format: `## How it plays` ends with a short narrated **signature turn**; `## Tips`
  gains a mulligan line (keep rules grounded in the goldfish's keepable-7 rate from slice 06) and a
  politics line (from table feel, slice 03). Word budget: hold 300–500 by trimming elsewhere (default);
  raising it is the checkpoint.
- `.claude/skills/commander-deck/SKILL.md`: the build flow runs `table_feel.py` and `originality.py`
  next to the existing checks; before push, an unprimed subagent gets only the list, the primer,
  RULES.md and the player's profile and reports rule breaks, factual card errors and dull stretches.
  Idea from P47Phoenix/Claude-Plugins.
- Use `writing-for-agents` for the skill edit.

**Verify:** rewrite one existing primer (pull it; don't push unless Brian asks) and count its words.
**Checkpoint:** word budget, shown with the rewritten primer.

## Done (2026-10-24)

RULES.md primer format and the `commander-deck` skill updated. Test: the Etali primer rewritten under the
new format by an agent following only RULES.md and the skill (510 → 494 words), with the fresh-eyes
review. The review caught a real error the old primer had (tutors can't find the commander) and
showed the reviewer needs the scripts' output; both fixed here. Choices: [choices/08.md](../choices/08.md).
