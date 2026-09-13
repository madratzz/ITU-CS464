const { test }=require('node:test');
const assert=require('node:assert/strict');
const M=require('../06-camera-feel/models.js');
const near=(a,b,e=1e-6)=>assert.ok(Math.abs(a-b)<e,`${a} differs from ${b}`);
test('frictionless elastic reflection conserves speed and reverses normal velocity',()=>{
  for(const theta of [0,.3,1,2]){const n=[Math.sin(theta),Math.cos(theta)],t=[n[1],-n[0]],v=[t[0]*3-n[0]*4,t[1]*3-n[1]*4];const out=M.reflect(v,n,1,0);near(Math.hypot(...out),5);near(out[0]*n[0]+out[1]*n[1],4);}
});
test('slide removes inward normal velocity; outward velocity is untouched',()=>{assert.deepEqual(M.reflect([3,-4],[0,1],1,.5,true),[1.5,0]);assert.deepEqual(M.reflect([3,4],[0,1],1,1),[3,4]);});
test('interception meets a moving target at the requested launch speed under gravity',()=>{
  for(const gravity of [0,9.8,15]){const r=[12,.5],v=[2,0],speed=18,solution=M.intercept(r,v,speed,gravity);assert.ok(solution);near(Math.hypot(...solution.velocity),speed);const t=solution.t;near(solution.velocity[0]*t,r[0]+v[0]*t);near(solution.velocity[1]*t-.5*gravity*t*t,r[1]+v[1]*t);}
});
test('interception reports unreachable receding targets',()=>{assert.equal(M.intercept([10,0],[20,0],5,0),null);assert.equal(M.intercept([100,0],[0,0],5,20),null);});
test('critical spring settles without overshooting a step input',()=>{const s={x:0,v:0},k=45,m=1,c=2*Math.sqrt(k*m);let peak=0;for(let i=0;i<1200;i++){M.spring(s,2,k,c,m,1/240);peak=Math.max(peak,s.x);}assert.ok(peak<=2);near(s.x,2,.001);});
test('an underdamped spring overshoots the target',()=>{const s={x:0,v:0};let peak=0;for(let i=0;i<1000;i++){M.spring(s,2,45,2,1,1/240);peak=Math.max(peak,s.x);}assert.ok(peak>2.5);});
test('Bezier endpoints, derivative and arc-length remapping are consistent',()=>{const p=[[-7,-2],[-4,5],[4,-4],[7,2]],table=M.arcTable(p);assert.deepEqual(M.bezier(p,0),p[0]);assert.deepEqual(M.bezier(p,1),p[3]);near(M.arcParameter(table,0),0);near(M.arcParameter(table,1),1);const speeds=[];for(let i=1;i<50;i++){const a=M.bezier(p,M.arcParameter(table,(i-1)/50)),b=M.bezier(p,M.arcParameter(table,i/50));speeds.push(Math.hypot(a[0]-b[0],a[1]-b[1]));}assert.ok(Math.max(...speeds)/Math.min(...speeds)<1.02);});
test('degenerate Bezier curve remains finite',()=>{const p=Array.from({length:4},()=>[2,3]);const table=M.arcTable(p);near(table.total,0);near(M.arcParameter(table,.5),.5);});
test('IK preserves both segment lengths for reachable and clamped targets',()=>{
  for(const target of [[2,0],[9,-3],[0,4],[.1,3.9],[-3,2]])for(const lengths of [[2.5,2.5],[1,3]])for(const bend of [-1,1]){const root=[0,4],s=M.ik(root,target,...lengths,bend);near(Math.hypot(s.knee[0]-root[0],s.knee[1]-root[1]),lengths[0]);near(Math.hypot(s.foot[0]-s.knee[0],s.foot[1]-s.knee[1]),lengths[1]);assert.ok(Number.isFinite(s.error));}
});
test('IK flags unreachable targets and exactly reaches valid ones',()=>{const s=M.ik([0,4],[2,0],2.5,2.5);near(s.error,0);assert.equal(s.reachable,true);const out=M.ik([0,4],[9,0],2.5,2.5);assert.equal(out.reachable,false);assert.ok(out.error>4);});
