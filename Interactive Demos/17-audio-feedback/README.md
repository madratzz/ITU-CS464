# Lab 17 — Sound & feedback bench

Compare a plain tone with designed pickup, impact, or footstep sounds. Tune pitch variation, layers, envelopes, volume, and feedback delay.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Press “Compare A → B” to hear a plain tone followed by the designed version. Toggle tonal and noise layers separately. Add 200 ms delay and notice how the sound disconnects from the visual event.

## Maths and assumptions

```
envelope: attack → exponential decay
pitch = base × 2^(variation / 12)
feedback time = event time + delay
```

A short envelope feels immediate; a longer decay adds weight. Pitch variation reduces repetition. The visual event happens immediately, while the sound follows the chosen delay. Audio is synthesized locally.

Keep volume modest and test in context. This is a synthetic sound-design sandbox, not a sample library. Nothing plays until you press a sound button; reset stops scheduled sounds.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
