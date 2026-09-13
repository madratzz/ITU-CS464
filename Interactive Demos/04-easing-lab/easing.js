(function(root){
 const bounce=t=>{const n=7.5625,d=2.75;if(t<1/d)return n*t*t;if(t<2/d)return n*(t-=1.5/d)*t+.75;if(t<2.5/d)return n*(t-=2.25/d)*t+.9375;return n*(t-=2.625/d)*t+.984375;};
 const functions={linear:t=>t,inQuad:t=>t*t,outQuad:t=>1-(1-t)**2,inOutCubic:t=>t<.5?4*t*t*t:1-(-2*t+2)**3/2,smoothstep:t=>t*t*(3-2*t),inExpo:t=>t===0?0:2**(10*t-10),outExpo:t=>t===1?1:1-2**(-10*t),inBack:t=>2.70158*t*t*t-1.70158*t*t,outBack:t=>1+2.70158*(t-1)**3+1.70158*(t-1)**2,outElastic:t=>t===0||t===1?t:2**(-10*t)*Math.sin((t*10-.75)*2*Math.PI/3)+1,outBounce:bounce,inOutSine:t=>-(Math.cos(Math.PI*t)-1)/2};
 const names={linear:'Linear',inQuad:'Quad · ease in',outQuad:'Quad · ease out',inOutCubic:'Cubic · ease in/out',smoothstep:'Smoothstep',inExpo:'Expo · ease in',outExpo:'Expo · ease out',inBack:'Back · ease in',outBack:'Back · ease out',outElastic:'Elastic · ease out',outBounce:'Bounce · ease out',inOutSine:'Sine · ease in/out'};
 const api={functions,names};if(typeof module!=='undefined')module.exports=api;else root.Easing=api;
})(typeof window!=='undefined'?window:globalThis);
