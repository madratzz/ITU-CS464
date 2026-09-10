# CS464 lecture decks — visual system

Conventions Lecture 01 established. Follow them when building Lecture 02 onward so
the series looks like one course, not fifteen unrelated slide decks.

## Typefaces

Both faces are embedded in the document as woff2 data URIs under `doc.assets`, and
declared in `doc.fonts`. A `fontFamily` the document does not carry falls back
silently, so new decks must copy the `assets` and `fonts` blocks across rather than
naming the families and hoping. This is worth being strict about: a missing face
looks correct on the machine of whoever has it installed, which is usually you.

- Display and body: **Instrument Sans** (variable, 100–900), written as
  `'Instrument Sans', 'Helvetica Neue', Arial, sans-serif`. Titles at weight 800.
- Labels, kickers, footers, code-ish text: **Space Mono** (400 and 700), written as
  `'Space Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace`, almost always
  uppercase with `letterSpacing` between 1.5 and 3.

## Palette

Background `#14171C`, surfaces `#1B2027` and `#232A34`, text `#EEF1F5`,
muted `#9AA2B1`, faint `#5C6472`.

Four accents, used to mean something rather than to decorate:

| Colour | Hex | Means |
|--------|-----|-------|
| Orange | `#FF8A3D` | The course itself; Act I; "what you build"; Achievers |
| Teal | `#55D6C2` | Act II; "what emerges"; Socializers |
| Blue | `#6C8CFF` | Act III; "what they feel"; Explorers |
| Magenta | `#FF4FA3` | Act IV, shipping, anything celebratory; Killers |

Each has a `_SOFT` fill at 14% and a `_GLOW` at 50–55%. Keep the mappings — a
student who learns "teal is Act II" on slide 6 should not find teal meaning
something else on slide 28.

## The three moves that carry the deck

1. **Glow.** Every accent-coloured disc, rule or badge carries a `shadow`
   (`{blur, color}` with the matching `_GLOW`). On a dark ground this is the single
   biggest difference between "a slide" and "a designed slide".
2. **Gradient.** Discs and badges use `fillGradient` between an accent and its
   neighbour — orange→amber, teal→cyan, blue→violet, magenta→coral.
3. **Motion that never stops.** Dashed rings with `fx.loop.dash-march`, and small
   bodies riding `fx.loop.motion-path` circles generated relative to their resting
   position. Never put an `fx.enter` on a motion-path element; they fight.

Neither `shadow` nor `fillGradient` appears in the published schema, but every
official Bento template uses both heavily and they render correctly.

## The orbit motif

The deck's signature. A marching dashed ring, a fainter inner ring, a glowing
gradient core, and three bodies at different radii and speeds. It appears on the
cover, on both section breaks, and on the closing slide — and, as the actual subject
matter, on the magic circle slide, where the ring *is* the boundary, the core is the
game, the bright bodies are players inside it and the grey ones are ordinary life
still turning outside.

`orbit_motif()` and `body()` in the Lecture 01 generator produce it.

## Layout

1280×720, 96px side margins, so the right-most edge is x=1184. Title band around
y=64–184; content from y≈208; footer at y=664.

Footers use the dynamic tokens `{{page:2}} / {{pages}}`, which resolve at render
time and exclude hidden state slides — so re-cutting a deck never desynchronises the
numbering, and drill-down slides don't inflate the count the room sees.

## Structural patterns worth reusing

- **Two-page reveal by morph.** Keep the same element ids across both slides and
  change only their properties; the second slide gets `transition: "morph"`. The
  15-week arc uses it to light up acts III and IV; the grading breakdown uses it to
  bring in the second column of components. Changing properties beats sliding new
  elements in — the audience sees the same object change state.
- **A walking highlight.** The three MDA slides share one content box (`mdabox`,
  which tweens colour) and a three-row chain on the right whose active row moves
  down. Three slides read as one idea in three positions.
- **Expand-in-place with state slides.** The Bartle matrix does this: four quadrants
  each carry `link` to a hidden slide whose `stateOf` names the matrix. On that state
  slide the clicked quadrant's rect and label keep their ids and are re-declared at
  full-panel size, so the morph physically expands it, while the other three are
  re-declared tiny inside a locator grid in the corner with a dashed marker in the
  vacated cell. Arrow keys skip state slides, so the linear lecture is untouched and
  the detail is there only if the room asks for it.
- **Never leave a big empty container.** An under-filled card reads as a bug. Size
  boxes to their content, or give the space a job.

## Gotchas found the hard way

- Do **not** implement "click anywhere to go back" as a full-canvas invisible rect
  carrying the link. The player styles link targets with a pill affordance, so a
  1280×720 hit rect draws an enormous accent-coloured ellipse across the slide
  whenever the cursor is over it. Use a small visible back button.
- charts-lite honours `"label": false` and `"legend": false` as literal booleans. The
  object form `{"show": false}` is silently ignored.
- Elements that have a morph partner skip `fx.enter` and `fx.countUp`. Setting them
  anyway earns an `overridden-enter-fx` warning, so build helpers with a "no fx"
  variant for an element's repeat appearance.
- charts-lite has no bar-grow animation and no per-item bar colours. Both bar charts
  in Lecture 01 are hand-built from rects and text with a staggered `fx.enter`.
- A freshly downloaded Bento template ships with an **empty** `#bento-doc` block —
  its showcase deck is minted by the app on first open. Read it from
  `window.bento.doc` in a browser, not by grepping the file.

## Checking the work

`window.bento.validate()` in the browser console must come back with 0 errors and
0 warnings. It does not catch overlap, a panel that looks empty, or a clipped chart
label, so also render every slide and look at it — most of the fixes in Lecture 01
came from the screenshots, not the validator.
