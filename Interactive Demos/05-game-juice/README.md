# Lab 05 — Let the hit land.

Compare a bare interaction with a layered impact. Add hit stop, squash, particles, flash, and camera shake one effect at a time.

## Run

Open `index.html` directly in a modern desktop browser with WebGL enabled. No internet, package installation, build, or server is needed. Touch controls are included where relevant. You can copy this entire folder elsewhere and run it independently. The optional “All labs” links point to the parent collection; they are not needed to run the demo.

If your environment restricts local files, run `python3 -m http.server 8000` in this folder and open `http://localhost:8000`.

## Classroom experiments

The left side receives the same projectile hit. The right adds presentation effects: a brief hit stop, an elastic recovery, pooled particles, a shockwave, and a decaying shake on its own camera.

Choose “All effects off”, trigger an impact, then enable only squash. Add a 60 ms stop. Finally add particles and shake. Compare “Subtle” with “Arcade”: more feedback is not automatically more readable.

This demo pauses the juiced target and particles, while camera shake continues in real time. In a game, choose which systems freeze. Hit stop must not stall input collection or UI. Sound is optional, synthesized locally, and muted until enabled.

## Source

- `app.js`: scene, interaction, and demonstration logic.
- `lab.js`: local UI and Three.js rendering helpers.
- `lab.css`: responsive styles and local font declarations.
- `assets/three.min.js`: Three.js 0.180.0, bundled as a classic script to support offline `file://` use; MIT license included.
- `assets/*.woff2`: Instrument Sans and Space Mono, reused from the course’s embedded fonts. See font license files.

The browser exposes `window.demoState` for teaching and automated inspection. Keyboard shortcuts ignore form controls. The easing lab honors reduced-motion preferences by starting paused; impact and jump effects require interaction.

## References

- [Three.js Vector3 API](https://threejs.org/docs/pages/Vector3.html)
- [Three.js rendering fundamentals](https://threejs.org/manual/en/fundamentals.html)
