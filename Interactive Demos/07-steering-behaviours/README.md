# Lab 07 — Autonomous steering field

Guide an agent with seek, flee, arrive, pursue, and evade. Inspect velocity, steering force, and obstacle avoidance.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Click the floor to move the target. Compare seek with arrive. Enable a moving target for pursue and evade. Turn obstacle avoidance off and on to inspect the additional steering vector.

## Maths and assumptions

```
desired = direction × desiredSpeed
steering = clamp(desired − velocity)
velocity += steering × Δt
```

Seek heads toward the current target. Pursuit predicts its future position; evade moves away from that prediction. Arrive reduces desired speed near the target. This is a steering-force model with bounded acceleration.

Steering is local navigation, not pathfinding. This lab uses predictive obstacle steering and circle separation; crowded or maze-like levels usually need a global route as well.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
