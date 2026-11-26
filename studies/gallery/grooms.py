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
scene.cycles.samples = 44
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

style = sys.argv[-2]
if style == 'film':
    for m,c in zip(groom.materials,[(.08,.011,.004),(.2,.035,.009),(.35,.065,.015),(.52,.115,.027),(.68,.19,.06)]):
        next(n for n in m.node_tree.nodes if n.type=='BSDF_HAIR_PRINCIPLED').inputs['Color'].default_value=(*c,1)
    for i in range(6500):
        group=i%38
        angle=group/38*math.tau+rng.gauss(0,.18)
        length=.7+.46*rng.random()+.18*math.sin(group*3)
        front=math.cos(angle)
        if front>.68: length*=.46
        spline=groom.splines.new('POLY'); spline.points.add(36)
        spline.material_index=rng.randrange(5)
        for j,p in enumerate(spline.points):
            t=j/36
            spread=math.sin(min(t/.44,1)*1.57)
            theta=angle+.82*math.sin(t*2.55)
            r=.55*spread+.025+(.135+.055*math.sin(group))*math.sin(t*14+group*.36)*spread
            x=math.sin(theta)*r
            y=-math.cos(theta)*r
            z=3.95-length*t+.07*math.sin(t*13+group*.45)*spread
            p.co=(x,y,z,1);p.radius=.78*(1-.87*t**8)
else:
    for i in range(7000):
        k=i%26
        side=-1 if k%2 else 1
        layer=k//2
        cx=side*(.13+.17*math.sin(layer*1.37))
        cy=.13*math.cos(layer*2)-.04
        cz=3.76+layer*.057
        angle=rng.uniform(-.5,1.6)
        ringlet=layer<2
        spline=groom.splines.new('POLY');spline.points.add(44)
        spline.material_index=rng.randrange(1,5)
        for j,p in enumerate(spline.points):
            t=j/44
            phase=t*(17 if ringlet else 4.6)+angle
            r=(.09 if ringlet else .25)+rng.gauss(0,.016)
            x=1.14*cx+r*math.cos(phase)+.12*side*t
            y=cy+r*math.sin(phase)-.14*t
            z=cz-(.99 if ringlet else .19)*t+.075*math.sin(phase)
            p.co=(x,y,z,1);p.radius=.8*(1-.8*t**9)
    petals=[material('Burgundy silk',(.24,.012,.041),.38), material('Rose silk',(.66,.19,.22),.41), material('Peach silk',(.82,.43,.31),.44)]
    gold=material('Gold seed',(.74,.38,.09),.28)
    for i in range(26):
        a=i*2.3999
        center=Vector((.52*math.cos(a),-.22+.17*math.sin(a),3.60+i*.039))
        size=rng.uniform(.045,.072)
        for ring in range(2):
            for j in range(5):
                q=j*math.tau/5+ring*.7
                loc=center+Vector((math.cos(q),-.17,math.sin(q)))*size*(1+.58*ring)
                ellipsoid('Silk petal',loc,(size*(1+.24*ring),size*.33,size*.61),petals[i%3])
                bpy.context.object.rotation_euler.y=-q
        ellipsoid('Gold centre',center+Vector((0,-.045,0)),(.025,.018,.025),gold)
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

bpy.ops.wm.save_as_mainfile(filepath=str(out/(style+'-groom.blend')))
for name,pos in [('front',(0,-10,3.1)),]:
    camera.location=pos
    point(camera,(0,0,2.38))
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
