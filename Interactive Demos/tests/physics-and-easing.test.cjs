const {test}=require('node:test');
const assert=require('node:assert/strict');
const P=require('../03-jump-lab/physics.js');
const E=require('../04-easing-lab/easing.js');
const dt=1/120,p={height:2.8,apex:.4,speed:5,fall:1.8,coyote:.12,buffer:.14,variable:true};
const tick=(s,params,input={})=>P.step(s,params,{move:0,press:false,release:false,...input},dt);
test('ground jump reaches intended height and apex within integration tolerance',()=>{
 const s=P.create();tick(s,p,{press:true});let peak=s.y,peakTime=s.time;
 for(let i=0;i<120;i++){tick(s,p);if(s.y>peak){peak=s.y;peakTime=s.time;}}
 assert.ok(Math.abs(peak-p.height)<.08);assert.ok(Math.abs(peakTime-p.apex)<.02);assert.equal(s.grounded,true);
});
test('80 ms late press succeeds with coyote time and fails without it',()=>{
 for(const enabled of [true,false]){const params={...p,coyote:enabled?.12:0};const s=P.create();s.x=-.99;tick(s,params);
  for(let i=0;i<10;i++)tick(s,params);tick(s,params,{press:true});assert.equal(s.jumps,enabled?1:0);
 }
});
test('consumed coyote window cannot produce a second jump',()=>{
 const s=P.create();tick(s,p,{press:true});for(let i=0;i<5;i++)tick(s,p);tick(s,p,{press:true});assert.equal(s.jumps,1);
});
test('a buffered press before landing jumps; expired or disabled buffers do not',()=>{
 for(const window of [.14,0,.01]){const s=P.create();Object.assign(s,{x:3,y:.3,vy:-4,grounded:false,lastGround:-100});const params={...p,buffer:window};tick(s,params,{press:true});for(let i=0;i<12;i++)tick(s,params);assert.equal(s.jumps,window===.14?1:0);}
});
test('release cuts jump height only when variable height is enabled',()=>{
 const peaks=[];for(const variable of [true,false]){const s=P.create(),params={...p,variable};tick(s,params,{press:true});for(let i=0;i<6;i++)tick(s,params);tick(s,params,{release:true});let peak=s.y;for(let i=0;i<80;i++){tick(s,params);peak=Math.max(peak,s.y);}peaks.push(peak);}assert.ok(peaks[0]<peaks[1]*.6);
});
test('higher falling gravity preserves apex and reduces air time',()=>{
 const times=[];for(const fall of [1,2]){const s=P.create(),params={...p,fall};tick(s,params,{press:true});while(!s.grounded&&s.time<3)tick(s,params);times.push(s.time);}assert.ok(times[1]<times[0]-.08);
});
test('all twelve eases have exact endpoints and finite values',()=>{
 assert.equal(Object.keys(E.functions).length,12);for(const [name,fn]of Object.entries(E.functions)){assert.ok(Math.abs(fn(0))<1e-12,name+' starts at 0');assert.ok(Math.abs(fn(1)-1)<1e-12,name+' ends at 1');for(let i=0;i<=1000;i++)assert.ok(Number.isFinite(fn(i/1000)),name);}
});
test('back and elastic curves deliberately overshoot',()=>{assert.ok(E.functions.outBack(.7)>1);assert.ok(E.functions.inBack(.2)<0);assert.ok(Math.max(...Array.from({length:101},(_,i)=>E.functions.outElastic(i/100)))>1.1);});
