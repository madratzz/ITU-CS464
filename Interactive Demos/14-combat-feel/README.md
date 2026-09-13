# Lab 14 — Combat timing chamber

Tune anticipation, active time, recovery, input buffering, knockback, and hit stop. Compare fast and heavy attacks against a training dummy.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Try nimble and heavy presets. Press again just before recovery ends, or use the repeatable combo trial. Remove the input buffer and repeat. Move the dummy outside the reach to see a miss.

## Maths and assumptions

```
startup → active → recovery → ready
press during recovery → buffer
hit once per swing, only while active
```

Startup telegraphs intent; active time can deal a hit; recovery creates commitment. The input buffer queues a future attack, not an immediate cancel. Hit stop freezes combat motion but still accepts input.

Keep collision windows separate from animation appearance. This simplified sector hit test only damages once per swing; health, movement, and defensive mechanics can be added around the same state machine.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
