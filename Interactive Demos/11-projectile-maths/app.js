'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const mode=L.select('mode','Experiment',[['lead','Lead a moving target'],['ballistic','Choose a ballistic launch angle']]);
  const speed=L.slider('speed','Launch speed',5,25,16,.1,' m/s'),gravity=L.slider('gravity','Gravity',0,20,9.8,.1,' m/s²'),angle=L.slider('angle','Ballistic launch angle',10,80,45,1,'°');
  const targetX=L.slider('target','Target X',0,8,4,.1,' m'),targetSpeed=L.slider('target-speed','Target velocity X',-3,6,4,.1,' m/s');
  let shot=null,last='READY',solution=null;
  const origin=new T.Vector3(-8,.5,0),balls=[],paths=[];
  function settings(){const r=[targetX()-origin.x,1-origin.y];return {v:targetSpeed(),g:gravity(),r,s:speed()};}
  function launch(){const p=settings();const lead=DemoMath.intercept(p.r,[p.v,0],p.s,p.g),naive=DemoMath.intercept(p.r,[0,0],p.s,p.g);solution=lead;const ballistic=[p.s*Math.cos(L.rad(angle())),p.s*Math.sin(L.rad(angle()))];if(mode()==='lead'&&!lead){shot=null;last='NO INTERCEPTION WITHIN 12 SECONDS';return;}
    shot={time:0,x:targetX(),vx:mode()==='lead'?p.v:0,g:p.g,velocities:mode()==='lead'?[lead.velocity,naive?.velocity||[0,0]]:[ballistic],hits:[false,false],end:mode()==='lead'?lead.t+.45:5};last='IN FLIGHT';paths.forEach(t=>t.clear());run.running=true;L.$('play').textContent='Pause';}
  L.buttons([['launch','Launch comparison',launch,true]]);const run=X.playback(()=>{shot=null;last='READY';paths.forEach(p=>p.clear());},{running:false});L.hint('Orange = leading solution or chosen arc. Teal = aim at the target’s initial position with the same speed. Target velocity and gravity are held constant during a trial.');
  const {scene,start}=L.engine({position:[1,8,28],look:[1,3,0],grid:36});scene.add(L.box(1,1,1,0x59697c,-8,0,0));const target=L.box(.8,1,.8,C.teal,targetX(),1,0);scene.add(target);
  for(const color of [C.orange,C.teal]){const b=L.sphere(.2,color);scene.add(b);balls.push(b);paths.push(X.trail(color,scene,500));}
  const guide=L.line([[0,0,0],[1,1,0]],0x617084,true);scene.add(guide);let key='';X.help('The target travels at constant velocity during each shot · Relaunch to apply tuning');
  start(dt=>{const k=[mode(),speed(),gravity(),targetX(),targetSpeed(),angle()].join(':');if(k!==key&&!shot){key=k;const p=settings();solution=DemoMath.intercept(p.r,[p.v,0],p.s,p.g);const vel=mode()==='lead'?solution?.velocity:[p.s*Math.cos(L.rad(angle())),p.s*Math.sin(L.rad(angle()))],pts=[];if(vel)for(let t=0;t<(mode()==='lead'?solution.t:4);t+=.04){const y=origin.y+vel[1]*t-.5*p.g*t*t;if(y<0)break;pts.push(new T.Vector3(origin.x+vel[0]*t,y,0));}L.replaceLine(guide,pts);}
    if(shot&&run.running){shot.time+=dt;const t=shot.time;target.position.set(shot.x+shot.vx*t,1,0);shot.velocities.forEach((v,i)=>{const b=balls[i];const old=b.position.clone();b.position.set(origin.x+v[0]*t,origin.y+v[1]*t-.5*shot.g*t*t,0);paths[i].add(b.position);const prevT=Math.max(0,t-dt),r0=new T.Vector3(origin.x+v[0]*prevT-shot.x-shot.vx*prevT,origin.y+v[1]*prevT-.5*shot.g*prevT*prevT-1,0),r1=b.position.clone().sub(target.position),delta=r1.clone().sub(r0);const u=delta.lengthSq()?L.clamp(-r0.dot(delta)/delta.lengthSq(),0,1):0;if(r0.addScaledVector(delta,u).length()<.6)shot.hits[i]=true;});if(t>=shot.end){run.running=false;L.$('play').textContent='Play';last=shot.hits[0]?'LEADING / ORANGE SHOT HIT':'TRIAL COMPLETE · NO HIT';}}
    if(!shot)target.position.set(targetX(),1,0);balls.forEach((b,i)=>b.visible=!!shot&&i<shot.velocities.length&&b.position.y>=0);guide.visible=!shot;
    L.stat(0,(shot?shot.time:solution?.t||0).toFixed(2)+' s');L.stat(1,speed().toFixed(1)+' m/s');L.stat(2,shot?.hits[0]?'Orange HIT':shot?.hits[1]?'Teal HIT':'—');L.pill(last);window.demoState={time:shot?.time||0,solution:solution?{time:solution.t,velocity:solution.velocity}:null,hits:shot?.hits||[],target:target.position.toArray(),status:last};
  });
})();
