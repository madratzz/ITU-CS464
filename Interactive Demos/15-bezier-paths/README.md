# Lab 15 — Curve & arc-length editor

Drag Bézier control points for a camera rail or projectile path. Compare uniform parameter motion with approximately constant-speed travel.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Drag the inner handles close to one endpoint. The teal body speeds up and slows down. Pause and scrub, or choose a point and adjust X/Y with the sliders for keyboard access.

## Maths and assumptions

```
B(t) = (1−t)³P₀ + 3(1−t)²tP₁
       + 3(1−t)t²P₂ + t³P₃
constant speed: distance → lookup t
```

Equal changes in curve parameter t do not generally cover equal distances. A sampled arc-length table maps travelled distance back to t. The orange body uses that table; teal advances directly through t.

Use curves for authored camera paths and projectiles. The arc-length table is a numerical approximation with 400 segments; rebuild it when a control point moves.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
