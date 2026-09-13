# Lab 06 — Camera follow playground

Compare rigid follow, smoothing, springs, dead zones, look-ahead, and speed-based zoom on the same moving subject.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Pause the subject, move its X position abruptly, and compare modes. Enable look-ahead, then speed zoom. Use the response slider to change how quickly the camera catches up.

## Maths and assumptions

```
smooth: α = 1 − exp(−λ Δt)
spring: a = (k(target − x) − cv) / m
```

A camera balances framing, responsiveness, and continuity. Exponential smoothing uses elapsed time; a spring carries velocity and can overshoot. The wireframe box marks the dead zone in world space.

Keep look-ahead bounded. Consider camera behaviour during sudden reversals, teleports, and stops. A dead zone ignores small movements until the subject crosses its boundary.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
