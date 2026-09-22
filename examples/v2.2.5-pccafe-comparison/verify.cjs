const {chromium}=require('../../plugins/genscaff/skills/genscaff-release-audit/scripts/node_modules/playwright');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const base=process.env.PCCAFE_URL||'http://127.0.0.1:8835';
const artifacts=path.join(__dirname,'artifacts');
const config={
  standard:{seat:s=>`input[name="seat"][value="${s}"]`,hour:h=>`input[name="duration"][value="${h}"]`,total:'#total-price',confirm:'.plan-submit',result:'#plan-confirmation',resultPrice:'#confirmed-price',edit:'#edit-plan',hero:'.hero .button-primary'},
  control:{seat:s=>`[data-seat="${s}"]`,hour:h=>`[data-hours="${h}"]`,total:'[data-total-price]',confirm:'.confirm-plan',result:'.plan-modal',resultPrice:'[data-modal-total]',edit:'.modal-edit',hero:'.hero .button-primary'}
};
async function style(el){return el.evaluate(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return {background:s.backgroundColor,color:s.color,transform:s.transform,outline:s.outlineStyle,outlineWidth:s.outlineWidth,transition:s.transitionDuration,width:r.width,height:r.height};});}
async function tabTo(page,selector){for(let i=0;i<60;i++){if(await page.locator(selector).evaluate(e=>e===document.activeElement))return;await page.keyboard.press('Tab');}throw Error(`Keyboard target unreachable: ${selector}`);}
(async()=>{
 fs.mkdirSync(artifacts,{recursive:true});const browser=await chromium.launch({headless:true});const records=[];
 try{for(const arm of Object.keys(config).filter(a=>!process.env.PCCAFE_ARM||a===process.env.PCCAFE_ARM)){const c=config[arm];for(const [device,width,height,touch] of [['desktop',1440,1000,false],['mobile',390,844,true]]){
  const context=await browser.newContext({viewport:{width,height},hasTouch:touch,isMobile:touch,deviceScaleFactor:1});const page=await context.newPage();const errors=[];const row={arm,device,viewport:{width,height},touchEmulation:touch,errors,checks:{}};records.push(row);
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.goto(`${base}/${arm}/`,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
  await page.screenshot({path:path.join(artifacts,`${arm}-${device}.png`)});await page.screenshot({path:path.join(artifacts,`${arm}-${device}-full.png`),fullPage:true});
  row.checks.images=await page.locator('img').evaluateAll(es=>es.length>0&&es.every(e=>e.complete&&e.naturalWidth>0));
  row.checks.noOverflow=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth);
  assert(row.checks.images,'image load');assert(row.checks.noOverflow,`${arm} ${device} overflow`);
  row.checks.calculations=[];
  for(const [seat,price] of Object.entries({standard:2000,wide:2500,duo:5000})){for(const h of [1,2,3]){
   const seatTarget=page.locator(c.seat(seat)),hourTarget=page.locator(c.hour(h));await (arm==='standard'?seatTarget.locator('..'):seatTarget).click();await (arm==='standard'?hourTarget.locator('..'):hourTarget).click();assert.equal((await page.locator(c.total).innerText()).replace(/\D/g,''),String(price*h));row.checks.calculations.push({seat,h,total:price*h});
  }}
  await page.locator(c.confirm).click();assert(await page.locator(c.result).isVisible());assert.equal((await page.locator(c.resultPrice).innerText()).replace(/\D/g,''),'15000');
  await page.screenshot({path:path.join(artifacts,`${arm}-${device}-confirmation.png`)});await page.locator(c.edit).click();assert(!(await page.locator(c.result).isVisible()));row.checks.confirmEdit=true;
  await page.goto(`${base}/${arm}/`,{waitUntil:'networkidle'});await tabTo(page,c.seat('standard'));await page.keyboard.press('ArrowRight');assert.equal((await page.locator(c.total).innerText()).replace(/\D/g,''),'2500');
  await tabTo(page,c.hour(1));await page.keyboard.press('ArrowRight');assert.equal((await page.locator(c.total).innerText()).replace(/\D/g,''),'5000');
  await tabTo(page,c.confirm);row.focus=await style(page.locator(c.confirm));row.checks.focusUnobscured=await page.locator(c.confirm).evaluate(e=>{const r=e.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return e===hit||e.contains(hit);});await page.screenshot({path:path.join(artifacts,`${arm}-${device}-focus.png`)});await page.keyboard.press('Enter');assert(await page.locator(c.result).isVisible());await tabTo(page,c.edit);await page.keyboard.press('Enter');assert(!(await page.locator(c.result).isVisible()));row.checks.keyboard=true;
  await page.goto(`${base}/${arm}/`,{waitUntil:'networkidle'});
  if(!touch){const target=page.locator(c.hero);row.pointer={normal:await style(target)};await target.hover();await page.waitForTimeout(400);row.pointer.hover=await style(target);await page.screenshot({path:path.join(artifacts,`${arm}-desktop-hover.png`)});await page.mouse.move(0,0);await page.waitForTimeout(400);row.pointer.out=await style(target);row.checks.hoverFeedback=row.pointer.normal.background!==row.pointer.hover.background||row.pointer.normal.color!==row.pointer.hover.color||row.pointer.normal.transform!==row.pointer.hover.transform;row.checks.pointerRestored=JSON.stringify(row.pointer.normal)===JSON.stringify(row.pointer.out);}
  else {const menu=page.locator('.menu-toggle');await menu.tap();assert.equal(await menu.getAttribute('aria-expanded'),'true');await page.screenshot({path:path.join(artifacts,`${arm}-mobile-menu.png`)});await menu.tap();assert.equal(await menu.getAttribute('aria-expanded'),'false');await page.locator(c.hero).tap();assert(page.url().includes('#'));row.checks.touchMenuAndAction=true;}
  await page.emulateMedia({reducedMotion:'reduce'});row.reducedMotion=await style(page.locator(c.confirm));row.checks.reducedMotion=parseFloat(row.reducedMotion.transition)<=0.001;assert.equal(errors.length,0,errors.join('\n'));row.checks.noRuntimeErrors=true;
  await context.close();
 }} }finally{fs.writeFileSync(path.join(artifacts,'verification.json'),JSON.stringify(records,null,2)+'\n');await browser.close();}
 console.log(JSON.stringify(records.map(r=>({arm:r.arm,device:r.device,checks:r.checks})),null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
