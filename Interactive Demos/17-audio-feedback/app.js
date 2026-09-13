'use strict';
(() => {
  const L=Lab,X=Extra,T=THREE,C=L.colors;
  const preset=L.select('preset','Sound family',[['pickup','Pickup'],['impact','Impact'],['step','Footstep']]);
  const pitch=L.slider('pitch','Base frequency',60,1200,440,1,' Hz'),variation=L.slider('variation','Pitch variation',0,12,2,.1,' semitones'),attack=L.slider('attack','Envelope attack',.002,.2,.01,.001,' s'),decay=L.slider('decay','Envelope decay',.04,.8,.22,.01,' s'),volume=L.slider('volume','Master volume',0,.5,.15,.01),delay=L.slider('delay','Designed feedback delay',0,300,0,10,' ms');
  const tonal=L.check('tonal','Tonal layer',true),noise=L.check('noise','Noise layer',false);
  let audio=null,master=null,analyser=null,sources=[],events=[],count=0,lastPitch=440,audioStatus='SILENT · PRESS A SOUND BUTTON',seed=17;
  const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
  async function init(){try{audio??=new(window.AudioContext||window.webkitAudioContext)();if(!master){master=audio.createGain();analyser=audio.createAnalyser();analyser.fftSize=256;master.connect(analyser);analyser.connect(audio.destination);}await audio.resume();master.gain.value=volume();audioStatus=audio.state==='running'?'AUDIO READY':'AUDIO SUSPENDED';return audio.state==='running';}catch(e){audioStatus='AUDIO UNAVAILABLE · '+e.message;return false;}}
  function voice(designed,baseTime){const now=baseTime,wait=designed?delay()/1000:0,when=now+wait,d=designed?decay():.15,a=designed?attack():.004,frequency=designed?pitch()*2**(((rand()*2-1)*variation())/12):220;
    if(designed)lastPitch=frequency;count++;events.push({designed,start:now,sound:when,duration:a+d});
    const makeEnvelope=level=>{const g=audio.createGain();g.gain.setValueAtTime(.0001,when);g.gain.linearRampToValueAtTime(level,when+a);g.gain.exponentialRampToValueAtTime(.0001,when+a+d);g.connect(master);return g;};
    function keep(source,g){sources.push(source);source.onended=()=>{source.disconnect();g.disconnect();sources=sources.filter(s=>s!==source);};source.start(when);source.stop(when+a+d+.03);}
    if(!designed||tonal()){const oscillator=audio.createOscillator();oscillator.type=designed&&preset()==='impact'?'triangle':'sine';oscillator.frequency.setValueAtTime(frequency,when);oscillator.frequency.exponentialRampToValueAtTime(designed?(preset()==='pickup'?frequency*1.6:frequency*.35):frequency,when+a+d);const env=makeEnvelope(.65);oscillator.connect(env);keep(oscillator,env);}
    if(designed&&noise()){const length=Math.ceil(audio.sampleRate*(a+d+.04)),buffer=audio.createBuffer(1,length,audio.sampleRate),samples=buffer.getChannelData(0);for(let i=0;i<length;i++)samples[i]=rand()*2-1;const src=audio.createBufferSource();src.buffer=buffer;const filter=audio.createBiquadFilter();filter.type='lowpass';filter.frequency.value=preset()==='step'?700:2500;const env=makeEnvelope(.4);src.connect(filter);filter.connect(env);keep(src,env);}
    audioStatus=designed?'DESIGNED SOUND SCHEDULED':'BASELINE TONE SCHEDULED';
  }
  async function play(which){if(!await init())return;const now=audio.currentTime+.025;if(which==='compare'){voice(false,now);voice(true,now+1.4);}else voice(which==='designed',now);}
  function reset(){for(const s of [...sources])try{s.stop();}catch{}events=[];count=0;seed=17;L.set('preset','pickup');applyPreset();L.set('volume',.15);L.set('delay',0);audioStatus='RESET · PRESS A SOUND BUTTON';}
  function applyPreset(){const p={pickup:[440,.01,.22,true,false],impact:[110,.004,.28,true,true],step:[90,.004,.12,false,true]}[preset()];L.set('pitch',p[0]);L.set('attack',p[1]);L.set('decay',p[2]);L.$('tonal').checked=p[3];L.$('noise').checked=p[4];}
  L.$('preset').addEventListener('change',applyPreset);L.$('volume').addEventListener('input',()=>{if(master)master.gain.value=volume();});
  L.buttons([['baseline','Play baseline',()=>play('baseline')],['designed','Play designed',()=>play('designed'),true]]);L.buttons([['compare','Compare A → B',()=>play('compare')],['reset','Reset / stop',reset]]);
  L.hint('No automatic playback. Start at a comfortable volume. Left = plain tone; right = designed sound. A visual pulse marks the input; the rising bars show actual synthesized audio.');
  const {scene,start}=L.engine({position:[9,10,19],look:[0,1,0]}),cubes=[],bars=[];
  for(let i=0;i<2;i++){const b=L.box(1.6,1.6,1.6,i?C.orange:0x8c99ad,i?4:-4,.8,0);scene.add(b);cubes.push(b);const l=L.label(i?'B / DESIGNED':'A / BASELINE');l.position.set(i?4:-4,.2,2.5);scene.add(l);}
  for(let i=0;i<24;i++){const b=L.box(.24,1,.3,i%2?C.teal:C.blue,-5.5+i*.48,.1,-3);scene.add(b);bars.push(b);}X.help('Play A, B, or a timed comparison · Reset cancels pending sounds');
  const bins=new Uint8Array(128);
  start(()=>{const now=audio?.currentTime||0;if(analyser)analyser.getByteFrequencyData(bins);bars.forEach((b,i)=>{b.scale.y=.05+bins[i*3]/255*3;b.position.y=b.scale.y*.5;});cubes.forEach((b,i)=>{const event=events.filter(e=>e.designed===!!i&&e.start<=now).at(-1);const age=event?now-event.start:100,pulse=Math.exp(-age*9)*Math.sin(age*20);b.scale.setScalar(1+pulse*.22);b.position.y=.8*b.scale.y;b.material.emissive.setHex(event&&now>=event.sound&&now<event.sound+.08?0x4c2610:0);});events=events.filter(e=>now-e.start<3);
    const values=Array.from({length:120},(_,i)=>{const t=i/119*(attack()+decay());return t<attack()?t/attack():Math.exp(-9.21*(t-attack())/decay());});X.graph([values],['#ff8a3d'],0,1,'DESIGNED ENVELOPE / ATTACK → DECAY (NORMALIZED)');L.stat(0,audio?audio.state:'Not started');L.stat(1,lastPitch.toFixed(0)+' Hz');L.stat(2,delay()+' ms');L.pill(audioStatus);window.demoState={audioState:audio?.state||'not-started',count,lastPitch,pendingSources:sources.length,events:events.map(e=>({...e})),delay:delay(),tonal:tonal(),noise:noise()};
  });
})();
