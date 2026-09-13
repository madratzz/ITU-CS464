# Lab 16 — Two-bone IK & foot placement

Drag a foot target and solve a two-bone leg. Change limb lengths, bend direction, terrain slope, and body adjustment.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Drag the foot beyond reach and change the upper/lower lengths. Reverse the knee bend. Switch to terrain placement, change slope, and enable body adjustment to help the leg reach the ground.

## Maths and assumptions

```
cos(α) = (L₁² + d² − L₂²) / (2L₁d)
knee = hip + L₁ × direction(α)
clamp d to the reachable interval
```

The solver places the knee using the cosine rule and then connects it to the reachable foot point. Targets outside the limb’s reach are clamped; the orange target stays visible so you can inspect the error.

Foot placement also needs contact timing, stable bend hints, and joint limits in production. This leg solves in a 2D plane inside the 3D scene; it is not a complete walking controller.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
