import * as T from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import encoded from './groom-data.js';
import dense from './dense-data.js';

const host=document.querySelector('#stage'), status=document.querySelector('#status');
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
const turnButton=document.querySelector('#turn'), swayButton=document.querySelector('#sway');
let renderer;
try {renderer=new T.WebGLRenderer({antialias:true});}
catch(error){
  status.textContent='This study needs WebGL to display the interactive groom.';
  turnButton.disabled=swayButton.disabled=true;
  throw error;
}
renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));
renderer.outputColorSpace=T.SRGBColorSpace;
renderer.toneMapping=T.ACESFilmicToneMapping;
host.append(renderer.domElement);
renderer.domElement.setAttribute('aria-label','Interactive three-dimensional blonde wig with small flowers on a white plinth');
renderer.domElement.setAttribute('role','img');
const scene=new T.Scene(), rig=new T.Group();
scene.background=new T.Color(0x080708);
scene.add(rig,new T.HemisphereLight(0xfff1df,0x5e4a53,1.25));
const camera=new T.OrthographicCamera();
camera.near=.01;camera.far=30;camera.position.set(0,2.66,8);camera.lookAt(0,2.03,0);
for(const [colour,power,x,y,z] of [[0xffeddf,3.2,-3,5,4],[0xffce9c,3,2,4,-3],[0xcbd5ff,1,3,3,3]]){
  const lamp=new T.DirectionalLight(colour,power);lamp.position.set(x,y,z);scene.add(lamp);
}
function mesh(geom,colour,roughness,xyz,scale){
  const m=new T.Mesh(geom,new T.MeshStandardMaterial({color:colour,roughness}));
  m.position.set(...xyz);if(scale)m.scale.set(...scale);rig.add(m);return m;
}
const sphere=new T.SphereGeometry(1,36,24);
mesh(new T.BoxGeometry(.90,2.58,.80),0xe8e3dc,.67,[0,1.29,0]);
mesh(sphere,0x161519,.75,[0,3.38,0],[.378,.55,.338]);
mesh(sphere,0x161519,.75,[0,2.97,-.035],[.19,.33,.19]);
mesh(sphere,0x161519,.75,[0,2.72,-.05],[.48,.21,.27]);

const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0)), packed=new DataView(bytes.buffer);
let seed=1907;
function random(){seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;}
const nodes=25, guides=[], fibres=[];
const palette=[0x9e6c45,0xba895b,0xc6a273,0xdcc09a,0xead3ac].map(c=>new T.Color(c));
for(let i=0;i<bytes.length;i+=102){
  const points=[];
  for(let j=0;j<17;j++){
    const o=i+j*6;
    points.push(new T.Vector3(packed.getInt16(o,true)/4096,packed.getInt16(o+4,true)/4096,-packed.getInt16(o+2,true)/4096));
  }
  guides.push({points,x:0,z:0,vx:0,vz:0,omega:9+random()*5});
}

const zipped=Uint8Array.from(atob(dense),c=>c.charCodeAt(0));
const data=new DataView(await new Response(new Blob([zipped]).stream()
  .pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
const stride=79, strandCount=data.byteLength/stride;
const positions=new Float32Array(strandCount*nodes*3);
const colours=new Float32Array(positions.length), rest=new Float32Array(positions.length);
const weights=new Float32Array(positions.length/3);
const indices=new Uint32Array(strandCount*(nodes-1)*2);
const fillDirection=new T.Vector3(-.4,.7,.58).normalize();
const rimDirection=new T.Vector3(.67,.62,-.38).normalize();
const tint=new T.Color();
function smooth(x){x=T.MathUtils.clamp(x,0,1);return x*x*(3-2*x);}
for(let i=0;i<strandCount;i++){
  const points=[], offset=i*stride, shade=palette[data.getUint8(offset)];
  let x=0,y=0,z=0;
  for(let j=0;j<13;j++){
    const o=offset+1+j*6;
    x+=data.getInt16(o,true);y+=data.getInt16(o+2,true);z+=data.getInt16(o+4,true);
    points.push(new T.Vector3(x/1024,z/1024,-y/1024));
  }
  const mid=points[8];
  let g=guides[0], distance=Infinity;
  for(const candidate of guides){
    const check=candidate.points[10].distanceToSquared(mid);
    if(check<distance){distance=check;g=candidate;}
  }
  fibres.push(g);
  const path=new T.CatmullRomCurve3(points);
  const samples=path.getPoints(nodes-1);
  for(let j=0;j<nodes;j++){
    const v=i*nodes+j, k=v*3, t=j/(nodes-1), f=samples[j];
    rest.set([f.x,Math.max(.015,f.y),f.z],k);
    weights[v]=smooth(t/.53)*smooth(rest[k+1]/.55);
    const tangent=samples[Math.min(j+1,nodes-1)].clone().sub(samples[Math.max(j-1,0)]).normalize();
    const key=Math.sqrt(Math.max(0,1-tangent.dot(fillDirection)**2));
    const rim=Math.sqrt(Math.max(0,1-tangent.dot(rimDirection)**2));
    const root=.64+.36*smooth(t/.32);
    tint.copy(shade).multiplyScalar(root*(.32+.51*key**3+.19*rim**7));
    colours.set([tint.r,tint.g,tint.b],k);
    if(j<nodes-1){
      const edge=(i*(nodes-1)+j)*2;
      indices[edge]=v;indices[edge+1]=v+1;
    }
  }
}
const geom=new T.BufferGeometry();
const attr=new T.BufferAttribute(positions,3);attr.setUsage(T.DynamicDrawUsage);
geom.setAttribute('position',attr);geom.setAttribute('color',new T.BufferAttribute(colours,3));
geom.setIndex(new T.BufferAttribute(indices,1));
const hair=new T.LineSegments(geom,new T.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.70}));
hair.frustumCulled=false;rig.add(hair);

// Each bloom is modelled with cupped petals, a textured centre and a short stem.
const petalShape=new T.SphereGeometry(1,12,8);
const petalMats=[0xe9b4a7,0xf7ddc8,0xc78183,0xe4c2a4].map(c=>new T.MeshStandardMaterial({color:c,roughness:.72,side:T.DoubleSide}));
const centreMat=new T.MeshStandardMaterial({color:0xceaa58,roughness:.8});
const stemMat=new T.MeshStandardMaterial({color:0x596047,roughness:.86});
const blooms=[];
for(const [x,y,z,size] of [[-.32,3.57,.29,.041],[-.35,3.46,.29,.028],[-.39,3.30,.24,.034],[.34,3.48,.27,.042],[.38,3.36,.25,.027],[.40,3.19,.21,.033],[-.46,2.94,.22,.028],[.43,2.86,.25,.031]]){
  const anchor=new T.Vector3(x,y,z);
  const g=guides.reduce((a,b)=>a.points[7].distanceToSquared(anchor)<b.points[7].distanceToSquared(anchor)?a:b);
  const blossom=new T.Group();
  for(let j=0;j<7;j++){
    const angle=j*Math.PI*2/7+random()*.22;
    const p=new T.Mesh(petalShape,petalMats[Math.floor(random()*petalMats.length)]);
    p.position.set(Math.cos(angle)*size*.57,Math.sin(angle)*size*.57,.007+random()*.008);
    p.rotation.set(Math.sin(angle)*.42,Math.cos(angle)*.42,angle);
    p.scale.set(size*(.63+.2*random()),size*.36,size*.13);blossom.add(p);
  }
  for(let j=0;j<9;j++){
    const c=new T.Mesh(petalShape,centreMat), a=j*2.4, r=size*.23*Math.sqrt(j/9);
    c.position.set(Math.cos(a)*r,Math.sin(a)*r,size*.48);
    c.scale.setScalar(size*.098);blossom.add(c);
  }
  const stem=new T.Mesh(new T.CylinderGeometry(.002,.003,size*1.45,7),stemMat);
  stem.position.set(0,-size*.45,-.012);stem.rotation.z=-.27;blossom.add(stem);
  blossom.position.copy(anchor);rig.add(blossom);blooms.push({blossom,anchor,g});
}
const ray=new T.Raycaster(), pointer=new T.Vector2(), cursor=new T.Vector3(), localCursor=new T.Vector3();
const plane=new T.Plane(new T.Vector3(0,0,1),-.28);
let active=false, impulse=0, turn=0, angle=0, last=0;
function updatePointer(event){
  const rect=renderer.domElement.getBoundingClientRect();
  pointer.set((event.clientX-rect.left)/rect.width*2-1,1-(event.clientY-rect.top)/rect.height*2);
  ray.setFromCamera(pointer,camera);
  active=!!ray.ray.intersectPlane(plane,cursor);
}
renderer.domElement.addEventListener('pointermove',updatePointer);
renderer.domElement.addEventListener('pointerdown',updatePointer);
for(const event of ['pointerleave','pointerup','pointercancel'])renderer.domElement.addEventListener(event,()=>{active=false;});
turnButton.addEventListener('click',()=>{turn=turn===0?.55:0;if(reduce.matches)angle=turn;});
swayButton.addEventListener('click',()=>{impulse=1;});
function resize(){
  const w=host.clientWidth,h=host.clientHeight,half=Math.max(2.16,1.46*h/w);
  camera.left=-half*w/h;camera.right=half*w/h;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();
  renderer.setSize(w,h,false);
}
new ResizeObserver(resize).observe(host);resize();
function spring(g,key,velocity,target,dt){
  const offset=g[key]-target, v=g[velocity], omega=g.omega;
  const slope=v+omega*offset, decay=Math.exp(-omega*dt);
  g[key]=target+(offset+slope*dt)*decay;
  g[velocity]=(v-omega*slope*dt)*decay;
}
function draw(time){
  const dt=Math.min(.045,(time-last)/1000);last=time;
  const quiet=reduce.matches;
  angle+=(turn-angle)*(1-Math.exp(-dt*7));
  rig.rotation.y=angle;rig.updateMatrixWorld();
  if(active)rig.worldToLocal(localCursor.copy(cursor));
  impulse*=Math.exp(-dt*4);
  for(const g of guides){
    let dx=0, influence=0;
    if(active){
      for(let j=4;j<16;j+=2){
        const point=g.points[j], x=point.x-localCursor.x, y=point.y-localCursor.y;
        const reach=Math.exp(-(x*x+y*y)/.16);
        if(reach>influence){influence=reach;dx=x;}
      }
    }
    const push=influence*(.115*Math.tanh(dx*8)+.022);
    spring(g,'x','vx',quiet?0:push+.16*impulse,dt);
    spring(g,'z','vz',quiet?0:-.10*influence+.035*impulse,dt);
  }
  fibres.forEach((g,i)=>{
    const end=(i+1)*nodes*3;
    for(let k=i*nodes*3;k<end;k+=3){
      const weight=weights[k/3];
      positions[k]=rest[k]+g.x*weight;
      positions[k+1]=rest[k+1];
      positions[k+2]=rest[k+2]+g.z*weight;
    }
  });
  for(const {blossom,anchor,g} of blooms){
    blossom.position.set(anchor.x+g.x*.34,anchor.y,anchor.z+g.z*.34);
    blossom.rotation.z=-g.x*1.7;
  }
  attr.needsUpdate=true;renderer.render(scene,camera);
  requestAnimationFrame(draw);
}
status.textContent=reduce.matches?'Reduced motion is enabled.':'Move over the hair to stir it. Move away to let it settle.';
requestAnimationFrame(draw);
