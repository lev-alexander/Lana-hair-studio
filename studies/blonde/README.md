# Blonde exhibit groom study

The Blender scene builds an editable set of 7,800 tapered fibres, a matte display head and a warm-white plinth. It renders front and three-quarter checks. Run with Blender 4.3.2:

```sh
mkdir -p renders
blender -b -P studies/blonde/groom.py -- renders
```

## Website research

- [Bruno Simon on Codrops](https://tympanus.net/codrops/author/brunosimon/) demonstrates scroll-driven Three.js. Use the normal page scroll as a camera and spring input with an ordinary HTML reading order.
- [35mm site breakdown](https://tympanus.net/codrops/2025/05/30/deconstructing-the-35mm-website-a-look-at-the-process-and-technical-details/) is a reference for restrained photographic presentation and controlled shader effects.
- [Three.js Hair Shader](https://github.com/creategamecharacters/threejs-hair-shader) is a candidate for tangent-aligned highlights on textured hair cards. Check licence and dependency versions before adoption.
- [Hair Simulator](https://github.com/eriondibrani/hair-simulator) is a reference for GPU-instanced strands. Benchmark the cost on an actual phone before choosing this route.

Use the close-up render to judge fibre direction and highlight width. Build the browser asset from a small number of authorable locks with baked strand detail. Keep springs at the lock level, anchored at the roots, and compare frame time and silhouette with a still. The full Cycles groom is a master asset for renders.
