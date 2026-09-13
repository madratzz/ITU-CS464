# Lab 11 — Ballistics & interception

Explore gravity-driven arcs and leading a moving target. Compare a shot at the current position with an interception solution.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

In interception mode, increase target velocity. Compare the teal shot at its original position with the orange leading shot. Raise gravity or reduce launch speed until the target becomes unreachable.

## Maths and assumptions

```
p(t) = p₀ + v₀t + ½gt²
|r + v_target t − ½gt²| = speed × t
```

The leading solver searches for the earliest reachable flight time at the selected launch speed. It includes gravity and constant target velocity. If no solution exists within 12 seconds, the lab tells you.

Prediction is only as good as its assumptions. The target moves at constant velocity during each trial; acceleration and evasive movement require new estimates. Ballistic mode instead uses the chosen launch angle.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
