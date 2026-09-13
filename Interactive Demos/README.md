# Maths × Game Feel — Interactive Demos

Seventeen offline Three.js labs for students, instructors, and working game developers.

**Open `index.html` in a browser to start.** There is no installation, build step, server, CDN, or internet requirement. Each numbered folder contains its own HTML, JavaScript, styles, fonts, Three.js bundle, and licenses. Copy a whole numbered folder to share that lab independently.

| Lab | Topics | Experiments |
| --- | --- | --- |
| [01 — Dot product](01-dot-product/index.html) | Enemy sight, FOV, range, occlusion, tank aiming, signed angles, projection | Move a target behind a tank; obstruct its sight; enable turret tracking |
| [02 — Cross product](02-cross-product/index.html) | Aircraft orientation, local axes, perpendicular vectors, triangle normals, winding, area | Bank an aircraft; reverse operand order; deform a triangle |
| [03 — Jump lab](03-jump-lab/index.html) | Jump height/apex, fall gravity, short hops, coyote time, input buffering | Play the platformer; run repeatable late-jump and early-input trials; pause and step |
| [04 — Easing lab](04-easing-lab/index.html) | 12 easing curves, interpolation, overshoot, anticipation, velocity | Race four curves; scrub time; switch between position, rotation and scale |
| [05 — Game juice](05-game-juice/index.html) | Hit stop, squash/stretch, particles, shockwaves, camera shake, sound | Compare baseline and juiced hits; isolate effects; try subtle and arcade presets |
| [06 — Camera follow playground](06-camera-feel/index.html) | Compare rigid follow, smoothing, springs, dead zones, look-ahead, and speed-based zoom on the same moving subject. | Pause the subject, move its X position abruptly, and compare modes. Enable look-ahead, then speed zoom. Use the response slider to change how quickly the camera catches up. |
| [07 — Autonomous steering field](07-steering-behaviours/index.html) | Guide an agent with seek, flee, arrive, pursue, and evade. Inspect velocity, steering force, and obstacle avoidance. | Click the floor to move the target. Compare seek with arrive. Enable a moving target for pursue and evade. Turn obstacle avoidance off and on to inspect the additional steering vector. |
| [08 — Reflection & sliding bench](08-collision-maths/index.html) | Fire a ball at a wall and compare reflection with sliding. Change its normal, incidence angle, restitution, and tangential friction. | Set restitution to 1 and friction to 0: speed is preserved. Set restitution to 0, then compare with slide. Rotate the wall; the same calculation works in its new orientation. |
| [09 — Rotations & orientation](09-rotations/index.html) | Compare Euler interpolation, quaternion SLERP, and normalized quaternion LERP. Inspect the aligned axes that cause gimbal lock. | Scrub between the default headings and compare the noses. Switch to the gimbal experiment, set pitch to 90°, and change yaw and roll: the outer and inner rotation axes align. |
| [10 — Spring response bench](10-springs/index.html) | Explore stiffness, damping, and mass. Compare your spring with critical and overdamped references, then reuse its motion for recoil or a pop-in. | Set damping to zero, step the target, and watch persistent oscillation. Apply critical damping, then add an impulse. Switch the presentation between carriage, recoil, and scale. |
| [11 — Ballistics & interception](11-projectile-maths/index.html) | Explore gravity-driven arcs and leading a moving target. Compare a shot at the current position with an interception solution. | In interception mode, increase target velocity. Compare the teal shot at its original position with the orange leading shot. Raise gravity or reduce launch speed until the target becomes unreachable. |
| [12 — Local ↔ world transforms](12-coordinate-spaces/index.html) | Move a turret inside a translating, rotating, scaled parent. Compare its local coordinates with its world position and lock it in world space. | Change parent yaw and scale while holding the local X value fixed. Enable world-position lock, then move the parent: the local coordinates must change to keep the same world point. |
| [13 — Frame-rate comparison](13-time-steps/index.html) | Simulate 15, 30, 60, or 144 FPS and compare per-frame movement, delta-time movement, and a fixed-step accumulator under hitches. | Run the two-second trial at 15 FPS, then 144 FPS. Both time-based lanes should finish at speed × 2. Add 200 ms hitches and compare distance with the frame-count method. |
| [14 — Combat timing chamber](14-combat-feel/index.html) | Tune anticipation, active time, recovery, input buffering, knockback, and hit stop. Compare fast and heavy attacks against a training dummy. | Try nimble and heavy presets. Press again just before recovery ends, or use the repeatable combo trial. Remove the input buffer and repeat. Move the dummy outside the reach to see a miss. |
| [15 — Curve & arc-length editor](15-bezier-paths/index.html) | Drag Bézier control points for a camera rail or projectile path. Compare uniform parameter motion with approximately constant-speed travel. | Drag the inner handles close to one endpoint. The teal body speeds up and slows down. Pause and scrub, or choose a point and adjust X/Y with the sliders for keyboard access. |
| [16 — Two-bone IK & foot placement](16-inverse-kinematics/index.html) | Drag a foot target and solve a two-bone leg. Change limb lengths, bend direction, terrain slope, and body adjustment. | Drag the foot beyond reach and change the upper/lower lengths. Reverse the knee bend. Switch to terrain placement, change slope, and enable body adjustment to help the leg reach the ground. |
| [17 — Sound & feedback bench](17-audio-feedback/index.html) | Compare a plain tone with designed pickup, impact, or footstep sounds. Tune pitch variation, layers, envelopes, volume, and feedback delay. | Press “Compare A → B” to hear a plain tone followed by the designed version. Toggle tonal and noise layers separately. Add 200 ms delay and notice how the sound disconnects from the visual event. |

The launcher includes a text search and Maths / Movement / Game feel filters.

## Running and sharing

Use a modern browser with WebGL and hardware acceleration enabled. Open the collection’s `index.html`, or any numbered folder’s `index.html`, directly. The optional “All labs” navigation in an isolated copy points to the original parent collection; it is not a runtime dependency.

If your organization disables local HTML, serve either the collection or an individual lab:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000`. All resources still stay local. An embedded-browser preview can use the same local server.

## A suggested teaching sequence

1. **Predict before touching a slider.** What should the dot product be at 90°? Which way should a reversed cross product point?
2. **Change one variable.** Toggle a wall without changing FOV. Remove coyote time without changing the jump arc. Add squash before adding shake.
3. **Use the live measurements.** Distinguish normalized direction from distance, eased progress from time, and coyote time from input buffering.
4. **Transfer the result.** Ask learners to describe where they would use the technique in their own controller, AI, camera, UI, or combat system.

Allow roughly 10 minutes per lab, or use individual experiments during a lecture. Each lab includes formulas, a guided experiment, source notes, and a local README.

## Controls and conventions

- Maths labs: sliders/selectors; drag to orbit, scroll to zoom.
- Jump lab: A/D or arrow keys; Space/W/up to jump; release early for a short hop; R to reset. On-screen controls also work with touch. Keyboard shortcuts ignore focused form controls.
- Easing lab: play/pause, replay, and a time scrubber. Reduced-motion users start paused.
- Juice lab: click a target, press Space, or use “Trigger impact.” Sound is muted by default. Auto replay is opt-in.
- Distance uses metres and physics time uses seconds; forgiveness controls display milliseconds. The demos use +Y up and +Z forward for their models in Three.js’s right-handed coordinate system.

## Implementation notes

- Scenes use procedural geometry; no models, textures, or network assets are fetched.
- Each lab has its own copy of `lab.js` and `lab.css`, intentionally. If you change a shared helper, copy the change to the other labs too.
- Jump physics uses a 1/120-second fixed step with an accumulator. The teaching controller uses point-foot support and swept vertical landing checks, rather than a full rigid-body solver. Visual squash does not affect collisions. The ideal arc guide excludes release cuts and the falling-gravity multiplier.
- Easing functions live in `04-easing-lab/easing.js`. Back/elastic progress is allowed outside [0, 1]. The scale example has a small positive visual floor.
- Juice uses two independently rendered cameras; only the right one shakes. Hit stop freezes the juiced target animation and particles while shake continues. Sound uses the Web Audio API after user interaction.
- `window.demoState` exposes live teaching/debug values in each lab.
- Reset repositions the jump character while preserving tuned settings. The added labs use “Reset trial” to restart the experiment while preserving tuning; the coordinate-space and audio labs also restore their main defaults.

## Verification

The dependency-free simulation checks run with Node.js:

```sh
node --test tests/*.test.cjs
```

The optional browser suite needs Playwright and a Chromium browser. With Playwright installed and resolvable by Node:

```sh
node tests/browser.cjs
node tests/expansion-browser.cjs
```

Set `CHROME_PATH` to an installed Chrome executable to use it instead of Playwright’s browser. `DEMO_SCREENSHOTS` optionally selects the output directory; screenshots otherwise go to the operating system’s temporary directory. The suites check offline rendering, isolated-folder portability, UI interactions, mathematical cases, jump trials, reduced motion, and layouts at 390, 768 and 1440 pixels.

## Maintaining the added labs

Labs 06–17 also include local copies of `extras.js` (playback, graph, picking, and mesh helpers) and `models.js` (pure maths). Their source in lab 06 is the reference copy; propagate shared changes to all twelve folders.

`tools/build-expansion.py` rebuilds the added lab pages, local asset copies, README files, and catalog cards from its metadata. It does not overwrite the experiment-specific `app.js` files or the original five labs. Run it with Python 3 from any directory. Keep the local `models.js` and `extras.js` files when distributing a lab.

The interception solver uses a numerical search over 12 seconds; the two-bone IK solver works in a plane. These are teaching models, with their assumptions explained inside each lab. The audio lab generates sound using Web Audio and starts silently.

## Bundled dependencies and credits

- **Three.js 0.180.0**, MIT, vendored in every lab. See `assets/THREE-LICENSE.txt` in each numbered folder.
- **Instrument Sans** and **Space Mono**, SIL Open Font License, reused from the course’s embedded fonts. Their license files accompany every copy.
- Visual styling follows the repository’s course palette and type system.
- [Three.js Vector3 documentation](https://threejs.org/docs/pages/Vector3.html) and [rendering fundamentals](https://threejs.org/manual/en/fundamentals.html) provide API references.

To rebuild the classic offline Three.js bundle in a temporary tools directory, install `three@0.180.0` and `esbuild@0.28.2`. Bundle an entry containing `import * as THREE from 'three'; window.THREE = THREE;` using esbuild with `bundle: true`, `minify: true`, `format: 'iife'`, and `legalComments: 'eof'`. Copy that output to each lab’s `assets/three.min.js`, retaining Three.js’s license. The runnable labs themselves do not need these tools.
