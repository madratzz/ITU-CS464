"""Encode Blender's RGBA frames as an offline-compatible animated WebP."""
from pathlib import Path
from PIL import Image, features
HERE=Path(__file__).resolve().parent
frames=sorted(Path('/tmp/cs464-unity-3d-frames').glob('frame-*.png'))
assert len(frames)==192, f'Expected 192 frames, got {len(frames)}'
assert features.check('webp'), 'Pillow requires WebP support'
images=[Image.open(p).convert('RGBA') for p in frames]
assert all(im.size==(512,512) for im in images)
# Alternating durations preserve the exact 12-second period at 16 fps.
images[0].save(HERE/'unity-logo-3d.webp',save_all=True,append_images=images[1:],
               duration=[62,63]*96,loop=0,quality=85,method=3,alpha_quality=100,
               minimize_size=False)
images[24].save(HERE/'preview.png')
print('Encoded',len(images),'frames;', (HERE/'unity-logo-3d.webp').stat().st_size,'bytes')
