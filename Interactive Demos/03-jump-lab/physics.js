/* Pure, fixed-step jump simulation; also used by the regression tests. Feet are y=0 on a platform. */
(function(root){
 const platforms=[[-9,-1],[1.5,9]];
 function create(){return{x:-6,y:0,vy:0,time:0,grounded:true,lastGround:0,bufferUntil:-Infinity,consumed:false,event:'Ready',jumps:0};}
 function step(s,p,input,dt){
  s.time+=dt;s.x+=input.move*p.speed*dt;s.x=Math.max(-10,Math.min(10,s.x));
  const support=platforms.some(([a,b])=>s.x>=a&&s.x<=b);
  if(s.grounded&&!support){s.grounded=false;s.lastGround=s.time;s.event='Left the ledge';}
  if(s.grounded){s.lastGround=s.time;s.consumed=false;}
  if(input.press)s.bufferUntil=s.time+p.buffer;
  const jump=()=>{s.vy=2*p.height/p.apex;s.grounded=false;s.consumed=true;s.bufferUntil=-Infinity;s.jumps++;};
  const canCoyote=!s.consumed&&p.coyote>0&&s.time-s.lastGround<=p.coyote;
  if(s.bufferUntil>=s.time&&(s.grounded||canCoyote)){s.event=s.grounded?'Ground jump':'Coyote jump';jump();}
  else if(input.press)s.event=p.buffer>0?'Jump buffered':'Jump missed';
  if(input.release&&p.variable&&s.vy>0){s.vy*=.45;s.event='Jump cut on release';}
  const oldY=s.y,g=2*p.height/(p.apex*p.apex);
  if(!s.grounded){s.vy-=g*(s.vy<0?p.fall:1)*dt;s.y+=s.vy*dt;
   if(s.vy<=0&&oldY>=0&&s.y<=0&&support){s.y=0;s.vy=0;s.grounded=true;s.consumed=false;s.lastGround=s.time;s.event='Landed';if(s.bufferUntil>=s.time){jump();s.event='Buffered landing jump';}}
  }
  return s;
 }
 const api={create,step,platforms};if(typeof module!=='undefined')module.exports=api;else root.JumpPhysics=api;
})(typeof window!=='undefined'?window:globalThis);
