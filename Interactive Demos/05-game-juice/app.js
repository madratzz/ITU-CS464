'use strict';
(() => {
 const L=Lab,T=THREE,C=L.colors;
 const preset=L.select('preset','Juice preset',[['balanced','Balanced impact'],['subtle','Subtle feedback'],['arcade','Arcade punch'],['bare','All effects off']]);
 const strength=L.slider('strength','Impact strength',.2,2,1,.1,'×');
 const stop=L.slider('stop','Hit stop duration',0,160,60,10,' ms');
 const shake=L.check('shake','Camera shake',true),squash=L.check('squash','Squash & stretch',true),particles=L.check('particles','Impact particles',true),flash=L.check('flash','Flash & shockwave',true),sound=L.check('sound','Synthesized impact sound',false);
 let run=null,shots=0,auto=false,wait=0,activeParticles=0,audio=null;
 function ensureAudio(){if(!sound())return;try{audio??=new(window.AudioContext||window.webkitAudioContext)();audio.resume();}catch{L.$('sound').checked=false;}}
 function hitSound(){if(!sound()||!audio)return;const o=audio.createOscillator(),g=audio.createGain();o.type='triangle';o.frequency.setValueAtTime(180,audio.currentTime);o.frequency.exponentialRampToValueAtTime(40,audio.currentTime+.13);g.gain.setValueAtTime(.15,audio.currentTime);g.gain.exponentialRampToValueAtTime(.001,audio.currentTime+.16);o.connect(g).connect(audio.destination);o.start();o.stop(audio.currentTime+.18);}
 function fire(){ensureAudio();run={time:0,hit:false};shots++;wait=0;}
 L.buttons([['hit','Trigger impact',fire,true],['auto','Auto: off',()=>{auto=!auto;L.$('auto').textContent='Auto: '+(auto?'on':'off');if(auto)fire();}]]);
 L.buttons([['reset','Reset lab',()=>{run=null;shots=0;auto=false;L.$('auto').textContent='Auto: off';L.set('preset','balanced');applyPreset();L.$('sound').checked=false;}]]);
 L.hint('<b>Click a target or press Space</b> to fire. Both sides receive the same hit.<br>Toggle one effect at a time. The baseline camera stays fixed; only the right camera shakes. Sound starts muted.');
 function applyPreset(){const p=preset();L.set('strength',{balanced:1,subtle:.5,arcade:1.7,bare:1}[p]);L.set('stop',{balanced:60,subtle:20,arcade:110,bare:0}[p]);for(const id of ['shake','squash','particles','flash'])L.$(id).checked=p!=='bare';}
 L.$('preset').addEventListener('change',applyPreset);L.$('sound').addEventListener('change',ensureAudio);
 const {scene,start,renderer}=L.engine({position:[0,9,18],grid:80});
 const groups=[],targets=[],balls=[],rings=[],debris=[],cameras=[];
 for(let i=0;i<2;i++){const x=i===0?-16:16;const group=new T.Group();group.position.x=x;scene.add(group);groups.push(group);group.add(L.box(5,.2,5,0x283443,0,.06,0));const target=L.box(1.65,1.65,1.65,i===0?0x8190a6:C.orange,0,.98,0);group.add(target);targets.push(target);for(const eyeX of [-.33,.33]){const eye=L.box(.16,.18,.03,0x14171c,eyeX,.16,.84);target.add(eye);}const ball=L.sphere(.25,C.teal,0,1,5);group.add(ball);balls.push(ball);
  const ring=new T.Mesh(new T.RingGeometry(.9,1,64),new T.MeshBasicMaterial({color:C.orange,transparent:true,side:T.DoubleSide,depthWrite:false}));ring.rotation.x=-Math.PI/2;ring.position.y=.19;group.add(ring);rings.push(ring);
  const camera=new T.PerspectiveCamera(40,1,.1,100);camera.position.set(x+7,7,12);camera.lookAt(x,1,0);cameras.push(camera);
 }
 // Fixed particle directions keep repeated comparisons reproducible; meshes are pooled.
 for(let i=0;i<36;i++){const a=i*2.399963,vy=2+(i%5)*.65;const m=L.box(.08+(i%3)*.04,.1,.1,[C.orange,C.teal,C.pink][i%3]);m.userData.velocity=new T.Vector3(Math.cos(a)*(2+i%4),vy,Math.sin(a)*(2+i%4));groups[1].add(m);debris.push(m);}
 document.addEventListener('keydown',e=>{if(e.code==='Space'&&!/INPUT|SELECT|BUTTON/.test(e.target.tagName)){e.preventDefault();if(!e.repeat)fire();}});
 renderer.domElement.addEventListener('pointerdown',e=>{const rect=renderer.domElement.getBoundingClientRect(),localX=e.clientX-rect.left,i=localX<rect.width/2?0:1;const pointer=new T.Vector2(((localX-i*rect.width/2)/(rect.width/2))*2-1,-((e.clientY-rect.top)/rect.height)*2+1);const ray=new T.Raycaster();ray.setFromCamera(pointer,cameras[i]);if(ray.intersectObject(targets[i],true).length)fire();});
 const baseColors=[0x8190a6,C.orange];
 start(dt=>{
  if(run){run.time+=dt;if(run.time>=.35&&!run.hit){run.hit=true;hitSound();}}else{wait+=dt;}
  const age=run?run.time:-1,rawAfter=age-.35,freeze=stop()/1000,after=Math.max(0,rawAfter-freeze),impact=rawAfter>=0;
  activeParticles=0;
  for(let i=0;i<2;i++){const target=targets[i],isJuiced=i===1,k=isJuiced?strength():0,phase=isJuiced?after:Math.max(0,rawAfter);target.scale.set(1,1,1);target.rotation.z=0;target.position.set(0,.98,0);target.material.color.setHex(baseColors[i]);target.material.emissive.setHex(0);balls[i].visible=age>=0&&age<.35;balls[i].position.z=5-4.1*L.clamp(age/.35,0,1);rings[i].visible=false;
   if(impact){if(isJuiced&&squash()){const pulse=Math.exp(-phase*7)*Math.cos(phase*22)*.28*k;target.scale.set(1+pulse,1-pulse,1+pulse);target.position.y=.16+.825*target.scale.y;target.rotation.z=Math.sin(phase*26)*Math.exp(-phase*8)*.1*k;}if(isJuiced&&flash()){const f=Math.max(0,1-phase/.15);target.material.emissive.setRGB(f*.65,f*.45,f*.22);rings[i].visible=phase<.6;rings[i].scale.setScalar(1+phase*6*k);rings[i].material.opacity=Math.max(0,1-phase/.6)*.7;}}
   const camera=cameras[i],baseX=isJuiced?16:-16;camera.position.set(baseX+7,7,12);camera.lookAt(baseX,1,0);if(isJuiced&&impact&&shake()){const envelope=Math.exp(-Math.max(0,rawAfter)*12)*.22*k;camera.position.x+=Math.sin(rawAfter*151)*envelope;camera.position.y+=Math.sin(rawAfter*197+1)*envelope;}
  }
  for(const m of debris){m.visible=impact&&particles()&&after<.85;if(m.visible){activeParticles++;const v=m.userData.velocity;m.position.set(v.x*after*strength(),1+v.y*after-6*after*after,v.z*after*strength());m.rotation.set(after*8,after*5,after*3);m.scale.setScalar(Math.max(0,1-after/.85));}}
  L.stat(0,shots);L.stat(1,impact&&rawAfter<freeze?'FROZEN':run?'RUNNING':'READY');L.stat(2,activeParticles);L.pill(run?(impact?'SAME HIT · DIFFERENT FEEL':'PROJECTILE IN FLIGHT'):'READY · TRIGGER AN IMPACT');
  window.demoState={shots,age,activeParticles,hitStop:impact&&rawAfter<freeze,baselineScale:targets[0].scale.toArray(),juiceScale:targets[1].scale.toArray()};
  if(run&&run.time>1.6){run=null;wait=0;}if(auto&&!run&&wait>.5)fire();
 },()=>{
  const w=L.$('stage').clientWidth,h=L.$('stage').clientHeight,half=Math.floor(w/2);renderer.setScissorTest(true);for(let i=0;i<2;i++){const width=i===0?half:w-half;cameras[i].aspect=width/h;cameras[i].updateProjectionMatrix();renderer.setViewport(i*half,0,width,h);renderer.setScissor(i*half,0,width,h);renderer.render(scene,cameras[i]);}renderer.setScissorTest(false);renderer.setViewport(0,0,w,h);
 });
})();
