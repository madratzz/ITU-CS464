'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const mode=L.select('mode','Use the spring for',[['carriage','A moving carriage'],['recoil','Weapon recoil'],['scale','UI pop / scale']]);
  const stiffness=L.slider('stiffness','Stiffness k',5,150,45,1),damping=L.slider('damping','Damping c',0,60,5,.1),mass=L.slider('mass','Mass',.2,5,1,.1),target=L.slider('target','Target value',-3,3,2,.1);
  let states=[{x:0,v:0},{x:0,v:0},{x:0,v:0}],history=[[],[],[]],time=0;
  const reset=()=>{states=[{x:0,v:0},{x:0,v:0},{x:0,v:0}];history=[[],[],[]];time=0;};
  L.buttons([['step-target','Reverse target',()=>L.set('target',-target()),true],['impulse','Apply impulse',()=>states.forEach(s=>s.v+=5/mass())],['critical','Critical damping',()=>L.set('damping',2*Math.sqrt(stiffness()*mass()))]]);
  const run=X.playback(reset);L.hint('Orange = your damping. Teal = critical damping. Blue = 2× critical damping. All lanes share the same target, mass and stiffness.');
  const {scene,start}=L.engine({position:[11,12,18],look:[0,1,0]});const bodies=[],guides=[];
  for(let i=0;i<3;i++){scene.add(L.box(11,.12,1.7,0x293645,0,.02,(i-1)*3));const b=L.box(.8,.8,.8,[C.orange,C.teal,C.blue][i],0,.5,(i-1)*3);scene.add(b);bodies.push(b);const g=L.line([[0,0,0],[0,1,0]],0x748795,true);scene.add(g);guides.push(g);const label=L.label(['YOUR SPRING','CRITICAL','OVERDAMPED'][i]);label.scale.multiplyScalar(.6);label.position.set(-6,.4,(i-1)*3);scene.add(label);}
  X.help('Reverse the target or apply an impulse · Oscillation is a design parameter');
  const tick=X.fixed(dt=>{time+=dt;const critical=2*Math.sqrt(stiffness()*mass());states.forEach((s,i)=>DemoMath.spring(s,target(),stiffness(),[damping(),critical,2*critical][i],mass(),dt));},240);
  start(dt=>{if(run.running){tick(dt);states.forEach((s,i)=>{history[i].push(s.x);if(history[i].length>360)history[i].shift();});}
    states.forEach((s,i)=>{const b=bodies[i];b.position.x=mode()==='carriage'?s.x:0;b.rotation.x=mode()==='recoil'?s.x*.25:0;b.scale.setScalar(mode()==='scale'?Math.max(.05,1+s.x*.2):1);b.position.y=.1+b.scale.y*.4;L.replaceLine(guides[i],[new T.Vector3(target(),.1,(i-1)*3-.8),new T.Vector3(target(),.1,(i-1)*3+.8)]);guides[i].visible=mode()==='carriage';});
    const ratio=damping()/(2*Math.sqrt(stiffness()*mass()));L.stat(0,ratio.toFixed(2));L.stat(1,(target()-states[0].x).toFixed(3));L.stat(2,states[0].v.toFixed(3));L.pill(ratio<.99?'UNDERDAMPED · OSCILLATORY':ratio>1.01?'OVERDAMPED · SLOW RETURN':'CRITICALLY DAMPED');X.graph(history,['#ff8a3d','#55d6c2','#6c8cff'],-5,5,'SPRING POSITION / RECENT RENDER SAMPLES');window.demoState={ratio,time,states:states.map(s=>({...s})),target:target()};
  });
})();
