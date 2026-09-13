'use strict';
(() => {
 const L=Lab,T=THREE,C=L.colors;
 const mode=L.select('mode','Application',[['flight','Aircraft · local coordinate frame'],['normal','Triangle · surface normal']]);
 const yaw=L.slider('yaw','Yaw / heading',-180,180,25,1,'°');
 const pitch=L.slider('pitch','Pitch / nose up',-80,80,15,1,'°');
 const bank=L.slider('bank','Roll / bank',-180,180,-20,1,'°');
 const height=L.slider('height','Triangle vertex B height',-3,5,1.5,.1,' m');
 const flip=L.check('flip','Reverse the cross-product order',false);
 L.buttons([['level','Level flight',()=>{for(const id of ['yaw','pitch','bank'])L.set(id,0);}],['reset','Reset lab',()=>{L.set('mode','flight');L.set('yaw',25);L.set('pitch',15);L.set('bank',-20);L.set('height',1.5);L.$('flip').checked=false;updateControls();}]]);
 L.hint('<b>Read the colours:</b> teal = forward / AB, orange = right / AC, blue = cross product.<br>Drag to inspect the 3D geometry; scroll to zoom.');
 function updateControls(){const isFlight=mode()==='flight';for(const id of ['yaw','pitch','bank'])L.$(id).disabled=!isFlight;L.$('height').disabled=isFlight;}
 L.$('mode').addEventListener('change',updateControls);updateControls();
 const {scene,start}=L.engine({position:[9,8,12],look:[0,2,0],orbit:true});
 const plane=new T.Group();plane.add(L.box(.65,.5,4.3,0xd1dbe7));plane.add(L.box(5.8,.14,1.25,C.teal,0,0,-.2));plane.add(L.box(2.1,.12,.7,C.teal,0,.2,-1.8));plane.add(L.box(.12,.95,.8,C.orange,0,.5,-1.75));plane.add(L.sphere(.36,0x4d6f8e,0,.23,.65));const nose=new T.Mesh(new T.ConeGeometry(.33,1,16),L.material(C.orange));nose.rotation.x=Math.PI/2;nose.position.z=2.5;plane.add(nose);plane.position.y=3;scene.add(plane);
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(new Array(9).fill(0),3));const tri=new T.Mesh(geo,L.material(C.teal,{side:T.DoubleSide,transparent:true,opacity:.3}));scene.add(tri);
 const vertices=[L.sphere(.13,C.teal),L.sphere(.13,C.teal),L.sphere(.13,C.orange)];vertices.forEach(v=>scene.add(v));
 const arrows=[L.arrow(C.teal),L.arrow(C.orange),L.arrow(C.blue)];arrows.forEach(a=>scene.add(a));const normal=L.arrow(0xeef1f5);scene.add(normal);
 for(const arrow of [...arrows,normal]){arrow.traverse(o=>{if(o.material){o.material.depthTest=false;o.renderOrder=5;}});}
 const labels=['FORWARD / AB','RIGHT / AC','CROSS PRODUCT'].map((s,i)=>L.label(s,['#55d6c2','#ff8a3d','#8ba4ff'][i]));labels.forEach(l=>scene.add(l));
 let last='';
 start(()=>{
  const isFlight=mode()==='flight';plane.visible=isFlight;tri.visible=!isFlight;normal.visible=!isFlight;vertices.forEach(v=>v.visible=!isFlight);
  let origin,a,b,cross,area;
  if(isFlight){origin=plane.position.clone();plane.quaternion.setFromEuler(new T.Euler(-L.rad(pitch()),L.rad(yaw()),-L.rad(bank()),'YXZ'));a=new T.Vector3(0,0,1).applyQuaternion(plane.quaternion);b=new T.Vector3(1,0,0).applyQuaternion(plane.quaternion);cross=new T.Vector3().crossVectors(a,b);area=cross.length();if(flip())cross.negate();[a,b,cross].forEach((v,i)=>{L.vector(arrows[i],origin,v.clone().multiplyScalar(3.6));labels[i].position.copy(origin).addScaledVector(v,4.25);});L.stat(0,cross.length().toFixed(3));L.stat(1,a.dot(cross).toFixed(3));L.stat(2,'90.0°');L.pill(flip()?'RIGHT × FORWARD = −UP':'FORWARD × RIGHT = UP');
  }else{const A=new T.Vector3(-3,1.5,3),B=new T.Vector3(3,1.5+height(),3),D=new T.Vector3(0,1.5,-3);origin=A;a=B.clone().sub(A);b=D.clone().sub(A);cross=new T.Vector3().crossVectors(a,b);if(flip())cross.negate();area=cross.length()/2;const key=height()+':'+flip();if(key!==last){last=key;geo.attributes.position.array.set([...A.toArray(),...(flip()?D:B).toArray(),...(flip()?B:D).toArray()]);geo.attributes.position.needsUpdate=true;geo.computeVertexNormals();geo.computeBoundingSphere();}[A,B,D].forEach((v,i)=>vertices[i].position.copy(v));L.vector(arrows[0],A,a);L.vector(arrows[1],A,b);L.vector(arrows[2],A,cross.clone().normalize().multiplyScalar(3.6));const center=A.clone().add(B).add(D).divideScalar(3);L.vector(normal,center,cross.clone().normalize().multiplyScalar(2));labels[0].position.copy(B).add(new T.Vector3(0,.5,0));labels[1].position.copy(D).add(new T.Vector3(0,.5,0));labels[2].position.copy(A).addScaledVector(cross.clone().normalize(),4.2);L.stat(0,cross.length().toFixed(2)+' m²');L.stat(1,area.toFixed(2)+' m²');L.stat(2,L.deg(a.angleTo(b)).toFixed(1)+'°');L.pill(flip()?'AC × AB · NORMAL REVERSED':'AB × AC · SURFACE NORMAL');}
  L.$('metric1-label').textContent=isFlight?'Forward · cross':'Triangle area';
  L.$('normal-value').textContent=cross.clone().normalize().toArray().map(n=>n.toFixed(2)).join(', ');
  window.demoState={mode:mode(),cross:cross.toArray(),dot:a.dot(cross),magnitude:cross.length(),area,angle:L.deg(a.angleTo(b))};
 });
})();
