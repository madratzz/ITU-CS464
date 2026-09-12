# Lecture 02 — Inside Unity

32 slides. Version control for game projects, then the Scene/GameObject mental
model — CLO-2, Bloom L2 (Understand). Picks up exactly where Lecture 01's
"Next Up" slide left off; the Unity Environment Tour lab already happened, so
this lecture is entirely conceptual scaffolding for git and the scene graph.

**Deck:** [`CS464-Lecture-02-Inside-Unity.bento.html`](CS464-Lecture-02-Inside-Unity.bento.html)
— double-click to open. Every slide has speaker notes (`S` in present mode).

## What it covers

| Slides | Section |
|--------|---------|
| 1–4 | Cover, agenda, a 60-second recap of Lecture 01, today's CLO-2 outcomes |
| 5 | Section break — Version Control for Game Projects |
| 6–9 | The problem it solves, what version control is, why git specifically, git's three trees |
| 10–12 | The everyday loop — Edit & Stage, Commit, Sync — revealed as a walking chain |
| 13–14 | Branching, and merge conflicts (what one looks like, how to resolve it) |
| 15–19 | Why Unity projects are different, .gitignore, the .meta gotcha, Git LFS, common pitfalls & recovery |
| 20–21 | Workflow checklist, Version Control recap |
| 22 | Section break — Scene & GameObject Hierarchy |
| 23–28 | What is a Scene, GameObjects & Components, the Transform, parent-child hierarchy, organizing a scene, scenes at scale |
| 29 | Bringing it together — the worked example tying git and hierarchy into one commit |
| 30–32 | Key takeaways, next up, questions |

## Slides worth knowing about before you present

**The everyday loop (10–12)** reuses Lecture 01's MDA-trio pattern: one shared
box that changes colour, and a three-step chain on the right whose highlight
walks down as you advance — Edit & Stage, Commit, Sync (push/pull).

**Branches (13)** is a from-scratch diagram, not adapted from Lecture 01: a
`main` line with commit dots, a `feature/double-jump` branch forking off and
merging back, both lines marching with dashed connectors at the fork/merge
points.

**Bringing It Together (29)** is the slide that ties the whole lecture
together — it's the first time version control and the scene hierarchy
visibly touch: adding a GameObject updates `Level01.unity` *and*
`Level01.unity.meta`, and that pairing is exactly what you stage and commit.

**Next Up (31)**'s Lecture 03 card is a placeholder ("Components & Your First
Script", CLO-3) — the actual week-3 plan wasn't available when this deck was
built, so confirm and edit that card before presenting.

## Previews

Contact sheets: [`preview/`](preview/).

## Rebuilding the deck

The deck is generated, same as Lecture 01. `src/build_doc.py` writes the
document JSON into the `#bento-doc` block of the HTML file in place:

```bash
cd src && python3 build_doc.py
```

It needs `src/fonts/fonts.json` and `src/fonts/photo-asset.json` (copied
from Lecture 01 — same embedded typefaces and instructor photo, so the
course reads as one visual system). Paths at the bottom of the script point
at the deck; adjust them if you move things.

After any change, open the deck and run `window.bento.validate()` in the
browser console. It should report 0 errors and 0 warnings. It will not catch
overlapping elements or a panel that looks empty, so look at the slides too
— this build was checked by rendering every slide headlessly and reviewing
each one, same as Lecture 01's process (see `docs/build-log.md`).
