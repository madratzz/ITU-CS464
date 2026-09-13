# Lecture 02 — Inside Unity

41 main slides, with 13 optional animation states. Covers version control,
the Unity Editor, and Scene/GameObject hierarchy (CLO-2).

**[Open the deck](CS464-Lecture-02-Inside-Unity.bento.html).** All screenshots and
fonts are embedded, so presentation works offline. Use the on-slide controls
in presentation mode to run the examples. Arrow keys continue the main lecture;
they skip optional states. Press `S` for speaker notes.

## Teaching animations

| Slide | Control | What students should notice |
|---|---|---|
| 9 | Stage this version → Edit again → Commit and reveal | Working content changes to 8, but the staged value stays 6 and the commit records 6. |
| 10–12 | Advance the main slides | The same workflow highlight morphs from editing to committing to syncing. |
| 25 | Next panel / Replay tour | A highlight moves across the real Hierarchy, Inspector, Scene and Project panels. |
| 27 | Show Inspector / Replay selection | The highlight connects a scene selection with the object's components. |
| 28 | Open Console example / Back to Project | Large screenshots distinguish browsing assets from investigating diagnostics. |
| 30 | Enter Play + change X → Stop and reveal | The illustrative scene-object X value changes 0 → 3 → 0. Asset changes may persist. |
| 34 | Next property / Replay properties | The highlight walks through Position, Rotation and Scale in a real Inspector screenshot. |
| 35 | Move parent +3 / Reset positions | Parent and child move together. Child local X stays 1 while world X changes 3 → 6. |

Pause before revealing the result on slides 9, 30 and 35 and ask students to
predict it. Screenshot pixels remain unchanged; numerical teaching examples and
highlights are separate editable slide elements. Repeated editor images let
students follow the same workspace across related concepts.

## Ambient animation

Slides **1, 5, 24, 31 and 41** have faint drifting particles, a soft breathing
accent glow, and a beveled 3D Unity logo that separates into three sections,
then eases back together inside a slowly moving dashed ring. A small settling
pulse and two expanding, fading ripples emphasize the completed assembly.
The pieces return with a slight stagger, followed by a quiet hold. The model extrudes the original logo silhouette, with
a satin-silver material and soft studio lighting. Its transparent animated WebP
loops every 12 seconds (720 frames at 60 fps). Ring loops take 24 seconds;
particle loops take 28–53 seconds.

Content slides use just two low-opacity particles in the outer margins. These
effects stay clear of the screenshots and teaching content. Optional teaching
states share the same background element ids to preserve continuity. The logo animation is embedded once and reused by all five slides. It needs no
video controls or autoplay permission; the remaining effects use the embedded
Bento runtime. No internet connection is needed.

The editable Blender scene, rendered animation, and reproducible source scripts
are in [`src/logo-3d/`](src/logo-3d/).

## Content map

| Slides | Section |
|---|---|
| 1–4 | Introduction, recap and the course outline's CLO-2 |
| 5–23 | Git model, workflow, remotes, branches, review and Unity project files |
| 24–30 | Actual Unity Editor screenshots and guided examples |
| 31–37 | Scenes, components, transforms, parenting and organization |
| 38–41 | Worked commit, takeaways, upcoming topics and questions |

The upcoming topics follow the course outline's sequence: components, lights,
materials and prefabs before C# scripting. No unconfirmed Lecture 03 date or
scope is asserted.

## Screenshot sources

Ten PNGs from Unity's official documentation are embedded. The original downloads
and per-image source URLs are in [`src/screenshots/`](src/screenshots/), with a
machine-readable [`sources.json`](src/screenshots/sources.json). Unity Technologies
owns the source images. Sources also appear in the relevant speaker notes.

The editor overview is a real custom layout, not the default layout. The toolbar
screenshot is labelled **Unity 6 Preview**, as shown in Unity's manual. Panel
placement and appearance can vary with the installed version. Scene/Game view
comparison images come from different example scenes, explicitly labelled.

## Rebuilding

```sh
python3 lectures/02-inside-unity/src/build_doc.py
```

The generator updates only the `#bento-doc` JSON block in the HTML. Its inputs
are the embedded fonts, instructor photo, Unity logo, and the downloaded PNGs.
No internet connection is needed to rebuild.

## Review status and previews

The revision corrects scene/meta behavior, text serialization and Smart Merge,
Game-view gizmos, Play Mode asset exceptions, Transform terminology, hierarchy
costs, Git snapshot semantics, LFS setup, branch geometry and the upcoming topics.

The embedded Bento structural validator was run without a browser: **0 errors,
0 warnings, 0 informational findings**. All slide/state layouts were checked
with an independent static render using fallback fonts, and text-fit checks
reported no overflow. These checks do not establish live animation behavior.

[`preview/`](preview/) contains current **static layout previews**, including
optional states. They use fallback fonts and omit animation, glow and some
Bento-specific styling. Browser security policy blocked opening the local deck,
so live playback and browser text measurements remain unverified. For the final
presentation check, open the deck normally, use the controls listed above, and
run `window.bento.validate()` in the browser console if desired.
