'use strict';
(() => {
 const L=Lab,T=THREE,C=L.colors;
 const heading=L.slider('heading','Tank heading',-180,180,0,1,'°');
 const angle=L.slider('angle','Target bearing',-180,180,32,1,'°');
 const distance=L.slider('distance','Target distance',1,12,6,.1,' m');
 const fov=L.slider('fov','Field of view',10,180,90,1,'°');
 const range=L.slider('range','Detection range',2,12,9,.1,' m');
 const occlusion=L.check('occlusion','Add an occluding wall',false);
 const tracking=L.check('tracking','Turret tracks the target',false);
 const auto=L.check('auto','Orbit target automatically',false);
 L.buttons([['front','In front',()=>{L.set('angle',heading());L.set('distance',6);}],['behind','Behind',()=>L.set('angle',(heading()+360)%360-180)]]);
 L.buttons([['reset','Reset lab',()=>{for(const [id,v]of Object.entries({heading:0,angle:32,distance:6,fov:90,range:9}))L.set(id,v);for(const id of ['occlusion','tracking','auto'])L.$(id).checked=false;turretYaw=0;}]]);
 L.hint('<b>Read the colours:</b> teal = forward, orange = direction to target, blue = projection.<br>Drag the scene to orbit. Scroll to zoom.');
 const {scene,start}=L.engine({position:[13,15,19],look:[0,0,2],orbit:true});
 const tank=L.tank();scene.add(tank.group);
 const enemy=new T.Group();enemy.add(L.box(.85,1,.85,C.orange,0,.65,0));enemy.add(L.sphere(.28,0xffce9a,0,1.4,0));scene.add(enemy);
 const wall=L.box(3,2,1.4,0x59677c,0,1,3.7);scene.add(wall);
 const forward=L.arrow(C.teal),direction=L.arrow(C.orange),projection=L.arrow(C.blue);scene.add(forward,direction,projection);
 const perp=L.line([[0,0,0],[1,0,1]],C.blue,true);scene.add(perp);
 const ring=new T.Mesh(new T.RingGeometry(.7,.77,48),new T.MeshBasicMaterial({color:C.orange,side:T.DoubleSide}));ring.rotation.x=-Math.PI/2;ring.position.y=.025;scene.add(ring);
 const targetLabel=L.label('TARGET','#ffae73');scene.add(targetLabel);
 let cone=null,key='',turretYaw=0;
 // Segment / axis-aligned rectangle intersection. t is distance along the segment [0,1].
 function blocked(x,z){let lo=0,hi=1;for(const [delta,min,max]of [[x,-1.5,1.5],[z,3,4.4]]){if(Math.abs(delta)<1e-8){if(0<min||0>max)return false;}else{let a=min/delta,b=max/delta;if(a>b)[a,b]=[b,a];lo=Math.max(lo,a);hi=Math.min(hi,b);if(lo>hi)return false;}}return hi>0&&lo<1;}
 start(dt=>{
  if(auto())L.set('angle',((angle()+dt*24+180)%360)-180);
  const h=L.rad(heading()),a=L.rad(angle()),d=distance();
  const f=new T.Vector3(Math.sin(h),0,Math.cos(h)),to=new T.Vector3(Math.sin(a),0,Math.cos(a));
  const dot=L.clamp(f.dot(to),-1,1),cross=new T.Vector3().crossVectors(f,to).y;
  const signed=L.deg(Math.atan2(cross,dot)),threshold=Math.cos(L.rad(fov()/2));
  enemy.position.copy(to).multiplyScalar(d);ring.position.set(enemy.position.x,.025,enemy.position.z);targetLabel.position.copy(enemy.position).add(new T.Vector3(0,2,0));
  tank.group.rotation.y=h;wall.visible=occlusion();
  if(tracking()){const desired=L.rad(signed);turretYaw+=Math.atan2(Math.sin(desired-turretYaw),Math.cos(desired-turretYaw))*(1-Math.exp(-5*dt));}tank.turret.rotation.y=turretYaw;
  const origin=new T.Vector3(0,1.6,0);L.vector(forward,origin,f.clone().multiplyScalar(4));L.vector(direction,origin,to.clone().multiplyScalar(d));
  const projected=f.clone().multiplyScalar(d*dot);L.vector(projection,new T.Vector3(0,.17,0),projected);L.replaceLine(perp,[enemy.position.clone().setY(.17),projected.clone().setY(.17)]);
  const newKey=fov()+':'+range();if(newKey!==key){key=newKey;if(cone){scene.remove(cone);cone.geometry.dispose();cone.material.dispose();}const points=[0,.02,0];const half=L.rad(fov()/2),r=range();for(let i=0;i<64;i++){const a0=-half+i/64*half*2,a1=-half+(i+1)/64*half*2;points.push(0,.02,0,Math.sin(a0)*r,.02,Math.cos(a0)*r,Math.sin(a1)*r,.02,Math.cos(a1)*r);}const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(points.slice(3),3));cone=new T.Mesh(geo,new T.MeshBasicMaterial({color:C.teal,transparent:true,opacity:.09,side:T.DoubleSide,depthWrite:false}));scene.add(cone);}cone.rotation.y=h;
  const inAngle=dot>=threshold-1e-8,inRange=d<=range(),hidden=occlusion()&&blocked(enemy.position.x,enemy.position.z),visible=inAngle&&inRange&&!hidden;
  const status=!inRange?'OUT OF RANGE':!inAngle?'OUTSIDE VIEW CONE':hidden?'OCCLUDED BY WALL':'TARGET IN SIGHT';
  L.pill(status,visible?'#55d6c2':'#ff8a3d');ring.material.color.setHex(visible?C.teal:C.orange);
  L.stat(0,dot.toFixed(3));L.stat(1,signed.toFixed(1)+'° '+(Math.abs(signed)<.1?'ahead':signed>0?'right':'left'));L.stat(2,(d*dot).toFixed(2)+' m');
  L.$('threshold').textContent=threshold.toFixed(3);
  window.demoState={dot,signed,projection:d*dot,visible,inAngle,inRange,hidden};
 });
})();
