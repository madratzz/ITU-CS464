"""Trace the existing logo's alpha outline for deterministic 3D extrusion."""
import base64, io, json, math
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
source=json.loads((HERE.parent/'fonts/unity-logo-asset.json').read_text())['logo-unity']
im=Image.open(io.BytesIO(base64.b64decode(source.split(',',1)[1]))).convert('RGBA')
w,h=im.size
pixels=im.load()
filled={(x,y) for y in range(h) for x in range(w) if pixels[x,y][3]>=128}
edges={}
for x,y in filled:
    for adjacent,a,b in [((x,y-1),(x,y),(x+1,y)),((x+1,y),(x+1,y),(x+1,y+1)),((x,y+1),(x+1,y+1),(x,y+1)),((x-1,y),(x,y+1),(x,y))]:
        if adjacent not in filled:edges[a]=b
loops=[]
while edges:
    start=next(iter(edges));p=start;loop=[]
    while True:
        loop.append(p);p=edges.pop(p)
        if p==start:break
    loops.append(loop)
def simplify(points,eps=1.6):
    if len(points)<3:return points
    a,b=points[0],points[-1];dx=b[0]-a[0];dy=b[1]-a[1];den=math.hypot(dx,dy)
    distances=[abs(dy*(p[0]-a[0])-dx*(p[1]-a[1]))/den if den else math.dist(p,a) for p in points]
    i=max(range(len(points)),key=distances.__getitem__)
    if distances[i]>eps:return simplify(points[:i+1],eps)[:-1]+simplify(points[i:],eps)
    return [a,b]
out=[]
for loop in loops:
    half=len(loop)//2
    poly=simplify(loop[:half+1])[:-1]+simplify(loop[half:]+[loop[0]])[:-1]
    out.append([[(x-w/2)/h*3,(h/2-y)/h*3] for x,y in poly])
(HERE/'outline.json').write_text(json.dumps(out,indent=2)+'\n')
print('Outlined',len(out),'contours;',sum(map(len,out)),'vertices')
