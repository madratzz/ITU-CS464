'use strict';
(() => {
  const L=Lab, X=Extra, T=THREE;
  const mode=L.select('mode','Camera behaviour',[['rigid','Rigid follow'],['smooth','Exponential smoothing'],['spring','Damped spring'],['dead','Dead zone']],'smooth');
  const response=L.slider('response','Response',.5,10,3,.1), ahead=L.slider('ahead','Look-ahead time',0,1.5,.4,.1,' s');
  const zone=L.slider('zone','Dead-zone half-width',.2,4,1.5,.1,' m');
  const zoom=L.check('zoom','Zoom out with speed',false), motion=L.check('motion','Move the subject automatically',true);
  const position=L.slider('position','Subject X (manual)',-8,8,0,.1,' m');
  let time=0, follower=0, velocity=0, speed=0, subject=0, previous=0, initialized=false;
  const reset=()=>{time=0;follower=0;velocity=0;subject=0;previous=0;initialized=false;L.set('position',0);};
  const run=X.playback(reset); L.hint('Teal marks the camera’s framing point. Try an abrupt position change with automatic movement off. Reset preserves your tuning.');
  const engine=L.engine({position:[0,6,18],look:[0,1,0],grid:60}), {scene,camera,start}=engine;
  const actor=L.box(.8,1.4,.8,L.colors.orange,0,.7,0);scene.add(actor);
  for(let i=-20;i<=20;i+=4){scene.add(L.box(.35,2,.35,0x43526a,i,1,-3));const label=L.label(String(i)+' m','#9aa2b1');label.scale.multiplyScalar(.5);label.position.set(i,2.5,-3);scene.add(label);}
  const focus=L.sphere(.16,L.colors.teal,0,.1,0);scene.add(focus);
  const zoneLine=L.line([[0,0,0],[1,0,0]],L.colors.teal,true);scene.add(zoneLine);
  X.help('Camera follows along X · Compare response during reversals and stops');
  start(dt=>{
    if(run.running){time+=dt;subject=motion()?Math.sin(time*.85)*7:position();speed=initialized&&dt>0?(subject-previous)/dt:0;initialized=true;previous=subject;
      const goal=subject+L.clamp(speed*ahead(),-4,4);
      if(mode()==='rigid'){follower=goal;velocity=0;}
      else if(mode()==='smooth'){follower+=(goal-follower)*(1-Math.exp(-response()*dt));velocity=0;}
      else if(mode()==='dead'){const error=goal-follower;follower+=Math.sign(error)*Math.max(0,Math.abs(error)-zone());velocity=0;}
      else{let remaining=dt;while(remaining>0){const h=Math.min(remaining,1/240),s={x:follower,v:velocity};DemoMath.spring(s,goal,response()*12,2*Math.sqrt(response()*12)*.7,1,h);follower=s.x;velocity=s.v;remaining-=h;}}
    }
    actor.position.x=subject;focus.position.x=follower;camera.position.set(follower,6,18);camera.lookAt(follower,1,0);
    const desiredFov=43+(zoom()?Math.min(Math.abs(speed)*1.5,15):0);camera.fov+=(desiredFov-camera.fov)*(1-Math.exp(-5*dt));camera.updateProjectionMatrix();
    zoneLine.visible=mode()==='dead';L.replaceLine(zoneLine,[[-zone(),.05,-1],[zone(),.05,-1],[zone(),.05,1],[-zone(),.05,1],[-zone(),.05,-1]].map(v=>new T.Vector3(v[0]+follower,v[1],v[2])));
    L.stat(0,(subject-follower).toFixed(2)+' m');L.stat(1,Math.abs(speed).toFixed(2)+' m/s');L.stat(2,camera.fov.toFixed(1)+'°');L.pill((run.running?'LIVE · ':'PAUSED · ')+mode().toUpperCase());
    window.demoState={mode:mode(),subject,follower,error:subject-follower,speed,fov:camera.fov,running:run.running};
  });
})();
