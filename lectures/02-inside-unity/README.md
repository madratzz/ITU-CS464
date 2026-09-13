# Lecture 02 — Inside Unity

41 slides. Version control for game projects comes first this term, then the
Unity Editor itself, then the Scene/GameObject mental model — CLO-2, Bloom L2
(Understand). The Unity Environment Tour happens inside this lecture (Part 2)
rather than in a separate lab.

**Deck:** [`CS464-Lecture-02-Inside-Unity.bento.html`](CS464-Lecture-02-Inside-Unity.bento.html)
— double-click to open. Every slide has speaker notes (`S` in present mode).

## What it covers

| Slides | Section |
|--------|---------|
| 1–4 | Cover, agenda, a 60-second recap of Lecture 01, today's CLO-2 outcomes |
| 5 | Section break — Version Control for Game Projects |
| 6–9 | The problem it solves, what version control is, why git specifically, git's three trees |
| 10–12 | The everyday loop — Edit & Stage, Commit, Sync — revealed as a walking chain |
| 13 | Remotes & the GitHub workflow — origin, clone, push/pull, made explicit |
| 14–15 | Branching, and merge conflicts (what one looks like, how to resolve it) |
| 16 | Pull requests & code review — push branch, open PR, review, merge |
| 17–21 | Why Unity projects are different, .gitignore, the .meta gotcha, Git LFS, common pitfalls & recovery |
| 22–23 | Workflow checklist, Version Control recap |
| 24 | Section break — Unity Editor Overview |
| 25–30 | The editor at a glance, Scene View vs Game View, Hierarchy & Inspector, Project window & Console, the toolbar & transform tools, Play Mode's one gotcha |
| 31 | Section break — Scene & GameObject Hierarchy |
| 32–37 | What is a Scene, GameObjects & Components, the Transform, parent-child hierarchy, organizing a scene, scenes at scale |
| 38 | Bringing it together — the worked example tying git and hierarchy into one commit |
| 39–41 | Key takeaways, next up, questions |

## Slides worth knowing about before you present

**The order** is deliberate: version control (Part 1) comes before the Unity
Editor Overview (Part 2) this term, so students have the git vocabulary in
hand before the editor tour, and the tour itself can point at git-tracked
folders as a callback rather than a preview. Scene & GameObject Hierarchy
stays last (Part 3) either way.

**The cover and Part 2 section break (1, 24)** carry the deck's ambient
motif: a dashed ring marches slowly around the Unity logo, with a soft
breathing glow behind it — teal on the cover, orange on the Part 2 break.

**The everyday loop (10–12)** reuses Lecture 01's MDA-trio pattern: one
shared box that changes colour, and a three-step chain on the right whose
highlight walks down as you advance — Edit & Stage, Commit, Sync (push/pull).

**Remotes & the GitHub Workflow (13)** finally names what "push" and "pull"
have been pointing at since the Sync slide: a local-repo box and a GitHub
("origin") box with animated push/pull arrows between them, plus the explicit
`git clone` / `git remote -v` / `git push origin main` commands. Sets up
today's lab, which starts with `git clone`.

**Branches (14)** is a from-scratch diagram, not adapted from Lecture 01: a
`main` line with commit dots, a `feature/double-jump` branch forking off and
merging back, both lines marching with dashed connectors at the fork/merge
points.

**Pull Requests & Code Review (16)** is the piece that turns "I know git
commands" into "I can work on a team repo" — a four-step push → open PR →
review → merge card row, plus a "why bother" callout. Most students have only
ever pushed straight to `main`; worth demoing live on GitHub if you have a
projector handy.

**The Editor at a Glance (25)** is a labelled mock of the default Unity
layout — Hierarchy, Scene/Game, Inspector, Project, Console, toolbar — that
reveals panel by panel in a guided-tour order as you advance, with the
Scene/Game panel carrying a slow breathing glow. Colour does double duty:
the teal Project panel is now a *callback* to Part 1's version control
(students already know what that folder is), and the blue Hierarchy/
Inspector panels *preview* Part 3.

**Play Mode — The One Gotcha (30)** is worth a slide of its own for a
reason: "I changed something and it disappeared" is the single most common
early support question. The framing is that Play Mode is a sandbox, not a
save — changes made while playing revert the moment you stop.

**Bringing It Together (38)** is the slide that ties the whole lecture
together — it's the first time version control and the scene hierarchy
visibly touch: adding a GameObject updates `Level01.unity` *and*
`Level01.unity.meta`, and that pairing is exactly what you stage and commit.

**Next Up (40)**'s Lecture 03 card is a placeholder ("Components & Your First
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
used on the cover and the Part 2 section break). Paths at the bottom of the
script point at the deck; adjust them if you move things.

After any change, open the deck and run `window.bento.validate()` in the
browser console. It should report 0 errors and 0 warnings. It will not catch
overlapping elements or a panel that looks empty, so look at the slides too
— this build was checked by rendering every slide headlessly and reviewing
each one, same as Lecture 01's process.
