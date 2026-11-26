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

style = sys.argv[-2]
if style == 'film':
    for m,c in zip(groom.materials,[(.08,.011,.004),(.2,.035,.009),(.35,.065,.015),(.52,.115,.027),(.68,.19,.06)]):
        next(n for n in m.node_tree.nodes if n.type=='BSDF_HAIR_PRINCIPLED').inputs['Color'].default_value=(*c,1)
    def sample(points,t):
        u=t*(len(points)-1)
        k=min(int(u),len(points)-2)
        f=u-k
        a,b,c,d=[points[max(0,min(len(points)-1,k+j))] for j in (-1,0,1,2)]
        return .5*((2*b)+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f**3)
    def lock(points, count, width, shade):
        points=list(map(Vector,points))
        for i in range(count):
            x,y,z=[rng.gauss(0,width) for _ in range(3)]
            curve=groom.splines.new('POLY');curve.points.add(40)
            curve.material_index=min(4,max(0,shade+rng.choice([-1,0,0,0,1])))
            for j,p in enumerate(curve.points):
                t=j/40
                q=sample(points,t)
                w=.4+.6*math.sin(math.pi*t)
                wave=.015*math.sin(t*11+x*24)*math.sin(math.pi*t)
                p.co=(q.x+w*x+wave,q.y+w*y,q.z+w*z,1)
                p.radius=.7*(1-.92*t**8)
    # Crown and rear layers wrap around the mannequin.
    for i in range(30):
        a=i*math.tau/30
        x,y=math.sin(a),math.cos(a)
        if y<-.67: continue
        lock([(x*.08,y*.10,3.95),(x*.41,y*.36,3.82),(x*.53,y*.38,3.53),
              (x*.5,y*.39,3.19),(x*.62,y*.35,2.84+.17*math.sin(i))],130,.056,2)
    for side in (-1,1):
        for i in range(9):
            z=3.76-i*.092 + .044*math.sin(i*2.1+side)
            lock([(side*(.23+i*.024),-.29,z+.07),(side*.39,-.37,z),
                  (side*.54,-.35,z-.12),(side*(.65+.09*math.sin(i*1.4+side)),-.29+.035*i,z-.14),
                  (side*(.69-.012*i+.10*math.sin(i*1.3+side)), -.18+.025*i,z+.06+.06*math.cos(i))],230,.048,i%3+1)
    for i in range(10):
        k=i/9
        lock([(.21,-.19,3.94-k*.05),(.06,-.39,3.93-k*.06),
              (-.22,-.47,3.77-k*.08),(-.45,-.34,3.62-k*.055),
              (-.63,-.26,3.72-k*.07)],170,.033,3)
else:
    # Each roll is a torus-like bundle with fibres following its curl.
    rolls=[(-.27,-.19,3.77,.20),(.20,-.25,3.80,.19),(-.03,-.22,3.98,.26),
           (-.24,-.14,4.13,.19),(.23,-.13,4.13,.20),(.04,-.10,4.36,.23),
           (-.13,.06,4.48,.15),(.19,.08,4.30,.17),
           (-.28,.19,3.94,.21),(.19,.22,4.04,.24),(0,.21,4.24,.26)]
    for i,(x,y,z,r) in enumerate(rolls):
        for j in range(580):
            ring=rng.uniform(0,math.tau)
            phase=rng.uniform(0,math.tau)
            spread=rng.uniform(.02,.075)
            curve=groom.splines.new('POLY');curve.points.add(38)
            curve.material_index=rng.randrange(1,5)
            for k,p in enumerate(curve.points):
                t=k/38
                a=phase+t*5.6
                b=ring+t*3.0
                rr=r+spread*math.cos(b)
                p.co=(x+rr*math.cos(a),y+spread*math.sin(b)+.095*math.sin(a),z+rr*.77*math.sin(a),1)
                p.radius=.74*(1-.82*t**8)
    for side in (-1,1):
        for j in range(700):
            phase=rng.gauss(0,.36)
            radius=rng.uniform(.059,.116)
            curve=groom.splines.new('POLY');curve.points.add(50)
            curve.material_index=rng.randrange(1,5)
            for k,p in enumerate(curve.points):
                t=k/50
                a=t*math.tau*3.4+phase
                p.co=(side*(.31+.08*t)+radius*math.cos(a),-.31+radius*math.sin(a),3.78-(.89+.11*radius/.116)*t,1)
                p.radius=.78*(1-.85*t**8)
    petals=[material('Burgundy silk',(.24,.012,.041),.38), material('Rose silk',(.66,.19,.22),.41), material('Peach silk',(.82,.43,.31),.44)]
    gold=material('Gold seed',(.74,.38,.09),.28)
    for i in range(19):
        a=i*2.3999
        center=Vector((.52*math.cos(a),-.22+.17*math.sin(a),3.66+i*.045))
        size=rng.uniform(.034,.095)
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

light('Large silk key',(-3,-4,5.6),490,3,(1,.92,.87))
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
