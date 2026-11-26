"""Export all v2 fibres with 13 control samples and the source material index."""
import base64
import bpy
import gzip
import struct
from pathlib import Path

groom = next(obj for obj in bpy.data.objects if obj.name.startswith('Blonde groom'))
splines = list(groom.data.splines)
payload = bytearray()
for spline in splines:
    payload.append(spline.material_index)
    previous = [0, 0, 0]
    for point in list(spline.points)[::4]:
        coords = [round(value * 1024) for value in point.co[:3]]
        payload.extend(struct.pack('<hhh', *(coords[i] - previous[i] for i in range(3))))
        previous = coords
encoded = base64.b64encode(gzip.compress(payload, mtime=0)).decode()
Path(__file__).with_name('dense-data.js').write_text("export default '" + encoded + "';\n")
print(f'Exported {len(splines):,} strands, {len(encoded):,} encoded bytes')
