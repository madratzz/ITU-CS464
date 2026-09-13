# Lab 10 — Spring response bench

Explore stiffness, damping, and mass. Compare your spring with critical and overdamped references, then reuse its motion for recoil or a pop-in.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Set damping to zero, step the target, and watch persistent oscillation. Apply critical damping, then add an impulse. Switch the presentation between carriage, recoil, and scale.

## Maths and assumptions

```
a = (k(target − x) − cv) / m
c_critical = 2√(km)
ζ = c / c_critical
```

Below ζ = 1, a spring oscillates around its target. At critical damping it returns without oscillation; above it, recovery is slower. The reference lanes use the same stiffness and mass.

Springs can drive camera lag, weapon recovery, and UI motion. This numerical simulation runs at 240 Hz; extreme parameters still require an appropriate solver and timestep.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
