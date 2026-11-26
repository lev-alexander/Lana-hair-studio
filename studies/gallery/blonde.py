import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector

out = Path(sys.argv[-1]).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
rng = random.Random(71)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.sample_clamp_indirect = 2.5
scene.cycles.use_denoising = False
scene.render.resolution_x = 520
scene.render.resolution_y = 680
scene.render.resolution_percentage = 100
scene.world.color = (.015, .015, .015)

def material(name, color, roughness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    return mat

def ellipsoid(name, position, size, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(mat)
    for face in obj.data.polygons:
        face.use_smooth = True

black = material('Matte black display head', (.009,.007,.007), .75)
white = material('Warm white exhibition plinth', (.74,.73,.71), .48)
ellipsoid('Head', (0,0,3.38), (.38,.34,.55), black)
ellipsoid('Neck', (0,.035,2.97), (.19,.19,.33), black)
ellipsoid('Shoulders', (0,.05,2.72), (.48,.27,.21), black)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,1.29))
plinth = bpy.context.object
plinth.name = 'White plinth'
plinth.dimensions = (.9,.8,2.58)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
plinth.data.materials.append(white)
bevel = plinth.modifiers.new('Edge bevel','BEVEL')
bevel.width = .012
bevel.segments = 3
plinth.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.data.materials.append(material('Black floor', (.003,.003,.003), .65))

groom = bpy.data.curves.new('Centre-parted champagne blonde', 'CURVE')
groom.dimensions = '3D'
groom.bevel_depth = .0022
groom.bevel_resolution = 0
for color in [(0.31,.17,.075),(.49,.29,.13),(.64,.43,.23),(.8,.6,.36),(.94,.76,.53)]:
    mat = material('Champagne fibre', color, .32)
    nodes = mat.node_tree.nodes
    hair = nodes.new('ShaderNodeBsdfHairPrincipled')
    hair.parametrization = 'COLOR'
    hair.inputs['Color'].default_value = (*color,1)
    hair.inputs['Roughness'].default_value = .34
    mat.node_tree.links.new(hair.outputs[0], nodes.get('Material Output').inputs['Surface'])
    groom.materials.append(mat)
obj = bpy.data.objects.new('Blonde groom • editable individual fibres', groom)
scene.collection.objects.link(obj)

for side in (-1,1):
    locks = [(rng.uniform(-1,1), rng.uniform(-.9,.9), rng.uniform(.83,1.19))
             for _ in range(19)]
    for i in range(3900):
        drift, offset, length = locks[i % len(locks)]
        lane = rng.random()
        jitter = rng.gauss(0,.024)
        fur = i % 19 == 0
        phase = offset + rng.gauss(0,.14)
        end = max(.022, rng.gauss(.08,.075) + max(0,1-length)*2.9)
        spline = groom.splines.new('POLY')
        spline.points.add(48)
        spline.material_index = rng.choices(range(5), [8,20,35,28,9])[0]
        for j,p in enumerate(spline.points):
            t=j/48
            spread=math.sin(min(t/.24,1)*math.pi/2)
            root_y=-.25+lane*.59
            root_z=3.85+.075*math.sin(lane*math.pi)
            z=max(.019, root_z-(root_z-end)*t)
            bell=math.sin(math.pi*t)**.7
            wave=math.sin(t*(17+2.7*drift)+lane*3+phase+side*.53)*(.041+.068*bell)*spread
            x=side*(.013+spread*(.34+.21*lane+.17*t+jitter)+wave)
            y=root_y+.10*math.sin(t*16+lane*4+phase)*spread-.19*t+lane*.07*t
            # Route the visible hairline over the display head before the locks fall.
            if t < .22:
                u = t/.22
                theta = .015 + u*1.85
                root_y = -.31 + lane*.63
                cross_section = math.sqrt(max(.07, 1-(root_y/.37)**2))
                scalp_x = side*(.38+lane*.05)*cross_section*math.sin(theta)
                scalp_z = 3.38+.58*cross_section*math.cos(theta)
                blend = u**3
                x = scalp_x*(1-blend)+x*blend
                z = scalp_z*(1-blend)+z*blend
                y = root_y*(1-blend)+y*blend
            # Locks keep their individual direction and settle tangentially onto the floor.
            lock_weight = min(1, max(0, (t-.12)/.2))
            lock_weight = lock_weight**2*(3-2*lock_weight)
            x+=lock_weight*(.11*drift+.066*math.sin(t*25+offset*4))
            y+=lock_weight*(.17*offset+.065*math.cos(t*23+offset*4))
            if t > .73:
                u = (t-.73)/.27
                floor = u*u*(3-2*u)
                pool = max(0,length-.85)*4.6*floor
                x+=(-.22 if side==1 else -.78)*pool + .19*drift*floor
                y-=(.45+.45*lane)*pool
                z = z*(1-floor) + end*floor
            if fur:
                x+=side*.08*math.sin(t*27+phase)*bell
            p.co=(x,y,z,1)
            p.radius=(.65+lane*.33)*(1-.91*t**9)

def point(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def light(name, pos, power, size, color):
    src=bpy.data.lights.new(name,'AREA')
    src.energy=power
    src.shape='DISK'
    src.size=size
    src.color=color
    obj=bpy.data.objects.new(name,src)
    scene.collection.objects.link(obj)
    obj.location=pos
    point(obj,(0,0,2.3))

light('Large silk key',(-3,-4,5.6),490,3,(1,.88,.76))
light('Soft neutral fill',(2.5,-3,4),220,3,(.86,.92,1))
light('Rim',(2,2,5),540,2,(1,.89,.75))
bpy.ops.object.camera_add(location=(0,-10,3.1))
camera=bpy.context.object
scene.camera=camera
camera.data.type='ORTHO'
camera.data.ortho_scale=5.05
point(camera,(0,0,2.38))

bpy.ops.wm.save_as_mainfile(filepath=str(out/'blonde-groom.blend'))
for name,pos in [('front',(0,-10,3.1)),]:
    camera.location=pos
    point(camera,(0,0,2.38))
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
