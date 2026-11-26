"""Editable clay blockout of the Film wig. Run in Blender 4.3."""
import bpy, math, sys
from mathutils import Vector
from pathlib import Path

out=Path(sys.argv[-1])
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='OBJECT'
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.background_type='WORLD'
scene.world.color=(.04,.04,.04)
scene.render.resolution_x=620
scene.render.resolution_y=720
scene.render.resolution_percentage=100

def sphere(name, xyz, scale, colour):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=xyz)
    obj=bpy.context.object
    obj.name=name
    obj.scale=scale
    obj.color=(*colour,1)
    for p in obj.data.polygons:
        p.use_smooth=True

sphere('Head', (0,0,1.64), (.35,.32,.48), (.088,.073,.075))
sphere('Neck', (0,.015,1.26), (.18,.19,.31), (.088,.073,.075))
sphere('Shoulders', (0,.04,1.04), (.45,.26,.16), (.088,.073,.075))
sphere('Crown volume', (0,.045,1.95), (.43,.35,.33), (.32,.11,.06))
sphere('Back volume', (0,.24,1.59), (.48,.24,.53), (.28,.08,.045))

def sweep(name,points,width,depth,shade):
    points=list(map(Vector,points))
    centers=[]
    for i in range(49):
        step=i/48*(len(points)-1)
        k=min(int(step),len(points)-2)
        f=step-k
        a,b,c,d=(points[min(len(points)-1,max(0,k+j))] for j in (-1,0,1,2))
        centers.append(.5*(2*b+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f**3))
    vertices=[]
    sections=20
    for i,p in enumerate(centers):
        t=i/48
        tangent=(centers[min(48,i+1)]-centers[max(0,i-1)]).normalized()
        normal=tangent.cross(Vector((0,1,0))).normalized()
        binormal=tangent.cross(normal).normalized()
        taper=.018+.982*math.sin(math.pi*(.10+.90*t))**.83
        for j in range(sections):
            a=math.tau*j/sections
            vertices.append(tuple(p+taper*(normal*math.cos(a)*width+binormal*math.sin(a)*depth)))
    faces=[tuple(reversed(range(sections)))]
    for i in range(48):
        for j in range(sections):
            a=i*sections+j
            b=i*sections+(j+1)%sections
            faces.append((a,b,b+sections,a+sections))
    faces.append(tuple(range(48*sections,49*sections)))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(obj)
    obj.color=(shade,shade*.37,shade*.21,1)
    for polygon in mesh.polygons:
        polygon.use_smooth=True

sweep('Fringe | diagonal face frame',[(.26,-.13,2.16),(.11,-.29,2.18),
      (-.16,-.41,2.00),(-.39,-.36,1.86),(-.58,-.20,1.91),(-.69,-.06,2.01)],.135,.058,.57)
sweep('Fringe | part relief',[(.27,-.08,2.17),(.13,-.26,2.23),
      (-.15,-.34,2.12),(-.36,-.33,1.99),(-.56,-.18,2.02)],.085,.075,.47)
for side in (-1,1):
    for i in range(4):
        z=1.84-i*.185+(.10 if i==0 and side==1 else 0)+.035*math.sin(i*2.2+side)
        reach=[.58,.70,.79,.73][i]+.04*side
        sweep(f'{"Left" if side<0 else "Right"} | feather {i+1}',
              [(side*(.26+i*.03),-.13,z+.25),
               (side*(.37+.045*i),-.285,z+.09),(side*(.48+.026*i),-.29+.025*i,z-.15),
               (side*(reach-.10),-.20,z-.16),(side*reach,-.03,z+[.04,.01,-.05,-.10][i])],
              .141+i*.01,.087,[.51,.46,.40,.34][i])
    sweep(f'Rear barrel {side}',[(side*.27,.21,2.14),(side*.50,.26,1.86),
          (side*.59,.23,1.48),(side*.48,.28,1.14),(side*.64,.36,1.05)],.22,.16,.31)

bpy.ops.object.camera_add()
camera=bpy.context.object
camera.data.type='ORTHO'
camera.data.ortho_scale=2.05
scene.camera=camera
angles={'front':(0,-6,1.66),'three-quarter':(3.5,-5,3.2),'side':(6,0,1.72)}
for name,position in angles.items():
    camera.location=position
    camera.rotation_euler=(Vector((0,0,1.64))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
camera.location=angles['three-quarter']
camera.rotation_euler=(Vector((0,0,1.64))-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scarlet-blockout.blend'))
