# Lab 03 — Make the jump feel right.

Play with jump arcs, variable height, coyote time, and input buffering. Test the tiny timing windows that make movement feel responsive.

## Run

Open `index.html` directly in a modern desktop browser with WebGL enabled. No internet, package installation, build, or server is needed. Touch controls are included where relevant. You can copy this entire folder elsewhere and run it independently. The optional “All labs” links point to the parent collection; they are not needed to run the demo.

If your environment restricts local files, run `python3 -m http.server 8000` in this folder and open `http://localhost:8000`.

## Classroom experiments

Height and time to apex define the rising arc. Higher falling gravity shortens descent; releasing jump early cuts upward velocity. The orange guide shows the ideal continuous, symmetric arc, before those modifiers.

Coyote time accepts a jump shortly after leaving an edge. Buffering remembers a press shortly before landing. Run each trial, set its window to zero, and repeat. The coyote trial presses ~80 ms late; the buffer trial presses ~70 ms early.

Consume both allowances when jumping so coyote time cannot become a second jump. Physics runs at 120 Hz, independent of render rate. Pause and step to inspect a frame; tune windows in milliseconds, not frame counts.

## Source

- `app.js`: scene, interaction, and demonstration logic.
- `lab.js`: local UI and Three.js rendering helpers.
- `lab.css`: responsive styles and local font declarations.
- `assets/three.min.js`: Three.js 0.180.0, bundled as a classic script to support offline `file://` use; MIT license included.
- `assets/*.woff2`: Instrument Sans and Space Mono, reused from the course’s embedded fonts. See font license files.
 - `physics.js`: independently testable fixed-step jump simulation.

The browser exposes `window.demoState` for teaching and automated inspection. Keyboard shortcuts ignore form controls. The easing lab honors reduced-motion preferences by starting paused; impact and jump effects require interaction.

## References

- [Three.js Vector3 API](https://threejs.org/docs/pages/Vector3.html)
- [Three.js rendering fundamentals](https://threejs.org/manual/en/fundamentals.html)
