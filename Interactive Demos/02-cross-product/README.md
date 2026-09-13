# Lab 02 — Find your orientation.

Bank an aircraft, reconstruct its local frame, and discover how triangle winding changes a surface normal.

## Run

Open `index.html` directly in a modern desktop browser with WebGL enabled. No internet, package installation, build, or server is needed. Touch controls are included where relevant. You can copy this entire folder elsewhere and run it independently. The optional “All labs” links point to the parent collection; they are not needed to run the demo.

If your environment restricts local files, run `python3 -m http.server 8000` in this folder and open `http://localhost:8000`.

## Classroom experiments

The cross product returns a vector perpendicular to its inputs. Parallel inputs give zero, so they cannot define a unique normal. The blue arrow shows direction; triangle normals are drawn at a fixed length for readability.

Level the aircraft: +Z forward × +X right gives +Y up. Add pitch and roll, then reverse the order. Switch to the triangle and move vertex B; the normal stays perpendicular to both edges.

Use normals for lighting, slopes and contact orientation; use a local basis for aircraft controls. This lab uses Three.js’s right-handed frame, with the aircraft nose along local +Z. Check axis and winding conventions when porting.

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
