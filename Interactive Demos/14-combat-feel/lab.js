/* Shared runtime, copied locally into every lab to keep each folder portable. */
'use strict';
const Lab = (() => {
 const T = THREE, $ = id => document.getElementById(id);
 const colors = {orange:0xff8a3d,teal:0x55d6c2,blue:0x6c8cff,pink:0xff4fa3,muted:0x66758b};
 const rad = d => d*Math.PI/180, deg = r => r*180/Math.PI, clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
 function slider(id,label,min,max,value,step=1,unit='') {
  $('controls').insertAdjacentHTML('beforeend',`<div class="control"><label for="${id}">${label}<output id="${id}-out" for="${id}"></output></label><input type="range" id="${id}" min="${min}" max="${max}" value="${value}" step="${step}"></div>`);
  const el=$(id);const update=()=>$(id+'-out').textContent=Number(el.value).toFixed(step<1?Math.ceil(-Math.log10(step)):0)+unit;el.addEventListener('input',update);update();return ()=>+el.value;
 }
 function select(id,label,options,value){$('controls').insertAdjacentHTML('beforeend',`<div class="control"><label for="${id}">${label}</label><select id="${id}">${options.map(([v,l])=>`<option value="${v}">${l}</option>`).join('')}</select></div>`);if(value!==undefined)$(id).value=value;return()=>$(id).value;}
 function check(id,label,value){$('controls').insertAdjacentHTML('beforeend',`<label class="check"><input id="${id}" type="checkbox" ${value?'checked':''}>${label}</label>`);return()=>$(id).checked;}
 function buttons(items){const row=document.createElement('div');row.className='actions';for(const [id,label,fn,primary] of items){const b=document.createElement('button');b.id=id;b.textContent=label;b.className=primary?'primary':'';b.onclick=fn;row.append(b);}$('controls').append(row);}
 function hint(html){$('controls').insertAdjacentHTML('beforeend',`<p class="hint">${html}</p>`);}
 function set(id,value){$(id).value=value;$(id).dispatchEvent(new Event('input'));}
 function stat(i,value){const el=$('stat'+i);if(el.textContent!==String(value))el.textContent=value;}
 function pill(text,color){$('status').textContent=text;if(color)$('status').style.color=color;}
 function material(color,extra={}){return new T.MeshStandardMaterial({color,roughness:.6,metalness:.15,...extra});}
 function box(w,h,d,color,x=0,y=0,z=0){const m=new T.Mesh(new T.BoxGeometry(w,h,d),material(color));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;return m;}
 function sphere(r,color,x=0,y=0,z=0){const m=new T.Mesh(new T.SphereGeometry(r,24,16),material(color));m.position.set(x,y,z);m.castShadow=true;return m;}
 function line(points,color,dashed=false){const g=new T.BufferGeometry().setFromPoints(points.map(p=>Array.isArray(p)?new T.Vector3(...p):p));const m=dashed?new T.LineDashedMaterial({color,dashSize:.25,gapSize:.15}):new T.LineBasicMaterial({color});const l=new T.Line(g,m);if(dashed)l.computeLineDistances();return l;}
 function replaceLine(l,points){l.geometry.dispose();l.geometry=new T.BufferGeometry().setFromPoints(points);if(l.isLine)l.computeLineDistances();}
 function arrow(color){return new T.ArrowHelper(new T.Vector3(0,1,0),new T.Vector3(),1,color,.32,.16);}
 function vector(a,origin,v){const len=v.length();a.visible=len>1e-6;if(a.visible){a.position.copy(origin);a.setDirection(v.clone().normalize());a.setLength(len,Math.min(.35,len*.25),Math.min(.18,len*.12));}}
 function label(text,color='#eef1f5'){const c=document.createElement('canvas');c.width=512;c.height=80;const ctx=c.getContext('2d');ctx.font='600 30px sans-serif';ctx.textAlign='center';ctx.fillStyle=color;ctx.fillText(text,256,48);const tex=new T.CanvasTexture(c);const m=new T.Sprite(new T.SpriteMaterial({map:tex,depthTest:false,transparent:true}));m.scale.set(6,.9375,1);return m;}
 function engine({position=[12,13,16],look=[0,0,0],orbit=false,grid=24}={}){
  const host=$('stage'),scene=new T.Scene();scene.background=new T.Color(0x171c23);
  let renderer;try{renderer=new T.WebGLRenderer({antialias:true});}catch(e){host.innerHTML='<div class="error">This lab needs WebGL. Enable hardware acceleration in your browser, then reload. Your browser could not create a 3D context.</div>';throw e;}
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;host.prepend(renderer.domElement);renderer.domElement.setAttribute('aria-label','Interactive 3D demonstration');renderer.domElement.setAttribute('role','img');
  const camera=new T.PerspectiveCamera(43,1,.1,200);camera.position.set(...position);const target=new T.Vector3(...look);camera.lookAt(target);
  scene.add(new T.HemisphereLight(0xddeaff,0x263042,2));const light=new T.DirectionalLight(0xffffff,3);light.position.set(-8,15,9);light.castShadow=true;light.shadow.mapSize.set(1024,1024);Object.assign(light.shadow.camera,{left:-18,right:18,top:18,bottom:-18});scene.add(light);
  const floor=new T.Mesh(new T.PlaneGeometry(120,120),material(0x171c23));floor.rotation.x=-Math.PI/2;floor.position.y=-.04;floor.receiveShadow=true;scene.add(floor);
  const lines=new T.GridHelper(grid,grid,0x405065,0x293444);lines.position.y=-.015;scene.add(lines);
  const resize=()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();};new ResizeObserver(resize).observe(host);resize();
  if(orbit){let drag=null;const canvas=renderer.domElement;canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointermove',e=>{if(!drag)return;const sph=new T.Spherical().setFromVector3(camera.position.clone().sub(target));sph.theta-=(e.clientX-drag[0])*.006;sph.phi=clamp(sph.phi+(e.clientY-drag[1])*.006,.15,Math.PI*.48);camera.position.copy(new T.Vector3().setFromSpherical(sph).add(target));camera.lookAt(target);drag=[e.clientX,e.clientY];});for(const type of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(type,()=>drag=null);canvas.addEventListener('wheel',e=>{e.preventDefault();const v=camera.position.clone().sub(target);v.multiplyScalar(Math.exp(e.deltaY*.001));v.clampLength(8,45);camera.position.copy(v.add(target));},{passive:false});}
  let last=0;function start(update,draw){function frame(t){const dt=last?Math.min((t-last)/1000,.05):0;last=t;update(dt,t/1000);if(draw)draw();else renderer.render(scene,camera);requestAnimationFrame(frame);}requestAnimationFrame(frame);}
  return{scene,camera,renderer,start,target};
 }
 function tank(){const g=new T.Group();g.add(box(1.7,.55,2.2,0x436c65,0,.55,0));for(const x of [-.95,.95]){g.add(box(.4,.55,2.5,0x29333b,x,.35,0));for(let z=-.8;z<1;z+=.4){const w=new T.Mesh(new T.CylinderGeometry(.22,.22,.43,12),material(0x657080));w.rotation.z=Math.PI/2;w.position.set(x,.35,z);g.add(w);}}
  const turret=new T.Group();turret.position.y=1;turret.add(box(1,.5,1.1,colors.teal));turret.add(box(.2,.18,1.8,0xb2f4df,0,.05,1.15));g.add(turret);return{group:g,turret};}
 return{$,colors,rad,deg,clamp,slider,select,check,buttons,hint,set,stat,pill,material,box,sphere,line,replaceLine,arrow,vector,label,engine,tank};
})();
