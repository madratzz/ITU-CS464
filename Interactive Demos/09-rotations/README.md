# Lab 09 — Rotations & orientation

Compare Euler interpolation, quaternion SLERP, and normalized quaternion LERP. Inspect the aligned axes that cause gimbal lock.

## Run

Open `index.html` directly. This folder is self-contained, with local Three.js 0.180.0, fonts, scripts, and licenses. No network, build, or install is required. The optional “All labs” link points to the collection and can be ignored when sharing an isolated copy.

A modern browser with WebGL is required. If local HTML is restricted, run `python3 -m http.server 8000` here and open `http://localhost:8000`.

## Experiment

Scrub between the default headings and compare the noses. Switch to the gimbal experiment, set pitch to 90°, and change yaw and roll: the outer and inner rotation axes align.

## Maths and assumptions

```
q(t) = slerp(q₀, q₁, t)
q and −q represent the same rotation
YXZ lock: pitch = ±90°
```

Interpolating 170° to −170° as raw numbers takes a 340° route. Quaternion interpolation takes the 20° orientation path. SLERP has constant angular speed; normalized LERP usually does not.

Quaternions avoid an Euler parameter singularity, but cannot restore a degree of freedom to a physical three-gimbal mechanism. Euler input converted to a quaternion still inherits that input ambiguity.

## Source guide

- `app.js`: this experiment’s controls, scene and state.
- `models.js`: pure maths functions, shared as a local copy and covered by the collection’s tests.
- `extras.js`: animation controls, graphs, picking and model helpers.
- `lab.js` / `lab.css`: local course UI and rendering helpers.
- `assets/`: Three.js and course fonts, with their redistribution licenses.

`window.demoState` exposes measurements for teaching and automated checks. Animated demonstrations start paused for users who request reduced motion. Sound only starts after explicit interaction.
