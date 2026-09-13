# Lab 04 — Same journey. New feeling.

Race easing curves side by side. Scrub their motion, inspect overshoot, and apply the same curve to position, scale, or rotation.

## Run

Open `index.html` directly in a modern desktop browser with WebGL enabled. No internet, package installation, build, or server is needed. Touch controls are included where relevant. You can copy this entire folder elsewhere and run it independently. The optional “All labs” links point to the parent collection; they are not needed to run the demo.

If your environment restricts local files, run `python3 -m http.server 8000` in this folder and open `http://localhost:8000`.

## Classroom experiments

An ease maps normalized time to progress. The curve’s slope is velocity. A flat start accelerates gradually; a flat end settles gently. Progress velocity is measured per simulation second, before the playback-rate multiplier.

Compare Linear with Quad ease in and Quad ease out. Scrub Back ease out near 60–80%: progress exceeds 1. Then try Elastic and Bounce. Switch from position to scale to see why overshoot works well for a pop-in.

Ease camera transitions, UI, pickups, and deliberate movement. Keep player input responsive. Do not clamp eased progress if you want overshoot; only clamp time. Scale has a tiny visual floor to avoid an inverted mesh during anticipation.

## Source

- `app.js`: scene, interaction, and demonstration logic.
- `lab.js`: local UI and Three.js rendering helpers.
- `lab.css`: responsive styles and local font declarations.
- `assets/three.min.js`: Three.js 0.180.0, bundled as a classic script to support offline `file://` use; MIT license included.
- `assets/*.woff2`: Instrument Sans and Space Mono, reused from the course’s embedded fonts. See font license files.
 - `easing.js`: independently testable easing functions.

The browser exposes `window.demoState` for teaching and automated inspection. Keyboard shortcuts ignore form controls. The easing lab honors reduced-motion preferences by starting paused; impact and jump effects require interaction.

## References

- [Three.js Vector3 API](https://threejs.org/docs/pages/Vector3.html)
- [Three.js rendering fundamentals](https://threejs.org/manual/en/fundamentals.html)
