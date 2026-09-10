# CS464 — Game Development

Course materials for **CS464 Game Development**, Information Technology University
(ITU), Fall 2025. Taught by Muhammad Raza Butt.

The course is practical and project-based: fifteen weeks that start with design
theory, open Unity in week four, and end with each student presenting a game only
they made. Lecture slides live here as self-contained Bento decks — one HTML file
each, no build step, no dependencies, no internet needed to present.

> **Note on the repo name.** The official course outline says **CS464**; this
> repository is named `ITU-CS646`. File names follow the outline. Worth renaming one
> or the other so they agree.

## Layout

```
course/       the official course outline (source of truth for CLOs and grading)
lectures/     one folder per lecture: the deck, its source, and slide previews
docs/         the deck design system, and a log of how Lecture 01 was built
templates/    reference Bento decks used as design source material
```

## Lectures

| # | Title | Deck | Covers |
|---|-------|------|--------|
| 01 | The Anatomy of Play | [`lectures/01-anatomy-of-play/`](lectures/01-anatomy-of-play/) | Course logistics, the 15-week arc, grading, what a game is, the magic circle, rules of play, finite vs infinite games, MDA, the 8 kinds of fun, Bartle's taxonomy |

## Opening a deck

Double-click the `.bento.html` file. It opens in any browser and boots straight
into the editor with the deck loaded — the Bento app ships inside the file itself,
so there is nothing to install and nothing to fetch.

- `→` / `←` move through slides, `Esc` toggles the editor, `S` opens speaker view
  with the presenter notes.
- Some slides are clickable. On Bartle's taxonomy, clicking a quadrant expands it
  into a full brief; arrow keys skip those, so they only appear if you want them.
- Every slide carries speaker notes. They are the actual teaching script, not a
  restatement of what is on screen.

## Editing a deck

The whole document is JSON in a single `<script type="application/bento+json"
id="bento-doc">` block inside the HTML file. You can edit visually in the browser
and save, or edit the JSON directly.

Lecture 01 is *generated* rather than hand-edited — see
[`lectures/01-anatomy-of-play/src/`](lectures/01-anatomy-of-play/src/). Change the
Python, re-run it, and it rewrites the JSON block in place. If you edit that deck
by hand in the browser, the generator becomes stale, so pick one.

## Conventions

Anything that gets built for this course should follow
[`docs/deck-design-system.md`](docs/deck-design-system.md) — typefaces, palette,
the motion vocabulary, and the layout grid. The point is that fifteen lectures look
like one course rather than fifteen unrelated slide decks.
