# Lecture 02 — Inside Unity

39 slides. The Unity Editor itself, then version control for game projects, then
the Scene/GameObject mental model — CLO-2, Bloom L2 (Understand). The Unity
Environment Tour now happens inside this lecture (Part 1) rather than in a
separate lab, so this deck opens with laptops-open editor tour before moving
into git and the scene graph.

**Deck:** [`CS464-Lecture-02-Inside-Unity.bento.html`](CS464-Lecture-02-Inside-Unity.bento.html)
— double-click to open. Every slide has speaker notes (`S` in present mode).

## What it covers

| Slides | Section |
|--------|---------|
| 1–4 | Cover, agenda, a 60-second recap of Lecture 01, today's CLO-2 outcomes |
| 5 | Section break — Unity Editor Overview |
| 6–11 | The editor at a glance, Scene View vs Game View, Hierarchy & Inspector, Project window & Console, the toolbar & transform tools, Play Mode's one gotcha |
| 12 | Section break — Version Control for Game Projects |
| 13–16 | The problem it solves, what version control is, why git specifically, git's three trees |
| 17–19 | The everyday loop — Edit & Stage, Commit, Sync — revealed as a walking chain |
| 20–21 | Branching, and merge conflicts (what one looks like, how to resolve it) |
| 22–26 | Why Unity projects are different, .gitignore, the .meta gotcha, Git LFS, common pitfalls & recovery |
| 27–28 | Workflow checklist, Version Control recap |
| 29 | Section break — Scene & GameObject Hierarchy |
| 30–35 | What is a Scene, GameObjects & Components, the Transform, parent-child hierarchy, organizing a scene, scenes at scale |
| 36 | Bringing it together — the worked example tying git and hierarchy into one commit |
| 37–39 | Key takeaways, next up, questions |

## Slides worth knowing about before you present

**The Editor at a Glance (6)** is a labelled mock of the default Unity layout —
Hierarchy, Scene/Game, Inspector, Project, Console, toolbar — colour-coded as a
preview of what's ahead: blue panels (Hierarchy, Inspector) come back in Part 3,
teal (Project window) comes back in Part 2. Walk the room through the real
editor on screen while this slide is up.

**Play Mode — The One Gotcha (11)** is worth a slide of its own for a reason:
"I changed something and it disappeared" is the single most common early
support question. The framing is that Play Mode is a sandbox, not a save —
changes made while playing revert the moment you stop.

**The everyday loop (17–19)** reuses Lecture 01's MDA-trio pattern: one shared
box that changes colour, and a three-step chain on the right whose highlight
walks down as you advance — Edit & Stage, Commit, Sync (push/pull).

**Branches (20)** is a from-scratch diagram, not adapted from Lecture 01: a
`main` line with commit dots, a `feature/double-jump` branch forking off and
merging back, both lines marching with dashed connectors at the fork/merge
points.

**Bringing It Together (36)** is the slide that ties the whole lecture
together — it's the first time version control and the scene hierarchy
visibly touch: adding a GameObject updates `Level01.unity` *and*
`Level01.unity.meta`, and that pairing is exactly what you stage and commit.

**Next Up (38)**'s Lecture 03 card is a placeholder ("Components & Your First
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

It needs `src/fonts/fonts.json`, `src/fonts/photo-asset.json` (copied from
Lecture 01 — same embedded typefaces and instructor photo, so the course reads
as one visual system), and `src/fonts/unity-logo-asset.json` (the official
Unity cube-logo mark, supplied by the instructor and embedded as a data URI —
used on the cover and the Part 1 section break). Paths at the bottom of the
script point at the deck; adjust them if you move things.

After any change, open the deck and run `window.bento.validate()` in the
browser console. It should report 0 errors and 0 warnings. It will not catch
overlapping elements or a panel that looks empty, so look at the slides too
— this build was checked by rendering every slide headlessly and reviewing
each one, same as Lecture 01's process.
