# Lab 13 — Frame-rate comparison

Simulate 15, 30, 60, or 144 FPS and compare per-frame movement, delta-time movement, and a fixed-step accumulator under hitches.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Run the two-second trial at 15 FPS, then 144 FPS. Both time-based lanes should finish at speed × 2. Add 200 ms hitches and compare distance with the frame-count method.

## Maths and assumptions

```
wrong: x += speed / 60 per frame
variable: x += speed × frameDt
fixed: accumulate time; step at 120 Hz
```

The top lane assumes every rendered frame lasts 1/60 second. The others integrate elapsed time. The FPS control simulates an update cadence; it does not change your browser’s actual rendering rate.

Fixed steps make physics behaviour more consistent. Production games also need backlog limits and often interpolate the displayed pose. This small trial processes its full backlog so the accounting is visible.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
