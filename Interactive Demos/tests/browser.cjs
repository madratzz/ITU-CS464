/* Optional browser regression suite. Requires Playwright; production demos do not. */
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const os=require('node:os');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..'),out=process.env.DEMO_SCREENSHOTS||path.join(os.tmpdir(),'cs464-demo-screenshots');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const context=await browser.newContext({viewport:{width:1440,height:1050},offline:true});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 const open=async folder=>{await page.goto(pathToFileURL(path.join(root,folder,'index.html')).href);if(folder)await page.waitForFunction(()=>window.demoState);};
 const value=async(id,v)=>{await page.locator('#'+id).evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},String(v));await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));};
 const flush=()=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
 const click=async selector=>{await page.click(selector);await flush();};
 const check=async selector=>{await page.check(selector);await flush();};
 const state=()=>page.evaluate(()=>window.demoState);
 try{
  await open('01-dot-product');await value('angle',0);assert.equal((await state()).visible,true);await value('angle',90);assert.ok(Math.abs((await state()).dot)<1e-8);await click('#behind');assert.ok((await state()).dot<-.999);await click('#front');await check('#occlusion');await page.waitForFunction(()=>demoState.hidden);assert.equal((await state()).visible,false);await page.uncheck('#occlusion');await value('distance',12);assert.equal((await state()).inRange,false);await click('#reset');
  await page.screenshot({path:path.join(out,'01-dot-product.png'),fullPage:true});
  await open('02-cross-product');assert.ok(Math.abs((await state()).dot)<1e-8);const before=(await state()).cross;await check('#flip');await page.waitForTimeout(70);(await state()).cross.forEach((v,i)=>assert.ok(Math.abs(v+before[i])<1e-8));await value('mode','normal');await value('height',0);assert.ok(Math.abs((await state()).area-18)<1e-8);await value('height',5);assert.ok(Math.abs((await state()).dot)<1e-8);await page.screenshot({path:path.join(out,'02-cross-product-normal.png'),fullPage:true});
  await open('03-jump-lab');await click('#coyote-trial');await page.waitForFunction(()=>demoState.jumps===1);await page.waitForFunction(()=>demoState.grounded&&demoState.x>1.5);await value('coyote',0);await click('#coyote-trial');await page.waitForTimeout(450);assert.equal((await state()).jumps,0);await click('#buffer-trial');await page.waitForFunction(()=>demoState.jumps===1);await value('buffer',0);await click('#buffer-trial');await page.waitForTimeout(600);assert.equal((await state()).jumps,0);await click('#reset');await click('#pause');const time=(await state()).time;await page.waitForTimeout(100);assert.equal((await state()).time,time);await click('#step');assert.ok((await state()).time>time);await click('#pause');await page.locator('h1').click();await page.keyboard.down('Space');await page.waitForFunction(()=>demoState.jumps===1);await page.keyboard.up('Space');await page.screenshot({path:path.join(out,'03-jump-lab.png'),fullPage:true});
  await open('04-easing-lab');await value('scrub',70);assert.ok((await state()).value>1);assert.equal((await state()).playing,false);for(const curve of ['linear','inQuad','outQuad','inOutCubic','smoothstep','inExpo','outExpo','inBack','outBack','outElastic','outBounce','inOutSine']){await value('ease',curve);await value('scrub',100);assert.ok(Math.abs((await state()).value-1)<1e-8);}await value('mode','rotation');await value('scrub',50);await page.screenshot({path:path.join(out,'04-easing-lab.png'),fullPage:true});
  await open('05-game-juice');await click('#hit');await page.waitForFunction(()=>demoState.activeParticles>0);assert.deepEqual((await state()).baselineScale,[1,1,1]);await page.screenshot({path:path.join(out,'05-game-juice.png'),fullPage:true});await value('preset','bare');await click('#hit');await page.waitForTimeout(500);assert.equal((await state()).activeParticles,0);assert.deepEqual((await state()).juiceScale,[1,1,1]);
  for(const width of [390,768,1440]){await page.setViewportSize({width,height:900});for(const folder of ['', '01-dot-product','02-cross-product','03-jump-lab','04-easing-lab','05-game-juice']){await open(folder);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${folder} overflows at ${width}px`);if(width===390)await page.screenshot({path:path.join(out,(folder||'catalog')+'-mobile.png'),fullPage:true});}}
  // Verify a copied demo runs with no parent/sibling files present.
  const isolated=fs.mkdtempSync(path.join(os.tmpdir(),'cs464-isolated-'));fs.cpSync(path.join(root,'01-dot-product'),isolated,{recursive:true});await page.goto(pathToFileURL(path.join(isolated,'index.html')).href);await page.waitForFunction(()=>window.demoState?.visible===true);
  await context.close();const reduced=await browser.newContext({reducedMotion:'reduce',offline:true});const rp=await reduced.newPage();await rp.goto(pathToFileURL(path.join(root,'04-easing-lab/index.html')).href);await rp.waitForFunction(()=>window.demoState);assert.equal(await rp.evaluate(()=>demoState.playing),false);
  assert.deepEqual(errors,[]);console.log('PASS: vector maths, occlusion, normals, jump trials, keyboard controls, pause/step, 12 eases, impact comparison, 3 viewport sizes, offline copied folder, reduced motion; no browser errors.');console.log('Screenshots:',out);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
