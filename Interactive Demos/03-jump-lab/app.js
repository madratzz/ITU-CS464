'use strict';
(() => {
 const L=Lab,T=THREE,C=L.colors,P=JumpPhysics;
 const preset=L.select('preset','Controller preset',[['responsive','Responsive'],['precise','Strict / no forgiveness'],['floaty','Floaty']]);
 const height=L.slider('height','Jump height',1,5,2.8,.1,' m');const apex=L.slider('apex','Time to apex',.2,.8,.4,.01,' s');
 const speed=L.slider('speed','Move speed',2,9,5,.1,' m/s');const fall=L.slider('fall','Falling gravity multiplier',1,3,1.8,.1,'×');
 const coyote=L.slider('coyote','Coyote window',0,250,120,10,' ms');const buffer=L.slider('buffer','Input buffer',0,250,140,10,' ms');
 const variable=L.check('variable','Short hop on early jump release',true);
 let s=P.create(),paused=false,acc=0,trial=null,history=[],press=false,release=false,lastJumps=0;
 const keys=new Set();const params=()=>({height:height(),apex:apex(),speed:speed(),fall:fall(),coyote:coyote()/1000,buffer:buffer()/1000,variable:variable()});
 function reset(){s=P.create();trial=null;history=[];keys.clear();press=false;release=false;acc=0;lastJumps=0;}
 function runTrial(type){reset();paused=false;L.$('pause').textContent='Pause';trial={type,pressed:false,left:null};if(type==='coyote'){s.x=-1.3;}else{s.x=3;s.y=3;s.vy=-2;s.grounded=false;s.lastGround=-100;}s.event=type==='coyote'?'Trial: jump 80 ms after edge':'Trial: press ~70 ms before landing';}
 L.buttons([['coyote-trial','Coyote trial',()=>runTrial('coyote'),true],['buffer-trial','Buffer trial',()=>runTrial('buffer')]]);
 L.buttons([['pause','Pause',()=>{paused=!paused;L.$('pause').textContent=paused?'Resume':'Pause';}],['step','Step 1/120 s',()=>{paused=true;L.$('pause').textContent='Resume';tick(1/120);}],['reset','Reset',reset]]);
 L.hint('<b>Play:</b> A/D or ←/→ to move. Hold Space to jump; release early for a short hop. R resets.<br><b>Compare:</b> run a trial, set its window to 0 ms, then run again.');
 L.$('preset').addEventListener('change',()=>{const v={responsive:[2.8,.4,5,1.8,120,140],precise:[2.8,.4,5,1.8,0,0],floaty:[3.2,.7,4,1,160,180]}[preset()];['height','apex','speed','fall','coyote','buffer'].forEach((id,i)=>L.set(id,v[i]));reset();});
 const {scene,start}=L.engine({position:[0,7,22],look:[0,.8,0],grid:24});
 for(const obj of scene.children){if(obj.isMesh&&obj.geometry.type==='PlaneGeometry')obj.position.y=-3.2;if(obj.isGridHelper)obj.position.y=-3.18;}
 for(const [a,b]of P.platforms){scene.add(L.box(b-a,.8,3.2,0x394657,(a+b)/2,-.4,0));scene.add(L.box(b-a,.04,3.23,C.teal,(a+b)/2,.025,0));}
 const startLabel=L.label('RUN →','#55d6c2');startLabel.position.set(-5,-1.2,1.8);scene.add(startLabel);const gapLabel=L.label('THE COYOTE GAP','#9aa2b1');gapLabel.position.set(.25,-2.3,0);scene.add(gapLabel);
 const hero=new T.Group();hero.add(L.box(.65,1,.65,C.orange));for(const x of [-.16,.16])hero.add(L.box(.085,.1,.025,0x14171c,x,.17,.34));scene.add(hero);
 const velocity=L.arrow(C.blue);scene.add(velocity);const ghost=L.line([[0,0,0],[1,1,0]],C.orange);scene.add(ghost);let squash=0;
 function activeForm(e){return /INPUT|SELECT|TEXTAREA|BUTTON/.test(e.target.tagName);}
 document.addEventListener('keydown',e=>{if(activeForm(e))return;if(['Space','ArrowLeft','ArrowRight','ArrowUp','KeyA','KeyD','KeyW','KeyR'].includes(e.code))e.preventDefault();if(!e.repeat&&['Space','ArrowUp','KeyW'].includes(e.code))press=true;if(e.code==='KeyR')reset();keys.add(e.code);});
 document.addEventListener('keyup',e=>{if(['Space','ArrowUp','KeyW'].includes(e.code))release=true;keys.delete(e.code);});window.addEventListener('blur',()=>{keys.clear();press=false;release=true;});
 const touch=document.createElement('div');touch.className='touch-controls';touch.innerHTML='<button aria-label="Move left">←</button><button aria-label="Move right">→</button><button class="jump">Jump</button>';L.$('stage').append(touch);
 [...touch.children].forEach((b,i)=>{const k=['KeyA','KeyD','Space'][i];b.addEventListener('pointerdown',e=>{e.preventDefault();b.setPointerCapture(e.pointerId);keys.add(k);if(i===2)press=true;});for(const event of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(event,()=>{keys.delete(k);if(i===2)release=true;});});
 function tick(dt){let move=(keys.has('KeyD')||keys.has('ArrowRight')?1:0)-(keys.has('KeyA')||keys.has('ArrowLeft')?1:0),jump=press;
  if(trial){move=trial.type==='coyote'&&s.x<4?1:0;if(trial.type==='coyote'){if(!s.grounded&&trial.left===null)trial.left=s.time;if(trial.left!==null&&!trial.pressed&&s.time-trial.left>=.08){jump=true;trial.pressed=true;}}else if(!trial.pressed&&s.vy<0){const g=2*height()/apex()**2*fall(),landingTime=(s.vy+Math.sqrt(s.vy*s.vy+2*g*s.y))/g;if(landingTime<=.07){jump=true;trial.pressed=true;}}}
  const oldGround=s.grounded;P.step(s,params(),{move,press:jump,release},dt);press=false;release=false;if(!oldGround&&s.grounded)squash=1;if(s.jumps>lastJumps){lastJumps=s.jumps;squash=-.6;}
  if(trial&&trial.pressed&&s.grounded&&s.jumps>0){s.event=trial.type==='coyote'?'Coyote trial passed · landed':'Buffer trial passed · landed';trial=null;}history.push([s.time,s.y]);while(history.length>720)history.shift();if(s.y<-5){const message=s.jumps?'Respawned · try again':'Missed the jump · respawned';reset();s.event=message;}
 }
 const canvas=L.$('graph'),ctx=canvas.getContext('2d');
 function graph(){const w=canvas.clientWidth,h=115;canvas.width=w*devicePixelRatio;canvas.height=h*devicePixelRatio;ctx.scale(devicePixelRatio,devicePixelRatio);ctx.clearRect(0,0,w,h);ctx.strokeStyle='#344150';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(30,90);ctx.lineTo(w-10,90);ctx.stroke();ctx.fillStyle='#9aa2b1';ctx.font='10px monospace';ctx.fillText('HEIGHT / LAST 6 SECONDS',10,15);ctx.fillText('0 m',1,94);ctx.strokeStyle='#ff8a3d';ctx.beginPath();history.forEach(([t,y],i)=>{const x=30+(t-s.time+6)/6*(w-45),py=90-y/5*60;if(i)ctx.lineTo(x,py);else ctx.moveTo(x,py);});ctx.stroke();}
 start(dt=>{if(!paused){acc+=dt;while(acc>=1/120){tick(1/120);acc-=1/120;}squash*=Math.exp(-dt*12);}hero.position.set(s.x,s.y+.55,0);hero.scale.set(1+squash*.2,1-squash*.25,1+squash*.2);L.vector(velocity,new T.Vector3(s.x+.7,s.y+.5,0),new T.Vector3(0,s.vy*.15,0));
  const points=[];const p=params(),g=2*p.height/p.apex**2,v=2*p.height/p.apex;for(let t=0;t<=p.apex*2;t+=.03){const yy=v*t-.5*g*t*t;if(yy>=0)points.push(new T.Vector3(-6+p.speed*t,yy+.55,-.6));}L.replaceLine(ghost,points);
  L.stat(0,s.vy.toFixed(2)+' m/s');L.stat(1,(s.consumed?0:s.grounded?coyote():Math.max(0,p.coyote-(s.time-s.lastGround))*1000).toFixed(0)+' ms');L.stat(2,Math.max(0,(s.bufferUntil-s.time)*1000).toFixed(0)+' ms');L.pill((paused?'PAUSED · ':'')+s.event);L.$('gravity-value').textContent=g.toFixed(1);graph();window.demoState={...s,paused,trial:trial?.type};
 });
})();
