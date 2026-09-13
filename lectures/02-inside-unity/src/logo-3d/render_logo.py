"""Blender background renderer. --preview renders one frame, otherwise a 12s loop."""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
OUT=Path('/tmp/cs464-unity-3d-frames');OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.render.fps=16;scene.frame_start=1;scene.frame_end=192
scene.world=bpy.data.worlds.new('Studio world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.32,0.36,0.42,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
curve=bpy.data.curves.new('Original Unity mark outline','CURVE');curve.dimensions='2D'
curve.resolution_u=2;curve.fill_mode='BOTH';curve.extrude=.13;curve.bevel_depth=.022;curve.bevel_resolution=3
for polygon in json.loads((HERE/'outline.json').read_text()):
    spl=curve.splines.new('POLY');spl.points.add(len(polygon)-1)
    for p,(x,y) in zip(spl.points,polygon):p.co=(x,y,0,1)
    spl.use_cyclic_u=True
logo=bpy.data.objects.new('Unity mark — extruded original silhouette',curve);scene.collection.objects.link(logo)
mat=bpy.data.materials.new('Satin silver');mat.diffuse_color=(.82,.86,.9,1);mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.82,.86,.9,1)
bsdf.inputs['Metallic'].default_value=.52;bsdf.inputs['Roughness'].default_value=.26
curve.materials.append(mat)
def aim(obj,target=(0,0,0)):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def light(name,location,energy,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=location;aim(ob)
light('Large softbox',(-3,4,5),450,4,(1,.96,.90))
light('Cool fill',(4,0,4),330,3,(.72,.84,1))
light('Top rim',(1,4,-1),500,2,(.88,.96,1))
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam)
cam.location=(0,0,8);camdata.type='ORTHO';camdata.ortho_scale=3.9;aim(cam);scene.camera=cam
scene.view_settings.view_transform='AgX'
for frame in range(1,194):
    phase=2*math.pi*(frame-1)/192
    logo.rotation_euler=(math.radians(5)*math.sin(phase+.5),math.radians(19)*math.sin(phase),math.radians(1.5)*math.sin(phase))
    logo.location.y=.035*math.sin(phase)
    logo.keyframe_insert(data_path='rotation_euler',frame=frame)
    logo.keyframe_insert(data_path='location',frame=frame)
scene.frame_set(25)
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'unity-logo-3d.blend'))
if '--preview' in sys.argv:
    scene.render.filepath=str(HERE/'preview.png');bpy.ops.render.render(write_still=True)
else:
    scene.render.filepath=str(OUT/'frame-');bpy.ops.render.render(animation=True)
