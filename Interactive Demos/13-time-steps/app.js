'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const fps=L.select('fps','Simulated frame rate',[['15','15 FPS'],['30','30 FPS'],['60','60 FPS'],['144','144 FPS']],'30');
  const speed=L.slider('speed','Movement speed',1,6,4,.1,' m/s'),rate=L.slider('rate','Trial playback speed',.2,1,1,.1,'×'),hitch=L.check('hitch','Inject 200 ms hitches',false);
  let elapsed=0,lastFrame=0,nextFrame=0,frames=0,acc=0,dist=[0,0,0],complete=false;
  function reset(){elapsed=0;lastFrame=0;nextFrame=1/(+fps());frames=0;acc=0;dist=[0,0,0];complete=false;}
  L.buttons([['trial','Run two-second trial',()=>{reset();run.running=true;L.$('play').textContent='Pause';},true]]);
  const run=X.playback(reset,{running:false});reset();L.hint('Orange = speed / 60 per frame. Teal = speed × frame duration. Blue = fixed 120 Hz simulation. Marks show distance; the green marker is the expected two-second result.');
  for(const id of ['fps','speed','hitch'])L.$(id).addEventListener('change',()=>{reset();run.running=false;L.$('play').textContent='Play';});
  const {scene,start}=L.engine({position:[12,13,22],look:[0,0,0],grid:28}),bodies=[];const targetMarker=L.line([[0,0,0],[0,0,1]],C.teal,true);scene.add(targetMarker);
  for(let i=0;i<3;i++){scene.add(L.box(17,.1,1.8,0x293443,.5,0,(i-1)*3));const b=L.box(.65,.65,.65,[C.orange,C.teal,C.blue][i],-7,.4,(i-1)*3);scene.add(b);bodies.push(b);const label=L.label(['FRAME BASED','DELTA TIME','FIXED STEP'][i]);label.scale.multiplyScalar(.6);label.position.set(-8.4,.2,(i-1)*3);scene.add(label);}
  X.help('Simulated update FPS is independent of browser FPS · All lanes share one clock');
  function simulateFrame(at){const dt=at-lastFrame;lastFrame=at;frames++;dist[0]+=speed()/60;dist[1]+=speed()*dt;acc+=dt;while(acc>=1/120-1e-10){dist[2]+=speed()/120;acc-=1/120;}}
  start(dt=>{if(run.running&&!complete){elapsed=Math.min(2,elapsed+dt*rate());while(nextFrame<=elapsed+1e-9&&nextFrame<=2+1e-9){simulateFrame(Math.min(2,nextFrame));const old=nextFrame;nextFrame+=1/(+fps());if(hitch()&&Math.floor(old*2)!==Math.floor(nextFrame*2)&&nextFrame<1.9)nextFrame+=.2;}if(elapsed>=2){if(lastFrame<2-1e-9)simulateFrame(2);complete=true;run.running=false;L.$('play').textContent='Play';}}
    bodies.forEach((b,i)=>b.position.x=-7+dist[i]*.5);const expected=speed()*2;L.replaceLine(targetMarker,[new T.Vector3(-7+expected*.5,.1,-4.2),new T.Vector3(-7+expected*.5,.1,4.2)]);
    L.stat(0,elapsed.toFixed(2)+' / 2.00 s');L.stat(1,dist[0].toFixed(2)+' m');L.stat(2,dist[1].toFixed(2)+' m');L.pill(complete?'COMPLETE · EXPECTED '+expected.toFixed(2)+' m':run.running?'SIMULATING '+fps()+' FPS':'READY · RUN A TRIAL');window.demoState={elapsed,frames,distances:[...dist],expected,complete,simulatedFPS:+fps()};
  });
})();
