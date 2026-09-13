# Lab 08 — Reflection & sliding bench

Fire a ball at a wall and compare reflection with sliding. Change its normal, incidence angle, restitution, and tangential friction.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Set restitution to 1 and friction to 0: speed is preserved. Set restitution to 0, then compare with slide. Rotate the wall; the same calculation works in its new orientation.

## Maths and assumptions

```
vₙ = (v · n̂)n̂; vₜ = v − vₙ
bounce = (1 − μ)vₜ − e vₙ
slide = (1 − μ)vₜ
```

A normal separates velocity into perpendicular and tangential components. Restitution e controls rebound; μ removes a fraction of tangential speed at this single contact. This is an impulse demonstration, not a full friction solver.

Use a normalized normal. Only resolve velocity directed into the surface. A positional correction keeps the sphere from remaining inside the wall after a simulation step.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
