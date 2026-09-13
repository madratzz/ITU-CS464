'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const px=L.slider('px','Parent world X',-5,5,1,.1),yaw=L.slider('yaw','Parent yaw',-180,180,30,1,'°'),scale=L.slider('scale','Parent scale',.5,2,1,.1);
  const lx=L.slider('lx','Child local X',-4,4,2,.1),ly=L.slider('ly','Child local Y',.3,4,1.2,.1),lz=L.slider('lz','Child local Z',-4,4,0,.1);
  const lock=L.check('lock','Keep child position fixed in world',false),animate=L.check('animate','Animate the parent transform',false);
  let time=0,locked=null;const run=X.playback(()=>{time=0;locked=null;L.$('lock').checked=false;for(const [id,v]of Object.entries({px:1,yaw:30,scale:1,lx:2,ly:1.2,lz:0}))L.set(id,v);});
  L.hint('Small RGB axes belong to the teal parent; larger RGB axes mark world space. With the lock enabled, local coordinates are derived from the fixed world point.');
  const {scene,start}=L.engine({position:[14,13,18],look:[0,1,0],orbit:true});const parent=new T.Group();parent.add(L.box(4,.35,3,0x3c6965,0,.25,0));parent.add(new T.AxesHelper(3));scene.add(parent);
  const turret=L.tank();turret.group.scale.setScalar(.5);parent.add(turret.group);const worldAxes=new T.AxesHelper(6);scene.add(worldAxes);
  const line=L.line([[0,0,0],[1,1,1]],C.orange,true);scene.add(line);const marker=L.sphere(.15,C.pink);scene.add(marker);
  L.$('lock').addEventListener('change',()=>{scene.updateMatrixWorld(true);locked=lock()?turret.group.getWorldPosition(new T.Vector3()):null;});
  X.help('Drag to orbit · Scale, rotate and translate the parent to change coordinate space');
  start(dt=>{if(run.running)time+=dt;parent.position.x=px()+(animate()?Math.sin(time)*2:0);parent.rotation.y=L.rad(yaw())+(animate()?time*.3:0);parent.scale.setScalar(scale());parent.updateMatrixWorld(true);
    if(lock()&&locked)turret.group.position.copy(parent.worldToLocal(locked.clone()));else turret.group.position.set(lx(),ly(),lz());
    for(const id of ['lx','ly','lz'])L.$(id).disabled=lock();scene.updateMatrixWorld(true);const world=turret.group.getWorldPosition(new T.Vector3()),local=turret.group.position.clone(),roundTrip=parent.worldToLocal(world.clone());marker.visible=lock();if(locked)marker.position.copy(locked);L.replaceLine(line,[parent.position.clone(),world]);
    const fmt=v=>v.toArray().map(n=>n.toFixed(2)).join(', ');L.stat(0,fmt(local));L.stat(1,fmt(world));L.stat(2,roundTrip.distanceTo(local).toExponential(1));L.pill(lock()?'WORLD POSITION LOCKED · LOCAL COORDINATES CHANGE':'CHILD INHERITS PARENT TRANSFORM');window.demoState={local:local.toArray(),world:world.toArray(),error:roundTrip.distanceTo(local),locked:lock(),parentYaw:parent.rotation.y};
  });
})();
