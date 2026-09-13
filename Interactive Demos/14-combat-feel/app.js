'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const preset=L.select('preset','Attack preset',[['nimble','Nimble'],['heavy','Heavy']]);
  const startup=L.slider('startup','Anticipation / startup',.04,.6,.12,.01,' s'),active=L.slider('active','Active window',.05,.4,.15,.01,' s'),recovery=L.slider('recovery','Recovery',.05,.9,.25,.01,' s');
  const buffer=L.slider('buffer','Input buffer',0,250,120,10,' ms'),knock=L.slider('knock','Knockback impulse',0,8,3,.1),stop=L.slider('stop','Hit stop',0,150,45,5,' ms'),distance=L.slider('distance','Dummy distance',2,7,3.5,.1,' m');
  let time=0,phase='ready',age=0,until=-1,freeze=0,hits=0,attacks=0,hitThis=false,offset=0,dummyV=0,combo=false,comboPressed=false,lastInput='READY',durations=null;
  const reset=()=>{time=0;phase='ready';age=0;until=-1;freeze=0;hits=0;attacks=0;hitThis=false;offset=0;dummyV=0;combo=false;comboPressed=false;};
  function begin(){durations={startup:startup(),active:active(),recovery:recovery()};phase='startup';age=0;hitThis=false;until=-1;attacks++;}
  function attack(){if(phase==='ready'){begin();lastInput='ATTACK STARTED';}else if(buffer()>0){until=time+buffer()/1000;lastInput='INPUT BUFFERED';}else lastInput='INPUT IGNORED · BUSY';}
  L.buttons([['attack','Attack',()=>{attack();run.running=true;L.$('play').textContent='Pause';},true],['combo','Combo trial',()=>{reset();combo=true;attack();run.running=true;L.$('play').textContent='Pause';}]]);
  const run=X.playback(reset);L.hint('Space attacks when a form control is not focused. The combo trial presses again 60 ms before recovery ends. Set buffering to zero and compare.');
  L.$('preset').addEventListener('change',()=>{const p=preset()==='heavy'?[.35,.2,.65,150,6,85]:[.12,.15,.25,120,3,45];['startup','active','recovery','buffer','knock','stop'].forEach((id,i)=>L.set(id,p[i]));reset();});
  document.addEventListener('keydown',e=>{if(e.code==='Space'&&!e.repeat&&!/INPUT|SELECT|BUTTON/.test(e.target.tagName)){e.preventDefault();attack();}});
  const {scene,start}=L.engine({position:[9,13,18],look:[0,.7,0]}),fighter=L.box(.9,1.5,.9,C.teal,-4,.75,0),dummy=L.box(1,1.7,1,C.orange,0,.85,0);scene.add(fighter,dummy);
  const pivot=new T.Group();pivot.position.set(-4,1,0);const sword=L.box(3.8,.16,.18,0xd5e6f0,1.9,0,0);pivot.add(sword);scene.add(pivot);const ring=new T.Mesh(new T.RingGeometry(3.8,4,64),new T.MeshBasicMaterial({color:C.orange,side:T.DoubleSide,transparent:true,opacity:.12}));ring.rotation.x=-Math.PI/2;ring.position.set(-4,.03,0);scene.add(ring);
  X.help('Blue anticipation → orange active hit window → teal recovery · One hit per swing');
  const tick=X.fixed(dt=>{time+=dt;offset+=dummyV*dt;dummyV*=Math.exp(-5*dt);offset*=Math.exp(-dt*.8);if(freeze>0){freeze-=dt;return;}if(phase==='ready')return;age+=dt;
    if(combo&&!comboPressed&&attacks===1&&phase==='recovery'&&durations.recovery-age<=.06){attack();comboPressed=true;}
    if(phase==='active'&&!hitThis&&Math.abs(age/durations.active-.5)<.2&&distance()+offset<=4){hits++;hitThis=true;dummyV=knock();freeze=stop()/1000;}
    const length=durations[phase];if(age>=length){age-=length;if(phase==='startup')phase='active';else if(phase==='active')phase='recovery';else{phase='ready';age=0;if(until>=time)begin();}}
  });
  start(dt=>{if(run.running)tick(dt);let angle=-1.3;const p=durations?L.clamp(age/durations[phase],0,1):0;if(phase==='startup')angle=-.3-p;else if(phase==='active')angle=-1.3+p*2.6;else if(phase==='recovery')angle=1.3*(1-p)-.3*p;else angle=-.3;pivot.rotation.y=angle;fighter.scale.y=phase==='startup'?1-.15*p:1;fighter.position.y=.75*fighter.scale.y;dummy.position.x=-4+distance()+offset;dummy.material.emissive.setHex(freeze>0?0x6b2a0b:0);ring.material.opacity=phase==='active'?.25:.04;
    L.stat(0,freeze>0?'Hit stop':phase);L.stat(1,hits);L.stat(2,Math.max(0,(until-time)*1000).toFixed(0)+' ms');L.pill(lastInput+' · '+attacks+' ATTACKS');
    const total=startup()+active()+recovery(),values=Array.from({length:121},(_,i)=>{const t=i/120*total;return t<startup()?1:t<startup()+active()?2:.5;});X.graph([values],['#ff8a3d'],0,2.5,'ATTACK TIMELINE: STARTUP → ACTIVE → RECOVERY');window.demoState={phase,time,age,hits,attacks,bufferRemaining:Math.max(0,until-time),freeze,distance:distance()+offset,lastInput};
  });
})();
