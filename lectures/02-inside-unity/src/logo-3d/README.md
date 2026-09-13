# Animated 3D Unity mark

The original instructor-supplied Unity PNG in `../fonts/unity-logo-asset.json`
provides the silhouette. The model extrudes that mark with bevels, a satin-silver
material and studio lighting. The Unity mark belongs to Unity Technologies.

## Current assembly animation

- `unity-logo-assembly.blend`: editable three-piece assembly scene.
- `unity-logo-assembly.webp`: transparent 512×512 animation embedded in the deck.
- `assembly-*.png`: selected frames for inspection.
- `outline.json`: contour derived from the original logo alpha channel.

The 12-second loop (720 rendered frames at 60 fps) holds assembled, separates with exponential ease-in (Expo-EaseIn), pauses, then returns with the same easing and 125 ms stagger.
At 5.25 seconds the completed assembly gets a small settling pulse and two
expanding, fading ripples. A quiet hold follows before the seamless repeat.
WebP uses repeating 16/17/17 ms frame durations for an average of 60 fps
and an exact 12-second loop. The encoder combines one identical pair during
the separated hold into a 33 ms frame (719 stored frames). Actual playback
depends on the viewer.
The assembled mark uses the original continuous geometry to avoid cut seams.

Rebuild with Python containing Pillow and Blender:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --threads 6 --python lectures/02-inside-unity/src/logo-3d/render_assembly.py
python3 lectures/02-inside-unity/src/logo-3d/encode_assembly.py
python3 lectures/02-inside-unity/src/build_doc.py
```

Temporary frames go to `/tmp/cs464-unity-assembly-60fps-frames`. Add `-- --preview`
to the Blender command to render four representative still frames.

## Previous turning variant

`unity-logo-3d.blend`, `unity-logo-3d.webp`, `render_logo.py`, `encode_logo.py`
and `preview.png` retain the earlier gentle-turn version as an alternative.
The original 2D logo also remains available in the deck assets.
