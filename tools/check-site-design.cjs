/* Cross-page regressions: one masthead, working mobile navigation, persisted
   theme, readable content, correct profile links and no clipped page width. */
const {chromium}=require('playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
const base=process.env.COURSE_BASE_URL||'http://127.0.0.1:8765/';
const out='test-results/readable';fs.mkdirSync(out,{recursive:true});
const pub=JSON.parse(fs.readFileSync('curriculum/publication.json','utf8'));
const pages=['iscarb.html','student-guide.html','course-resources.html','instructor-guide.html','nelc-alignment.html','methodology.html','fbr-submission.html','download.html','download-stats.html','index.html','iscarb-students.html','404.html','cimt.html','imam.html',...pub.lectures.map(c=>c.study_path)];
(async()=>{
 const browser=await chromium.launch(),results={pages:[],errors:[]};
 for(const width of [1440,1024,390,320]){
  const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage();
  page.on('pageerror',e=>results.errors.push({width,error:e.message}));
  // Public counters/gallery are not part of this design test. No synthetic hits.
  await context.route('**/*.supabase.co/**',r=>r.abort());
  for(const file of pages){
   try{
    await page.goto(base+file);
    assert.equal(await page.locator('.site-header').count(),1,'one masthead');
    assert.equal(await page.locator('.site-footer').count(),1,'one shared footer');
    assert.equal(await page.locator('.site-header .profile-link').getAttribute('href'),'https://adeebnoor.github.io/');
    assert.equal(await page.locator('.site-nav a').count(),6,'stable navigation');
    assert.equal(await page.locator('.iscarb-methodology-nav').count(),0,'no legacy navigation injector');
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'horizontal overflow');
    assert(await page.locator('.site-brand img').evaluate(im=>im.complete&&im.naturalWidth>0),'brand image');
    if(width<901){
     assert(!(await page.locator('#courseNav').isVisible()));await page.locator('#navToggle').click();
     assert(await page.locator('#courseNav').isVisible());await page.keyboard.press('Escape');
     assert(!(await page.locator('#courseNav').isVisible()));
     assert.equal(await page.locator('#navToggle').getAttribute('aria-expanded'),'false');
    }
    await page.locator('#themeBtn').click();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
    assert.equal(await page.locator('body').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(11, 21, 32)');
    await page.reload();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
    if(['course-resources.html','methodology.html'].includes(file)&&[1440,390].includes(width))await page.screenshot({path:out+'/site-'+file.replace('.html','')+'-'+width+'-dark.png'});
    await page.locator('#themeBtn').click();assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
    if(['course-resources.html','student-guide.html','methodology.html','iscarb.html','lectures/iscarb/sources/Ch13-Study.html'].includes(file)&&[1440,390].includes(width))await page.screenshot({path:out+'/site-'+file.split('/').pop().replace('.html','')+'-'+width+'.png'});
    results.pages.push({file,width,pass:true});
   }catch(e){results.errors.push({file,width,error:e.message});await page.screenshot({path:out+'/site-FAIL-'+file.split('/').pop()+'-'+width+'.png'});}
  }
  await context.close();
 }
 // The exact screenshot reported by the instructor: source slide 48 on R11.
 const context=await browser.newContext({viewport:{width:1440,height:900}}),page=await context.newPage();
 await page.goto(base+'lectures/iscarb/Ch13-Security-Engineering.html#R11');
 await page.locator('.source-vector img').evaluate(im=>im.decode());
 await page.screenshot({path:out+'/fixed-ch13-R11.png'});
 await page.locator('.source-vector').click();
 await page.screenshot({path:out+'/fixed-ch13-expanded.png'});
 await browser.close();fs.writeFileSync(out+'/site-design-results.json',JSON.stringify(results,null,2));
 console.log(JSON.stringify({pageChecks:results.pages.length,errors:results.errors},null,2));
 if(results.errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
