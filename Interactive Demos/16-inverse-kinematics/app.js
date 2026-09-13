'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const mode=L.select('mode','Placement mode',[['free','Free foot target'],['terrain','Foot on sloped terrain']]);
  const tx=L.slider('tx','Foot target X',-6,6,2,.1),ty=L.slider('ty','Foot target Y (free mode)',-1,6,0,.1),upper=L.slider('upper','Upper bone length',1,4,2.5,.1),lower=L.slider('lower','Lower bone length',1,4,2.5,.1),hip=L.slider('hip','Hip height',2,6,4,.1),slope=L.slider('slope','Terrain slope',-25,25,10,1,'°');
  const reverse=L.check('reverse','Reverse knee bend',false),adjust=L.check('adjust','Adjust body height to reach terrain',false),walk=L.check('walk','Animate a procedural step',false);
  let time=0;const run=X.playback(()=>{time=0;L.set('tx',2);L.set('ty',0);});L.hint('Orange marker = requested foot. Teal = solved limb. Magenta segment = unreachable distance. The foot aligns with the ground in terrain mode.');
  const e=L.engine({position:[0,3,23],look:[0,2,0],grid:22}),{scene,start}=e;for(const o of scene.children){if(o.isMesh&&o.geometry.type==='PlaneGeometry')o.position.y=-2;if(o.isGridHelper)o.position.y=-1.99;}
  const bones=[X.bone(C.teal),X.bone(C.blue)],joints=[L.sphere(.22,C.teal),L.sphere(.22,C.orange),L.sphere(.18,C.teal)],foot=L.box(.8,.18,.4,C.teal),body=L.box(1.1,.65,.75,0x74869e),target=L.sphere(.16,C.orange),error=L.line([[0,0,0],[0,1,0]],C.pink,true),ground=L.box(18,.15,3,0x3c4c60);scene.add(...bones,...joints,foot,body,target,error,ground);
  X.onPlane(e,new T.Plane(new T.Vector3(0,0,1),0),p=>{L.$('walk').checked=false;L.set('tx',L.clamp(p.x,-6,6));L.set('ty',L.clamp(p.y,-1,6));},{draggable:true});X.help('Drag in the scene to place the foot · The solver preserves both bone lengths');
  start(dt=>{if(run.running)time+=dt;const terrain=mode()==='terrain',x=walk()?Math.sin(time*1.5)*3:tx(),terrainY=x*Math.tan(L.rad(slope()));const y=terrain?terrainY+.18+(walk()?Math.max(0,Math.cos(time*1.5))*.8:0):ty();
    let rootY=hip();if(terrain&&adjust()){const maxVertical=Math.sqrt(Math.max(.001,(upper()+lower()-.05)**2-x*x));rootY=Math.min(rootY,y+maxVertical);}
    const root=[0,rootY],requested=[x,y],result=DemoMath.ik(root,requested,upper(),lower(),reverse()?-1:1),positions=[root,result.knee,result.foot].map(p=>new T.Vector3(p[0],p[1],0));
    X.segment(bones[0],positions[0],positions[1]);X.segment(bones[1],positions[1],positions[2]);joints.forEach((j,i)=>j.position.copy(positions[i]));foot.position.copy(positions[2]);foot.rotation.z=terrain?L.rad(slope()):0;body.position.set(0,rootY+.5,0);target.position.set(x,y,.2);L.replaceLine(error,[positions[2],new T.Vector3(x,y,0)]);ground.rotation.z=terrain?L.rad(slope()):0;ground.position.y=terrain?0:-1.5;L.$('ty').disabled=terrain;L.$('slope').disabled=!terrain;
    L.stat(0,result.error.toFixed(3)+' m');L.stat(1,L.deg(result.kneeAngle).toFixed(1)+'°');L.stat(2,result.reachable?'Reachable':'Clamped');L.pill(result.reachable?'TARGET REACHED':'TARGET OUTSIDE REACH · CLOSEST VALID POSE');window.demoState={root,knee:result.knee,foot:result.foot,target:requested,error:result.error,reachable:result.reachable,upper:upper(),lower:lower(),rootHeight:rootY};
  });
})();
