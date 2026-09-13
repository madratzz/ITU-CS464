'use strict';
(() => {
 const L=Lab,T=THREE,C=L.colors,E=Easing;
 const ease=L.select('ease','Selected easing curve',Object.entries(E.names),'outBack');
 const mode=L.select('mode','Animate property',[['position','Position · a 10 metre race'],['scale','Scale · a pop-in'],['rotation','Rotation · a full turn']]);
 const duration=L.slider('duration','Duration',.4,4,2,.1,' s');const rate=L.slider('rate','Playback rate',.1,2,1,.1,'×');
 const scrub=L.slider('scrub','Scrub time',0,100,0,1,'%');
 const loop=L.check('loop','Repeat animation',true);const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;let playing=!reduced,elapsed=0,t=0;
 L.buttons([['play',playing?'Pause':'Play',()=>{playing=!playing;L.$('play').textContent=playing?'Pause':'Play';},true],['replay','Replay',()=>{elapsed=0;t=0;playing=true;L.$('play').textContent='Pause';}]]);
 L.buttons([['reset','Reset lab',()=>{L.set('ease','outBack');L.set('mode','position');L.set('duration',2);L.set('rate',1);L.set('scrub',0);L.$('loop').checked=true;elapsed=0;t=0;playing=false;L.$('play').textContent='Play';}]]);
 L.$('scrub').addEventListener('input',()=>{t=scrub()/100;elapsed=t*duration();playing=false;L.$('play').textContent='Play';});
 L.hint('<b>Same endpoints. Same duration.</b> Only the mapping from time to progress changes.<br>Scrub slowly to inspect overshoot and bounce. Switch the property to see the same curve reused.');
 const {scene,start}=L.engine({position:[12,14,18],look:[0,0,0],grid:22});
 const laneNames=['SELECTED','LINEAR','CUBIC IN/OUT','BOUNCE OUT'],laneColors=[C.orange,C.teal,C.blue,C.pink],bodies=[];
 for(let i=0;i<4;i++){const z=-4.5+i*3;scene.add(L.box(12,.08,1.8,0x242e3a,0,0,z));scene.add(L.line([[-5,.065,z],[5,.065,z]],0x546477,true));for(const x of [-5,5])scene.add(L.box(.04,.03,1.8,0x7e8999,x,.08,z));const b=L.box(.65,.65,.65,laneColors[i],-5,.4,z);scene.add(b);bodies.push(b);const label=L.label(laneNames[i],['#ff8a3d','#55d6c2','#8ba4ff','#ff74b8'][i]);label.scale.multiplyScalar(.75);label.position.set(-7,.15,z);scene.add(label);}
 const startLabel=L.label('START'),endLabel=L.label('FINISH');startLabel.position.set(-5,.1,-6.2);endLabel.position.set(5,.1,-6.2);scene.add(startLabel,endLabel);
 const canvas=L.$('graph'),ctx=canvas.getContext('2d');canvas.setAttribute('aria-label','Easing curve: horizontal axis normalized time, vertical axis normalized progress');
 function drawGraph(fn){const w=canvas.clientWidth,h=115;canvas.width=w*devicePixelRatio;canvas.height=h*devicePixelRatio;ctx.scale(devicePixelRatio,devicePixelRatio);const x=t=>32+t*(w-48),y=v=>91-v*58;ctx.clearRect(0,0,w,h);ctx.strokeStyle='#344150';for(const val of [0,.5,1]){ctx.beginPath();ctx.moveTo(x(0),y(val));ctx.lineTo(x(1),y(val));ctx.stroke();ctx.fillStyle='#9aa2b1';ctx.font='9px monospace';ctx.fillText(val.toFixed(1),5,y(val)+3);}ctx.strokeStyle='#55d6c2';ctx.setLineDash([3,5]);ctx.beginPath();ctx.moveTo(x(0),y(0));ctx.lineTo(x(1),y(1));ctx.stroke();ctx.setLineDash([]);ctx.strokeStyle='#ff8a3d';ctx.lineWidth=2;ctx.beginPath();for(let i=0;i<=200;i++){const u=i/200;if(i)ctx.lineTo(x(u),y(fn(u)));else ctx.moveTo(x(u),y(fn(u)));}ctx.stroke();ctx.fillStyle='#eef1f5';ctx.beginPath();ctx.arc(x(t),y(fn(t)),4,0,Math.PI*2);ctx.fill();ctx.fillStyle='#9aa2b1';ctx.font='9px monospace';ctx.fillText('TIME 0 → 1',w-90,109);ctx.fillText('PROGRESS',34,12);}
 start(dt=>{if(playing){elapsed+=dt*rate();t=Math.min(1,elapsed/duration());if(elapsed>duration()+.7){if(loop()){elapsed=0;t=0;}else{playing=false;L.$('play').textContent='Play';}}L.$('scrub').value=t*100;L.$('scrub-out').textContent=(t*100).toFixed(0)+'%';}
  const fn=E.functions[ease()],fns=[fn,E.functions.linear,E.functions.inOutCubic,E.functions.outBounce];bodies.forEach((b,i)=>{const v=fns[i](t);b.position.x=mode()==='position'?-5+10*v:0;b.scale.setScalar(mode()==='scale'?Math.max(.02,.1+v*1.5):1);b.rotation.y=mode()==='rotation'?Math.PI*2*v:0;b.position.y=b.scale.y*.325+.08;});
  const v=fn(t),a=Math.max(0,t-.0001),b=Math.min(1,t+.0001),speed=(fn(b)-fn(a))/(b-a)/duration();L.stat(0,t.toFixed(3));L.stat(1,v.toFixed(3));L.stat(2,speed.toFixed(2)+' /s');L.pill(E.names[ease()].toUpperCase()+(v>1?' · OVERSHOOT':v<0?' · ANTICIPATION':''));drawGraph(fn);window.demoState={t,value:v,ease:ease(),mode:mode(),playing,positions:bodies.map(b=>b.position.x)};
 });
})();
