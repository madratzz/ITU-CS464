# Lab 01 — See it. Aim at it.

Explore enemy detection, tank steering, and vector projection. Move the target and watch the decisions change.

## Run

Open `index.html` directly in a modern desktop browser with WebGL enabled. No internet, package installation, build, or server is needed. Touch controls are included where relevant. You can copy this entire folder elsewhere and run it independently. The optional “All labs” links point to the parent collection; they are not needed to run the demo.

If your environment restricts local files, run `python3 -m http.server 8000` in this folder and open `http://localhost:8000`.

## Classroom experiments

Both directions are normalized. The dot is +1 ahead, 0 perpendicular, and −1 behind. Detection also needs a range test and a clear line of sight.

Set the bearing to 90° and heading to 0°: the dot becomes zero. Put the target directly ahead, then add the wall. A positive dot alone does not guarantee visibility. Enable turret tracking to see steering.

With +Y up and +Z forward, a positive signed angle turns toward +X (right). The blue vector is signed forward displacement; use it to measure forward speed, aim alignment, or how far ahead an object lies.

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
