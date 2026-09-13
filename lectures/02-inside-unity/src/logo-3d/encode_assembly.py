"""Encode Blender's RGBA frames as an offline-compatible animated WebP."""
from pathlib import Path
from PIL import Image, features
HERE=Path(__file__).resolve().parent
frames=sorted(Path('/tmp/cs464-unity-assembly-60fps-frames').glob('frame-*.png'))
assert len(frames)==720, f'Expected 720 frames, got {len(frames)}'
assert features.check('webp'), 'Pillow requires WebP support'
images=[Image.open(p).convert('RGBA') for p in frames]
assert all(im.size==(512,512) for im in images)
# WebP timestamps use integer milliseconds: 16/17/17 gives 60 fps on average.
images[0].save(HERE/'unity-logo-assembly.webp',save_all=True,append_images=images[1:],
               duration=[16,17,17]*240,loop=0,quality=85,method=3,alpha_quality=100,
               minimize_size=False)
images[360].save(HERE/'assembly-ripple.png')
print('Encoded',len(images),'frames;', (HERE/'unity-logo-assembly.webp').stat().st_size,'bytes')
