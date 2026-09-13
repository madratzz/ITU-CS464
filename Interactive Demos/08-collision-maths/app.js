'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const mode=L.select('mode','Contact response',[['bounce','Reflect / bounce'],['slide','Slide along surface']]);
  const angle=L.slider('angle','Incidence from normal',-65,65,30,1,'°'),normalAngle=L.slider('normal','Wall rotation',-70,70,0,1,'°');
  const speed=L.slider('speed','Incoming speed',2,12,7,.1,' m/s'),restitution=L.slider('restitution','Restitution',0,1,1,.05),friction=L.slider('friction','Tangential loss',0,1,0,.05);
  let p=new T.Vector3(),v=new T.Vector3(),n=new T.Vector3(),tangent=new T.Vector3(),time=0,hits=0,outgoing=0,launched=false;
  const reset=()=>{time=0;hits=0;outgoing=0;launched=false;updateLaunch();path.clear();};
  L.buttons([['launch','Launch ball',()=>{reset();launched=true;run.running=true;L.$('play').textContent='Pause';},true]]);
  const run=X.playback(reset,{running:false});L.hint('Teal = outward wall normal. Orange = incoming/current velocity. Blue = resolved velocity after contact. Relaunch after changing a contact parameter.');
  const {scene,start}=L.engine({position:[12,15,19],look:[0,0,2]});const wall=L.box(40,2,.18,0x54627a,0,1,0),ball=L.sphere(.35,C.orange),normal=L.arrow(C.teal),velocity=L.arrow(C.orange),resolved=L.arrow(C.blue);scene.add(wall,ball,normal,velocity,resolved);const path=X.trail(C.orange,scene);
  function updateLaunch(){n.set(Math.sin(L.rad(normalAngle())),0,Math.cos(L.rad(normalAngle())));tangent.set(n.z,0,-n.x);p.copy(n).multiplyScalar(6).addScaledVector(tangent,-2);v.copy(n).multiplyScalar(-Math.cos(L.rad(angle()))*speed()).addScaledVector(tangent,Math.sin(L.rad(angle()))*speed());}
  updateLaunch();X.help('A normalized normal separates tangential motion from motion into the wall');
  const tick=X.fixed(dt=>{time+=dt;p.addScaledVector(v,dt);if(p.dot(n)<.35&&v.dot(n)<0){p.addScaledVector(n,.35-p.dot(n));const a=DemoMath.reflect([v.x,v.z],[n.x,n.z],restitution(),friction(),mode()==='slide');v.set(a[0],0,a[1]);hits++;outgoing=v.length();L.vector(resolved,p.clone().setY(.6),v.clone().multiplyScalar(.5));}if(time>3)run.running=false;});
  start(dt=>{if(!launched)updateLaunch();if(run.running){launched=true;tick(dt);path.add(p.clone().setY(.35));}wall.rotation.y=Math.atan2(n.x,n.z);ball.position.copy(p).setY(.35);L.vector(normal,new T.Vector3(0,.1,0),n.clone().multiplyScalar(3));L.vector(velocity,p.clone().setY(.6),v.clone().multiplyScalar(.4));resolved.visible=hits>0;L.stat(0,p.dot(n).toFixed(2)+' m');L.stat(1,(hits?outgoing:0).toFixed(2)+' m/s');L.stat(2,hits);L.pill(hits?'CONTACT RESOLVED · '+mode().toUpperCase():launched?'APPROACHING WALL':'READY · LAUNCH A BALL');L.$('play').textContent=run.running?'Pause':'Play';window.demoState={hits,time,signedDistance:p.dot(n),speed:v.length(),outgoing,velocity:v.toArray(),normal:n.toArray()};});
})();
