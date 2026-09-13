# Lab 12 — Local ↔ world transforms

Move a turret inside a translating, rotating, scaled parent. Compare its local coordinates with its world position and lock it in world space.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Change parent yaw and scale while holding the local X value fixed. Enable world-position lock, then move the parent: the local coordinates must change to keep the same world point.

## Maths and assumptions

```
worldPoint = parentMatrix × localPoint
localPoint = inverse(parentMatrix) × worldPoint
```

A local offset follows the parent’s translation, rotation, and scale. World coordinates describe its position in the scene. Inverting the parent transform converts a world-space point back into local coordinates.

Use points for positions and directions for orientation or motion. Translation affects points, not direction vectors. This lab locks position only; the turret’s orientation still inherits its parent.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
