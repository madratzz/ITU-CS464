"""Render a 12-second 60 fps Expo-EaseIn three-piece assembly with two fading impact ripples."""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
OUT=Path('/tmp/cs464-unity-assembly-60fps-frames');OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
FPS=60;FRAME_COUNT=12*FPS
scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=FRAME_COUNT
scene.world=bpy.data.worlds.new('Studio world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.36,.42,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
mat=bpy.data.materials.new('Satin silver');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.82,.86,.9,1)
bsdf.inputs['Metallic'].default_value=.52;bsdf.inputs['Roughness'].default_value=.26
root=bpy.data.objects.new('Assembly root',None);scene.collection.objects.link(root)
root.rotation_euler=(math.radians(4),math.radians(-9),0)
outline=json.loads((HERE/'outline.json').read_text())[0]
def clip(poly,a,b):
    """Clip an outline to a*x+b*y >= 0, retaining its winding."""
    result=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp=a*p[0]+b*p[1];dq=a*q[0]+b*q[1]
        if dp>=-1e-9:result.append(p)
        if (dp>=0)!=(dq>=0):
            u=dp/(dp-dq);result.append([p[0]+u*(q[0]-p[0]),p[1]+u*(q[1]-p[1])])
    return result

def make_logo(name,poly):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='2D';curve.fill_mode='BOTH'
    curve.extrude=.13;curve.bevel_depth=.022;curve.bevel_resolution=3
    spl=curve.splines.new('POLY');spl.points.add(len(poly)-1)
    for p,(x,y) in zip(spl.points,poly):p.co=(x,y,0,1)
    spl.use_cyclic_u=True;curve.materials.append(mat)
    ob=bpy.data.objects.new(name,curve);scene.collection.objects.link(ob);ob.parent=root
    return ob
full=make_logo('Assembled original — no cut seams',outline)
a=1/math.sqrt(3)
polygons=[clip(clip(outline,-1,0),-a,1),clip(clip(outline,1,0),a,1),clip(clip(outline,a,-1),-a,-1)]
pieces=[make_logo(name,p) for name,p in zip(['Left section','Right section','Lower section'],polygons)]
directions=[(-math.sqrt(3)/2,.5),(math.sqrt(3)/2,.5),(0,-1)]

def polygon_area(p):return abs(sum(x*v-u*y for (x,y),(u,v) in zip(p,p[1:]+p[:1]))/2)
assert abs(sum(map(polygon_area,polygons))-polygon_area(outline))<1e-6

def aim(obj,target=(0,0,0)):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def light(name,location,energy,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=location;aim(ob)
light('Large softbox',(-3,4,5),450,4,(1,.96,.90))
light('Cool fill',(4,0,4),330,3,(.72,.84,1))
light('Top rim',(1,4,-1),500,2,(.88,.96,1))
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam)
cam.location=(0,0,8);camdata.type='ORTHO';camdata.ortho_scale=5.2;aim(cam);scene.camera=cam
scene.view_settings.view_transform='AgX'
ripples=[]
for i in range(2):
    curve=bpy.data.curves.new(f'Ripple {i+1}','CURVE');curve.dimensions='3D';curve.bevel_depth=.013 if i==0 else .009;curve.bevel_resolution=2
    spl=curve.splines.new('POLY');spl.points.add(127)
    for j,p in enumerate(spl.points):
        angle=2*math.pi*j/128;p.co=(math.cos(angle),math.sin(angle),0,1)
    spl.use_cyclic_u=True
    rm=bpy.data.materials.new(f'Ripple fade {i+1}');rm.use_nodes=True;n=rm.node_tree.nodes;n.clear()
    output=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');transparent=n.new('ShaderNodeBsdfTransparent');emission=n.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value=(.82,.90,1,1);emission.inputs['Strength'].default_value=1.3
    rm.node_tree.links.new(transparent.outputs[0],mix.inputs[1]);rm.node_tree.links.new(emission.outputs[0],mix.inputs[2]);rm.node_tree.links.new(mix.outputs[0],output.inputs['Surface'])
    curve.materials.append(rm)
    ob=bpy.data.objects.new(f'Assembly ripple {i+1}',curve);scene.collection.objects.link(ob);ob.location.z=-.5
    ripples.append((ob,mix.inputs[0]))

def clamp(x):return max(0,min(1,x))
def expo_ease_in(x):
    x=clamp(x)
    return 0.0 if x==0 else 2**(10*x-10)
CONTACT=5.25
for frame in range(1,FRAME_COUNT+2):
    t=(frame-1)/FPS
    splitting=1.5<t<CONTACT
    full.hide_render=splitting;full.keyframe_insert('hide_render',frame=frame)
    for i,(piece,(dx,dy)) in enumerate(zip(pieces,directions)):
        # Ease into separation, hold, then stagger the eased arrivals by 125 ms.
        if t<3:amount=expo_ease_in((t-1.5)/1.5)
        elif t<3.5:amount=1
        else:amount=1-expo_ease_in((t-3.5-i*.125)/1.5)
        piece.location=(dx*.48*amount,dy*.48*amount,0)
        piece.hide_render=not splitting
        piece.keyframe_insert('location',frame=frame);piece.keyframe_insert('hide_render',frame=frame)
    settle=clamp((t-CONTACT)/.6)
    # A small whole-logo scale pulse emphasizes contact without overlapping parts.
    bump=.025*math.sin(math.pi*settle)*math.exp(-2*settle) if CONTACT<=t<=CONTACT+.6 else 0
    root.scale=(1+bump,)*3;root.location.y=.018*math.sin(2*math.pi*t/12)
    root.keyframe_insert('scale',frame=frame);root.keyframe_insert('location',frame=frame)
    for i,(ob,opacity) in enumerate(ripples):
        u=(t-CONTACT-i*.25)/1.65
        radius=.65+1.75*(1-(1-clamp(u))**3)
        ob.scale=(radius,radius,radius)
        ob.hide_render=not 0<=u<1
        opacity.default_value=(.55 if i==0 else .32)*(1-clamp(u))**2 if u>=0 else 0
        ob.keyframe_insert('scale',frame=frame);ob.keyframe_insert('hide_render',frame=frame)
        opacity.keyframe_insert('default_value',frame=frame)
scene.frame_set(226)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'unity-logo-assembly.blend'))
if '--preview' in sys.argv:
    for frame,name in [(181,'separated'),(286,'returning'),(361,'ripple'),(451,'assembled')]:
        scene.frame_set(frame);scene.render.filepath=str(HERE/f'assembly-{name}.png');bpy.ops.render.render(write_still=True)
else:
    scene.render.filepath=str(OUT/'frame-');bpy.ops.render.render(animation=True)
