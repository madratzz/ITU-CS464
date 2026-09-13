'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const mode=L.select('mode','Behaviour',[['seek','Seek'],['flee','Flee'],['arrive','Arrive'],['pursue','Pursue'],['evade','Evade']],'arrive');
  const maxSpeed=L.slider('speed','Maximum speed',1,8,4,.1,' m/s'),force=L.slider('force','Maximum acceleration',1,15,5,.1,' m/s²');
  const radius=L.slider('radius','Arrival slowing radius',1,6,3,.1,' m');
  const tx=L.slider('tx','Target X',-9,9,6,.1),tz=L.slider('tz','Target Z',-9,9,3,.1);
  const moving=L.check('moving','Move the target',false),avoid=L.check('avoid','Avoid the central obstacle',true);
  let time=0,pos=new T.Vector3(-6,0,-3),vel=new T.Vector3(),steer=new T.Vector3(),desired=new T.Vector3(),target=new T.Vector3(),prediction=new T.Vector3(),avoiding=false;
  const reset=()=>{time=0;pos.set(-6,0,-3);vel.set(0,0,0);};const run=X.playback(reset);
  L.hint('Orange = agent; teal = target / desired velocity; blue = actual velocity; magenta = acceleration. Target sliders and clicking the ground are equivalent.');
  const e=L.engine({position:[14,19,21],look:[0,0,0]}),{scene,start}=e;
  const agent=L.tank();agent.group.scale.setScalar(.65);agent.group.traverse(o=>{if(o.isMesh&&[C.teal,0x436c65].includes(o.material.color.getHex()))o.material.color.setHex(C.orange);});scene.add(agent.group);
  const marker=L.sphere(.35,C.teal),ghost=L.sphere(.16,C.pink);scene.add(marker,ghost);
  const obstacle=new T.Mesh(new T.CylinderGeometry(1.6,1.6,1.8,40),L.material(0x4e5872));obstacle.position.y=.9;scene.add(obstacle);
  const arrows=[L.arrow(C.teal),L.arrow(C.blue),L.arrow(C.pink)];scene.add(...arrows);const trail=X.trail(0x596675,scene);
  X.onPlane(e,new T.Plane(new T.Vector3(0,1,0),0),p=>{L.$('moving').checked=false;L.set('tx',L.clamp(p.x,-9,9));L.set('tz',L.clamp(p.z,-9,9));});X.help('Click the floor to set a target · Agent stays inside the ±10 m field');
  const tick=X.fixed(dt=>{
    time+=dt;const targetVelocity=moving()?new T.Vector3(3*Math.cos(time*.5),0,-3*Math.sin(time*.5)):new T.Vector3();target.set(moving()?6*Math.sin(time*.5):tx(),0,moving()?6*Math.cos(time*.5):tz());
    prediction.copy(target);const distance=pos.distanceTo(target);if(['pursue','evade'].includes(mode()))prediction.addScaledVector(targetVelocity,Math.min(2,distance/maxSpeed()));
    desired.copy(prediction).sub(pos);const d=desired.length();if(d>1e-8)desired.multiplyScalar(1/d);if(['flee','evade'].includes(mode()))desired.negate();
    const speed=mode()==='arrive'?maxSpeed()*Math.min(1,d/radius()):maxSpeed();desired.multiplyScalar(speed);steer.copy(desired).sub(vel);avoiding=false;
    if(avoid()){
      const forward=vel.length()>.1?vel.clone().normalize():desired.clone().normalize();const ahead=-pos.dot(forward),closest=pos.clone().addScaledVector(forward,Math.max(0,ahead));
      if(ahead>=0&&ahead<2+vel.length()&&closest.length()<2.4){const side=new T.Vector3(-forward.z,0,forward.x);if(closest.dot(side)<0)side.negate();steer.addScaledVector(side,force()*2);avoiding=true;}
    }
    steer.clampLength(0,force());vel.addScaledVector(steer,dt).clampLength(0,maxSpeed());pos.addScaledVector(vel,dt);
    if(avoid()&&pos.length()<2){const n=pos.length()>1e-6?pos.clone().normalize():new T.Vector3(1,0,0);pos.copy(n).multiplyScalar(2);if(vel.dot(n)<0)vel.addScaledVector(n,-vel.dot(n));}
    for(const a of ['x','z'])if(Math.abs(pos[a])>10){pos[a]=L.clamp(pos[a],-10,10);vel[a]=0;}
  });
  start(dt=>{if(run.running){tick(dt);trail.add(pos.clone().setY(.04));}else if(!moving())target.set(tx(),0,tz());agent.group.position.copy(pos);if(vel.length()>.1)agent.group.rotation.y=Math.atan2(vel.x,vel.z);marker.position.copy(target).setY(.4);ghost.position.copy(prediction).setY(.2);ghost.visible=['pursue','evade'].includes(mode());obstacle.visible=avoid();
    const origin=pos.clone().setY(1);[desired,vel,steer.clone().multiplyScalar(.3)].forEach((v,i)=>L.vector(arrows[i],origin,v));L.stat(0,pos.distanceTo(target).toFixed(2)+' m');L.stat(1,vel.length().toFixed(2)+' m/s');L.stat(2,steer.length().toFixed(2)+' m/s²');L.pill(mode().toUpperCase()+(avoiding?' · AVOIDING OBSTACLE':''));window.demoState={mode:mode(),position:pos.toArray(),distance:pos.distanceTo(target),speed:vel.length(),force:steer.length(),avoiding};
  });
})();
