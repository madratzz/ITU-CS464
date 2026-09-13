'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors,M=DemoMath;
  const preset=L.select('preset','Path preset',[['s','S curve'],['arch','Arch'],['loop','Loop']]);
  const selected=L.select('point','Selected control point',[['0','P0 · start'],['1','P1 · first handle'],['2','P2 · second handle'],['3','P3 · end']],'1');
  const cx=L.slider('cx','Selected point X',-8,8,-4,.1),cy=L.slider('cy','Selected point Y',-4,6,5,.1),duration=L.slider('duration','Travel duration',1,8,4,.1,' s'),scrub=L.slider('scrub','Travel progress',0,100,0,1,'%');
  let points=[[-7,-2],[-4,5],[4,-4],[7,2]],table=M.arcTable(points),progress=0,dirty=true,dragIndex=1;
  function sync(){const p=points[+selected()];L.set('cx',p[0]);L.set('cy',p[1]);}
  const run=X.playback(()=>{progress=0;L.set('scrub',0);});
  L.$('point').addEventListener('change',sync);for(const id of ['cx','cy'])L.$(id).addEventListener('input',()=>{points[+selected()]=[cx(),cy()];dirty=true;});
  L.$('preset').addEventListener('change',()=>{points={s:[[-7,-2],[-4,5],[4,-4],[7,2]],arch:[[-7,-2],[-5,6],[5,6],[7,-2]],loop:[[-2,-2],[-8,6],[8,6],[-2,-2]]}[preset()].map(p=>[...p]);sync();dirty=true;progress=0;});
  L.$('scrub').addEventListener('input',()=>{progress=scrub()/100;run.running=false;L.$('play').textContent='Play';});L.hint('Teal = uniform curve parameter. Orange = uniform travelled distance. Drag a handle, or select it above and use the X/Y sliders.');
  const e=L.engine({position:[0,1,25],look:[0,1,0],grid:24}),{scene,start}=e;
  for(const o of scene.children){if(o.isMesh&&o.geometry.type==='PlaneGeometry')o.position.y=-5;if(o.isGridHelper)o.position.y=-4.99;}
  const handles=points.map((p,i)=>{const b=L.sphere(.22,i===0||i===3?C.orange:C.teal);scene.add(b);return b;}),labels=points.map((p,i)=>{const l=L.label('P'+i);l.scale.multiplyScalar(.5);scene.add(l);return l;});
  const curve=L.line([[0,0,0],[1,1,0]],0xb0bece),cage=L.line([[0,0,0],[1,1,0]],0x4e7181,true);scene.add(curve,cage);const movers=[L.sphere(.28,C.teal),L.sphere(.28,C.orange)];scene.add(...movers);
  X.onPlane(e,new T.Plane(new T.Vector3(0,0,1),0),p=>{points[dragIndex]=[L.clamp(p.x,-8,8),L.clamp(p.y,-4,6)];L.$('point').value=dragIndex;sync();dirty=true;},{draggable:true,pick:ray=>{const hit=ray.intersectObjects(handles)[0];if(!hit)return false;dragIndex=handles.indexOf(hit.object);return true;}});X.help('Drag P0–P3 in the scene · Nearby paths are separated slightly in depth for readability');
  start(dt=>{if(dirty){dirty=false;table=M.arcTable(points);const pts=Array.from({length:201},(_,i)=>{const p=M.bezier(points,i/200);return new T.Vector3(p[0],p[1],0);});L.replaceLine(curve,pts);L.replaceLine(cage,points.map(p=>new T.Vector3(p[0],p[1],0)));points.forEach((p,i)=>{handles[i].position.set(p[0],p[1],0);labels[i].position.set(p[0],p[1]+.55,0);});}
    if(run.running){progress=(progress+dt/duration())%1;L.$('scrub').value=progress*100;L.$('scrub-out').textContent=(progress*100).toFixed(0)+'%';}
    const arcT=M.arcParameter(table,progress);[progress,arcT].forEach((t,i)=>{const p=M.bezier(points,t);movers[i].position.set(p[0],p[1],i===0?.32:-.32);});const tangent=M.tangent(points,progress),uniformSpeed=Math.hypot(...tangent)/duration(),constantSpeed=table.total/duration();
    L.stat(0,table.total.toFixed(2)+' m');L.stat(1,uniformSpeed.toFixed(2)+' m/s');L.stat(2,constantSpeed.toFixed(2)+' m/s');L.pill('UNIFORM t = '+progress.toFixed(3)+' · ARC-LENGTH t = '+arcT.toFixed(3));window.demoState={progress,arcT,length:table.total,uniformSpeed,constantSpeed,points:points.map(p=>[...p]),positions:movers.map(m=>m.position.toArray())};
  });
})();
