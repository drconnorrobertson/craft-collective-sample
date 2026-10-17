import fs from 'node:fs';
import path from 'node:path';

const SITE='https://www.craftcollectivesalongroup.com';
const DATE='2026-10-17';
const gray='/services/gray-blending-pittsburgh';
const consolidated=new Set(['booking','first-visit','hair-history','fine-hair','dense-hair','maintenance','grow-out'].map(x=>'/pittsburgh-hair-guide/color/gray-blending/'+x));
const natural=s=>s.replaceAll('Extensions for length for Fine Hair','Length Extensions for Fine Hair').replaceAll('extensions for length for fine hair','length extensions for fine hair').replaceAll('Extensions for length','Length Extensions').replaceAll('extensions for length','length extensions').replaceAll('Extensions for volume','Volume Extensions').replaceAll('extensions for volume','volume extensions').replaceAll('Curly-hair haircut','Curly Haircut').replaceAll('curly-hair haircut','curly haircut').replaceAll('Gray blending','Gray Blending');
const nextStep='<section data-service-quality><h2>Choose your studio and next step</h2><p>Visit our <a href="/locations/north-hills-pittsburgh">North Hills salon on Babcock Boulevard</a> or our <a href="/locations/canonsburg">Canonsburg studio</a>. <a href="/book">Check North Hills appointments online</a>; call <a href="tel:7245147231">724-514-7231</a> for Canonsburg or help choosing a service.</p><p>Before reserving a complex service, confirm the stylist, studio, appointment length and complete estimate, including any consultation, toning, haircut or finishing that applies. Browse <a href="/hair-salon-gallery-pittsburgh">our salon portfolio</a> and <a href="/meet-the-team">meet the team</a> to discuss work relevant to your goal.</p></section>';
const grayPlan='<section data-gray-plan><h2>Your gray-blending appointment plan</h2><h3>Before booking and your first visit</h3><p>Decide whether you want to keep some gray visible, cover it or transition toward natural silver. Bring current photographs showing your part, hairline and lengths, plus reference pictures of the amount of silver you want. Share your salon and home-color history, especially repeated permanent color on the lengths. Ask which appointment fits that starting point before selecting a menu item.</p><h3>Fine strands and dense hair</h3><p>Explain strand thickness and overall density separately. With fine strands, discuss where lightness and contrast will preserve the appearance of fullness. With dense hair, show the underneath as well as the surface and ask how the placement and time estimate account for each section. The consultation should determine the plan rather than the hair label alone.</p><h3>Maintenance and growing out color</h3><p>Agree on the amount of contrast you are comfortable seeing as roots grow. Ask whether future visits would refresh tone, adjust placement or continue a transition. Photograph your roots in similar lighting between visits so the stylist can assess the change. Confirm a return plan that fits your budget and routine, including which appointment to book next.</p></section>';

export function buildServiceQuality(out){
 let changed=0; const modified=new Set();
 function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const file=path.join(dir,entry.name);if(entry.isDirectory())walk(file);else if(entry.name.endsWith('.html')){
  const route='/'+path.relative(out,file).replaceAll(path.sep,'/').replace(/\/index\.html$/,'').replace(/^index\.html$/,'');
  let html=fs.readFileSync(file,'utf8'),before=html;
  // Preserve href/src attributes, URL slugs and JSON-LD identifiers.
  html=html.replace(/>[^<>]+</g,text=>natural(text));
  html=html.replace(/(<meta\b[^>]*content=")([^"]*)(")/g,(_,a,b,c)=>a+natural(b)+c);
  html=html.replace(/(<script type="application\/ld\+json">)(.*?)(<\/script>)/gs,(_,a,json,b)=>{
   const data=JSON.parse(json);const clean=o=>{if(!o||typeof o!=='object')return;for(const key of Object.keys(o)){if(['name','headline','description'].includes(key)&&typeof o[key]==='string')o[key]=natural(o[key]);else if(typeof o[key]==='object')clean(o[key]);}};clean(data);return a+JSON.stringify(data).replaceAll('</','<\\/')+b;
  });
  if(route.startsWith('/services/')||['/hair-services-pittsburgh','/locations/north-hills-pittsburgh','/locations/canonsburg'].includes(route)){
   html=html.includes('<article class="archive-body">')?html.replace('</article>',nextStep+'</article>'):html.replace('<footer>',`<div class="content-section"><div class="content-inner prose">${nextStep}</div></div><footer>`);
  }
  if(route===gray)html=html.replace('</article>',grayPlan+'</article>');
  for(const old of consolidated)html=html.replaceAll(`href="${old}"`,`href="${gray}"`);
  if(consolidated.has(route)){
   html=html.replace(/(<link\b[^>]*rel="canonical"[^>]*href=")[^"]*(")/,`$1${SITE+gray}$2`);
   html=html.replace('<article class="archive-body">','<article class="archive-body"><aside class="archive-cta"><h2>Read the complete gray-blending plan</h2><p>Booking, hair history, texture and upkeep are covered together in our <a href="'+gray+'">gray-blending service guide</a>.</p></aside>');
  }
  if(html!==before){fs.writeFileSync(file,html);modified.add(route);changed++;}
 }}}
 walk(out);
 const searchFile=path.join(out,'pittsburgh-hair-guide/search-index.json');
 const search=JSON.parse(fs.readFileSync(searchFile,'utf8')).filter(x=>!consolidated.has(x.path));
 for(const row of search){row.title=natural(row.title);if(row.path===gray)row.priority=40;}
 fs.writeFileSync(searchFile,JSON.stringify(search));
 for(const name of fs.readdirSync(out).filter(x=>x.endsWith('sitemap.xml'))){const file=path.join(out,name);let xml=fs.readFileSync(file,'utf8');xml=xml.replace(/<url>.*?<\/url>/gs,entry=>{const loc=entry.match(/<loc>(.*?)<\/loc>/)?.[1];const route=loc?.replace(SITE,'').replace(/\/$/,'')||'/';if(consolidated.has(route))return '';if(!modified.has(route))return entry;return entry.includes('<lastmod>')?entry.replace(/<lastmod>.*?<\/lastmod>/,`<lastmod>${DATE}</lastmod>`):entry.replace('</url>',`<lastmod>${DATE}</lastmod></url>`);});fs.writeFileSync(file,xml);}
 console.log(JSON.stringify({serviceQuality:{updatedPages:changed,consolidatedGrayGuides:consolidated.size,date:DATE}}));
}
