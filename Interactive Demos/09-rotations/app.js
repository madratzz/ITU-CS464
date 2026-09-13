'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const mode=L.select('mode','Experiment',[['interpolate','Euler vs quaternion interpolation'],['gimbal','Euler axes / gimbal lock']]);
  const method=L.select('method','Quaternion interpolation',[['slerp','SLERP · constant angular speed'],['nlerp','Normalized LERP']]);
  const from=L.slider('from','Start yaw',-180,180,170,1,'°'),to=L.slider('to','End yaw',-180,180,-170,1,'°'),scrub=L.slider('scrub','Interpolation time',0,100,50,1,'%');
  const yaw=L.slider('yaw','Gimbal yaw',-180,180,20,1,'°'),pitch=L.slider('pitch','Gimbal pitch',-90,90,65,1,'°'),roll=L.slider('roll','Gimbal roll',-180,180,0,1,'°');
  let time=.5;const run=X.playback(()=>{time=.5;L.set('scrub',50);},{running:false});
  L.$('scrub').addEventListener('input',()=>{time=scrub()/100;run.running=false;L.$('play').textContent='Play';});
  L.buttons([['lock','Show gimbal lock',()=>{L.set('mode','gimbal');L.set('pitch',90);sync();}]]);
  function sync(){const inter=mode()==='interpolate';for(const id of ['from','to','scrub','method'])L.$(id).disabled=!inter;for(const id of ['yaw','pitch','roll'])L.$(id).disabled=inter;}
  L.$('mode').addEventListener('change',sync);sync();L.hint('Left: raw Euler numbers. Right: quaternion orientation. In the gimbal view, teal is the outer yaw axis and orange is the inner roll axis.');
  const {scene,start}=L.engine({position:[11,13,21],look:[0,2,0],orbit:true});const planes=[X.aircraft(C.teal),X.aircraft(C.orange)];planes.forEach((p,i)=>{p.position.set(i===0?-4:4,2,0);scene.add(p);});
  const labels=[L.label('EULER','#55d6c2'),L.label('QUATERNION','#ff8a3d')];labels.forEach((p,i)=>{p.position.set(i===0?-4:4,.2,3.5);scene.add(p);});
  const axes=[L.arrow(C.teal),L.arrow(C.orange),L.arrow(C.blue)];scene.add(...axes);X.help('Drag to orbit · At ±90° pitch, the yaw and roll axes become parallel');
  start(dt=>{
    if(run.running&&mode()==='interpolate'){time=(time+dt*.3)%1;L.$('scrub').value=time*100;L.$('scrub-out').textContent=(time*100).toFixed(0)+'%';}
    const q0=new T.Quaternion().setFromAxisAngle(new T.Vector3(0,1,0),L.rad(from())),q1=new T.Quaternion().setFromAxisAngle(new T.Vector3(0,1,0),L.rad(to()));
    const q=q0.clone();if(method()==='slerp')q.slerp(q1,time);else{const sign=q0.dot(q1)<0?-1:1;q.set(q0.x*(1-time)+q1.x*time*sign,q0.y*(1-time)+q1.y*time*sign,q0.z*(1-time)+q1.z*time*sign,q0.w*(1-time)+q1.w*time*sign).normalize();}
    const inter=mode()==='interpolate';planes[1].visible=inter;labels.forEach(l=>l.visible=inter);planes[0].position.x=inter?-4:0;
    const eulerYaw=from()+(to()-from())*time;
    if(inter){planes[0].quaternion.setFromEuler(new T.Euler(0,L.rad(eulerYaw),0));planes[1].quaternion.copy(q);}else planes[0].quaternion.setFromEuler(new T.Euler(L.rad(pitch()),L.rad(yaw()),L.rad(roll()),'YXZ'));
    const yawAxis=new T.Vector3(0,1,0),rollAxis=new T.Vector3(0,0,1).applyEuler(new T.Euler(L.rad(pitch()),L.rad(yaw()),0,'YXZ')),pitchAxis=new T.Vector3(1,0,0).applyAxisAngle(yawAxis,L.rad(yaw()));
    axes.forEach((a,i)=>{a.visible=!inter;if(!inter)L.vector(a,new T.Vector3(0,2,0),[yawAxis,rollAxis,pitchAxis][i].clone().multiplyScalar(4));});
    const alignment=Math.abs(yawAxis.dot(rollAxis));L.stat(0,(inter?eulerYaw:yaw()).toFixed(1)+'°');L.stat(1,L.deg(q0.angleTo(q)).toFixed(1)+'°');L.stat(2,alignment.toFixed(3));L.pill(inter?'RAW ANGLES VS SHORTEST ORIENTATION PATH':alignment>.999?'GIMBAL LOCK · TWO AXES ALIGNED':'THREE DISTINCT ROTATION AXES');window.demoState={mode:mode(),t:time,eulerYaw,quaternionTurn:L.deg(q0.angleTo(q)),shortestPath:L.deg(q0.angleTo(q1)),alignment};
  });
})();
