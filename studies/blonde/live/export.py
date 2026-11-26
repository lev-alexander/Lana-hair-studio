"""Sample the original blonde groom for real-time rendering."""
import base64, bpy, struct
from pathlib import Path
groom=next(o for o in bpy.data.objects if o.name.startswith('Blonde groom'))
splines=list(groom.data.splines)
samples=[]
for spline in splines[::36]:
    for p in list(spline.points)[::3]:
        samples.extend(round(v*4096) for v in p.co[:3])
encoded=base64.b64encode(struct.pack('<'+'h'*len(samples),*samples)).decode()
Path(__file__).with_name('groom-data.js').write_text("export default '"+encoded+"';\n")
