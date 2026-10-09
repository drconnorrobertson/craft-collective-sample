import fs from 'node:fs';
import path from 'node:path';
import {pages} from './salon-planning-content.mjs';

const SITE='https://www.craftcollectivesalongroup.com';
const BASE='/pittsburgh-salon-planning';
const DATE='2026-10-09';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const link=(u,t)=>`<a href="${esc(u)}">${esc(t)}</a>`;
const para=s=>`<p>${esc(s)}</p>`;
const section=(h,b)=>`<section><h2>${esc(h)}</h2>${b}</section>`;
const routes=new Map(pages.map(p=>[p.slug,p.group==='Specialist services'?'/services/'+p.slug:BASE+'/'+p.slug]));
const names=new Map(pages.map(p=>[p.slug,p.title]));
const refs=slugs=>`<ul>${slugs.map(s=>`<li>${link(routes.get(s),names.get(s))}</li>`).join('')}</ul>`;

export function buildSalonPlanning(ROOT,OUT){
 const template=fs.readFileSync(path.join(ROOT,'guides/first-salon-visit-checklist-pittsburgh/index.html'),'utf8');
 const records=[];
 const booking=section('Choose your studio and appointment',
  `<p>Craft Collective has two studios: ${link('/locations/north-hills-pittsburgh','North Hills at 2014D Babcock Blvd, Pittsburgh, PA 15209')} and ${link('/locations/canonsburg','Canonsburg at 115 W Pike St, Canonsburg, PA 15317')}. The nearby-area guides describe where guests travel from; they are not additional salon locations.</p>`+
  `<p>${link('https://phorest.com/book/salons/craftcollectivesalongroup','Check North Hills appointments online')}. For Canonsburg, a complex service or help choosing a stylist, call ${link('tel:+17245147231','724-514-7231')}. Confirm the selected service, estimate, studio and preparation instructions before the visit.</p>`);
 function save(route,title,description,body,{service,group,hub=false}={}){
  if(description.length>165)description=`${title.split(':')[0]}. Compare the appointment, estimate and upkeep before booking with Craft Collective.`;
  const url=SITE+route;
  let t=template.replace(/<title>.*?<\/title>/s,`<title>${esc(title)}</title>`);
  for(const [attr,key,value] of [['name','description',description],['property','og:title',title],['property','og:description',description],['property','og:url',url],['name','twitter:title',title],['name','twitter:description',description]])
   t=t.replace(new RegExp(`(<meta ${attr}="${key}" content=")[^"]*(")`),(_,a,b)=>a+esc(value)+b);
  t=t.replace(/(<link rel="canonical" href=")[^"]*(")/,(_,a,b)=>a+url+b);
  t=t.replace(/<header class="archive-hero">.*?<\/header>/s,`<header class="archive-hero"><nav aria-label="Breadcrumb">${link('/','Home')} / ${link(BASE,'Salon planning')}${hub?'':' / '+esc(group)}</nav><h1>${esc(title)}</h1><p>Craft Collective Salon Group · Updated October 9, 2026</p></header>`);
  t=t.replace(/<article class="archive-body">.*?<\/article>/s,`<article class="archive-body">${body}${booking}</article>`);
  t=t.replace(/<script type="application\/ld\+json">.*?<\/script>/gs,'');
  const graph=[{'@type':'Organization','@id':SITE+'/#organization',name:'Craft Collective Salon Group',url:SITE,logo:{'@type':'ImageObject',url:SITE+'/images/logo.png'}},
   {'@type':hub?'CollectionPage':route.startsWith('/services/')?'WebPage':'Article','@id':url,url,name:title,description,...(!hub&&!route.startsWith('/services/')?{headline:title,datePublished:DATE,dateModified:DATE,author:{'@id':SITE+'/#organization'},publisher:{'@id':SITE+'/#organization'}}:{})},
   {'@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:'Home',item:SITE+'/'},{'@type':'ListItem',position:2,name:'Salon planning',item:SITE+BASE},...(!hub?[{'@type':'ListItem',position:3,name:title,item:url}]:[])]}];
  if(route.startsWith('/services/'))graph.push({'@type':'Service',name:title,url,provider:{'@id':SITE+'/#organization'},areaServed:'Pittsburgh metropolitan area',description});
  t=t.replace('</head>',`<link rel="stylesheet" href="/assets/pittsburgh-guides.css"><script type="application/ld+json">${JSON.stringify({'@context':'https://schema.org','@graph':graph}).replaceAll('</','<\\/')}</script></head>`);
  const file=path.join(OUT,route,'index.html');fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,t);
  records.push({path:route,title,group,service,wordCount:body.replace(/<[^>]+>/g,' ').split(/\s+/).filter(Boolean).length});
 }
 for(const p of pages){
  const related=pages.filter(x=>x.slug!==p.slug&&(x.service===p.service||x.group===p.group)).slice(0,4);
  const body=para(p.intro)+p.sections.map(([h,b])=>section(h,para(b))).join('')+
   section('Questions before booking',p.questions.map(([q,a])=>`<h3>${esc(q)}</h3>${para(a)}`).join(''))+
   section('See the work and meet the team',`<p>Explore ${link('/services/'+p.service,'the related service')}, ${link('/meet-the-team','the Craft Collective team')} and ${link('/hair-salon-gallery-pittsburgh','the salon gallery')}. Ask for examples relevant to your current hair and goal when choosing a stylist. The gallery is a portfolio, not a guarantee of an identical result on different hair.</p>`)+
   section('Continue planning',refs(related.map(x=>x.slug)));
  save(routes.get(p.slug),p.title,`${p.title.split(':')[0]}: compare options, understand the appointment and plan a Craft Collective visit in North Hills or Canonsburg.`,body,{service:p.service,group:p.group});
 }
 const groups=[...new Set(pages.map(p=>p.group))];
 save(BASE,'Pittsburgh Salon Planning: Services, Prices and Appointments','Plan Pittsburgh hair appointments with detailed guides to pricing, curly cuts, color, extensions, bridal styling and the two Craft Collective studios.',
  para('Choose a guide for the decision you are making, then confirm the service with the salon. These pages explain appointment scope, individual estimates, stylist selection and upkeep. They complement the hair-question library with more detailed help for choosing a visit.')+
  groups.map(g=>section(g,refs(pages.filter(p=>p.group===g).map(p=>p.slug)))).join('')+
  section('Explore your nearby area',`<p>${['wexford','mccandless','ross-township','cranberry-township','south-hills','mcmurray','mt-lebanon','washington-pa'].map(a=>link('/locations/'+a,a.split('-').map(w=>w[0].toUpperCase()+w.slice(1)).join(' '))).join(' · ')}</p>`)+
  section('Find a specific hair question',`<p>${link('/pittsburgh-hair-guide','Search the Pittsburgh hair-question library')} for focused questions about shapes, color choices, upkeep and service comparisons.</p>`),{hub:true,group:'Planning'});

 const enhancements={
  'balayage-pittsburgh':['Plan your balayage appointment','Tell the colorist whether you are refreshing an existing blend or creating new brightness. Identify where you want lightness, how much root contrast you prefer and how often you can return. A face-framing adjustment and a full color transition need different plans. Confirm the selected stylist and the complete estimate, including tonal finishing and a haircut when relevant.',['balayage-prices-pittsburgh','lived-in-color-pittsburgh','blonde-colorist-pittsburgh']],
  'highlights-pittsburgh':['Choose the coverage you need','Explain whether you want brightness around the face, through the top or throughout the head. Show how you wear your hair up so the stylist can discuss placement underneath as well as at the parting. Ask which areas a partial or full appointment covers and whether lowlights would help preserve the dimension you want. Confirm toning and finishing in the proposed estimate.',['highlights-prices-pittsburgh','blonde-colorist-pittsburgh','hair-gloss-toner-pittsburgh']],
  'hair-color-pittsburgh':['Book for your actual color goal','A root refresh, gray transition and uneven-color correction are different appointments. Share the recent color history and identify the area that concerns you. Ask which result is realistic first, what belongs in the estimate and what future visits would maintain. Corrective color requires an in-person consultation; call before selecting a routine color slot for a major change.',['gray-blending-pittsburgh','color-correction-pittsburgh','lived-in-color-pittsburgh','hair-gloss-toner-pittsburgh']],
  'haircuts-pittsburgh':['Match the cut to your everyday routine','Describe the current shape, the length you want to retain and how you normally dry or style your hair. For curls, show the natural finish; for a short change, include side and neckline references. Tell the stylist if the hair must tie back or if a fringe needs to work without daily heat styling. Ask how the proposed outline will grow and what maintenance to book.',['curly-haircuts-pittsburgh','kids-haircuts-pittsburgh','fine-hair-haircuts-pittsburgh','short-haircuts-pittsburgh','haircut-prices-pittsburgh']],
  'hair-extensions-pittsburgh':['Discuss the full extension commitment','Begin with the desired length and fullness, then compare methods for the same goal. Ask how the attachments would sit in your usual parting and tied-back styles. Confirm added hair, installation, matching, a blending cut, upkeep and removal in the proposal. A consultation is required; method availability and the recommended follow-up schedule should be settled with the selected specialist before ordering.',['hair-extensions-cost-pittsburgh','hand-tied-extensions-pittsburgh','tape-in-extensions-pittsburgh','keratin-bond-extensions-pittsburgh']],
  'keratin-treatment-pittsburgh':['Clarify smoothing before booking','Explain whether you want less frizz, easier blow-drying or a different finished texture. Ask which treatment is proposed, how it relates to your previous color or chemical services and what aftercare applies. Smoothing and a temporary blowout are different commitments. If you also want color or a haircut, discuss the sequence with the salon before combining services in an online booking.',['keratin-treatment-cost-pittsburgh','evening-hair-appointments-north-hills']],
  'bridal-hair-pittsburgh':['Build the wedding-day plan','Share the date, getting-ready location, group size and required finish time. Bring style references and accessories to a trial, then confirm the day-of appointment separately. For a party, list each requested service so the team can evaluate staffing and timing. Travel arrangements, packages, charges and availability must be agreed directly; do not assume a general bridal inquiry reserves a wedding date.',['bridal-hair-trial-pittsburgh','bridal-party-hair-pittsburgh','on-location-wedding-hair-pittsburgh']],
  'blowout-pittsburgh':['Plan the finish around your event','Tell the stylist whether you want volume, a smooth finish or waves, and share the time you need to leave. Discuss your current texture, washing preparation and any accessories before arriving. A blowout provides a styled finish and is different from a smoothing treatment or a permanent texture change. Check current appointment availability and allow time for travel after the service.',['last-minute-hair-appointments-pittsburgh','evening-hair-appointments-north-hills','bridal-hair-trial-pittsburgh']],
  'mens-grooming-pittsburgh':['Make the haircut request specific','Bring a reference showing the sides, top and neckline. Explain the amount of length you want to keep and how you style it at home. Ask how the selected shape works with your growth patterns and how frequently it needs attention. Confirm which detailing or finishing steps belong in the chosen appointment; the service estimate should describe your actual request rather than an assumed standard package.',['haircut-prices-pittsburgh','short-haircuts-pittsburgh','evening-hair-appointments-north-hills']]
 };
 let enhanced=0;
 const modifiedRoutes=new Set(['/faq', '/pittsburgh-hair-guide']);
 function inject(rel,html){
  const file=path.join(OUT,rel);let s=fs.readFileSync(file,'utf8');
  if(s.includes('id="salon-planning-resources"'))throw Error('Duplicate planning block '+rel);
  const block=`<section id="salon-planning-resources" class="salon-planning-resources"><div>${html}</div></section>`;
  if(s.includes('</main>'))s=s.replace('</main>',block+'</main>');
  else if(/<footer\b/.test(s))s=s.replace(/<footer\b/,block+'<footer');
  else throw Error('No insertion point '+rel);
  if(!s.includes('href="/assets/salon-planning.css"'))s=s.replace('</head>','<link rel="stylesheet" href="/assets/salon-planning.css"></head>');
  fs.writeFileSync(file,s);enhanced++;
  modifiedRoutes.add(rel==='index.html'?'/':'/'+rel.replace(/\/index\.html$/,''));
 }
 for(const [service,[h,text,slugs]] of Object.entries(enhancements))inject(`services/${service}/index.html`,`<h2>${esc(h)}</h2>${para(text)}${refs(slugs)}<p>${link(BASE,'Browse all appointment and pricing guides')}</p>`);
 const south=new Set(['canonsburg','south-hills','upper-st-clair','bethel-park','mcmurray','washington-pa','mt-lebanon']);
 const localNotes={
  'north-hills-pittsburgh':'For the Babcock Boulevard studio, use North Hills online booking. A new color direction or extension installation may need a consultation before the main service is reserved.',
  canonsburg:'For the W Pike Street studio, call for scheduling. Share the desired service and ask about the appropriate stylist and current appointment options at Canonsburg.',
  wexford:'For a Wexford-area visit, compare the requested service and stylist before choosing the travel destination. Check the Babcock Boulevard address in the North Hills booking confirmation.',
  'cranberry-township':'If you are traveling from Cranberry Township, allow time for the full service and the trip afterward. Tell the salon about an event deadline before selecting a color or styling appointment.',
  mccandless:'McCandless guests planning around work can check the North Hills calendar for the correct service. An evening opening for one service may not accommodate a longer color change.',
  'ross-township':'For Ross Township guests, begin with the specific haircut or color goal and then select the stylist. The studio address is 2014D Babcock Blvd; this area page describes the surrounding community.',
  mcmurray:'McMurray guests can call to compare Canonsburg scheduling with North Hills options. Ask which studio and stylist provide the particular appointment you want before making travel plans.',
  'washington-pa':'For a visit from Washington, PA, call about the Canonsburg studio and the complete service plan. Major color changes and extension installations need more planning than a maintenance trim.'
 };
 for(const area of fs.readdirSync(path.join(OUT,'locations'))){
  const rel=`locations/${area}/index.html`;if(!fs.existsSync(path.join(OUT,rel)))continue;
  const label=area.split('-').map(w=>w[0].toUpperCase()+w.slice(1)).join(' ');
  const target=south.has(area)?'canonsburg':'north-hills-pittsburgh';
  const note=localNotes[area]||`If you are planning a visit from ${label}, compare the actual studio addresses and selected stylist before booking. Your requested service, full appointment time and travel arrangements should determine the location you choose.`;
  inject(rel,`<h2>Plan your ${esc(label)}-area salon visit</h2>${para(note)}<p>Craft Collective has two storefronts, in North Hills Pittsburgh and Canonsburg. This nearby-area page does not represent a separate branch. Explore ${link('/locations/'+target,'the '+(target==='canonsburg'?'Canonsburg':'North Hills')+' studio')} and call to confirm another location if it better suits your plan.</p><h3>Choose the service before the calendar slot</h3><p>For new color, share your recent color history and a current photograph. For a haircut, explain the desired shape and everyday styling routine. For extensions, begin with the required consultation. Ask for a complete estimate and the next maintenance appointment before committing to a larger change.</p>${refs(['curly-haircuts-pittsburgh','gray-blending-pittsburgh','balayage-prices-pittsburgh','hair-extensions-cost-pittsburgh','bridal-party-hair-pittsburgh'])}`);
 }
 for(const rel of ['index.html','blog/index.html','hair-services-pittsburgh/index.html'])inject(rel,`<h2>Plan your next Pittsburgh hair appointment</h2><p>Explore detailed guides to specialist services, individual estimates, extensions and wedding-day arrangements.</p><p>${link(BASE,'Browse salon planning guides')} · ${link(routes.get('curly-haircuts-pittsburgh'),'Curly haircuts')} · ${link(routes.get('gray-blending-pittsburgh'),'Gray blending')} · ${link(routes.get('hair-extensions-cost-pittsburgh'),'Extension budgets')}</p>`);
 // Correct an overly broad existing claim about at-home color chemistry.
 const faqFile=path.join(OUT,'faq/index.html');let faq=fs.readFileSync(faqFile,'utf8');
 faq=faq.replace(/Box dyes deposit metallic salts and other compounds that can react unpredictably with professional color products\./g,'At-home color products differ. Tell your stylist exactly what you used so the consultation accounts for your color history.');
 fs.writeFileSync(faqFile,faq);
 const questionHub=path.join(OUT,'pittsburgh-hair-guide/index.html');let q=fs.readFileSync(questionHub,'utf8');
 q=q.replace('<article class="archive-body">',`<article class="archive-body"><aside class="archive-cta"><h2>Choosing an appointment?</h2><p>${link(BASE,'Explore detailed service, pricing and wedding guides')} before selecting a booking.</p></aside>`);fs.writeFileSync(questionHub,q);
 fs.writeFileSync(path.join(OUT,'assets/salon-planning.css'),`.salon-planning-resources{padding:4rem 1.5rem;background:#ede9e1;color:#2a2724}.salon-planning-resources>div{max-width:900px;margin:auto}.salon-planning-resources h2{font-family:'Cormorant Garamond',serif;font-size:clamp(1.8rem,4vw,2.5rem);line-height:1.2;margin:0 0 1rem}.salon-planning-resources h3{font-size:1.15rem;margin:1.5rem 0 .8rem}.salon-planning-resources p,.salon-planning-resources li{font-size:1rem;line-height:1.8}.salon-planning-resources p{margin:1rem 0}.salon-planning-resources ul{padding-left:1.25rem;margin:1rem 0}.salon-planning-resources li{margin:.5rem 0}.salon-planning-resources a{color:#715323;text-decoration:underline;text-underline-offset:3px}.salon-planning-resources a:focus-visible{outline:2px solid #715323;outline-offset:4px}`);
 // Include the new records in the existing usable search, without changing the original CSV.
 const searchFile=path.join(OUT,'pittsburgh-hair-guide/search-index.json');const search=JSON.parse(fs.readFileSync(searchFile,'utf8'));
 search.push(...records.filter(r=>r.path!==BASE).map(r=>({path:r.path,title:r.title,primaryKeyword:r.title.toLowerCase()})));fs.writeFileSync(searchFile,JSON.stringify(search));
 fs.mkdirSync(path.join(OUT,BASE),{recursive:true});fs.writeFileSync(path.join(OUT,BASE,'page-manifest.json'),JSON.stringify({updated:DATE,pages:records,enhancedExistingPages:enhanced,sources:['/faq','/hair-services-pittsburgh','/services/hair-extensions-pittsburgh','/services/bridal-hair-pittsburgh'],pricing:'Individual quotes; no invented prices'},null,2));
 const sitemap='/salon-planning-sitemap.xml';fs.writeFileSync(path.join(OUT,sitemap),`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${records.map(r=>`<url><loc>${SITE+r.path}</loc><lastmod>${DATE}</lastmod></url>`).join('')}</urlset>`);
 const rootSitemap=path.join(OUT,'sitemap.xml');let xml=fs.readFileSync(rootSitemap,'utf8');if(!xml.includes(sitemap))xml=xml.replace('</sitemapindex>',`<sitemap><loc>${SITE+sitemap}</loc><lastmod>${DATE}</lastmod></sitemap></sitemapindex>`);fs.writeFileSync(rootSitemap,xml);
 for(const name of fs.readdirSync(OUT).filter(n=>n.endsWith('sitemap.xml')&&n!=='sitemap.xml')){
  const f=path.join(OUT,name);let s=fs.readFileSync(f,'utf8');
  s=s.replace(/<url>.*?<\/url>/gs,entry=>{
   const loc=entry.match(/<loc>(.*?)<\/loc>/)?.[1];
   if(!loc?.startsWith(SITE)||!modifiedRoutes.has(loc.slice(SITE.length).replace(/\/$/,'')||'/'))return entry;
   return entry.includes('<lastmod>')?entry.replace(/<lastmod>.*?<\/lastmod>/,`<lastmod>${DATE}</lastmod>`):entry.replace('</url>',`<lastmod>${DATE}</lastmod></url>`);
  });fs.writeFileSync(f,s);
 }
 for(const r of records){
  const s=fs.readFileSync(path.join(OUT,r.path,'index.html'),'utf8');
  if((s.match(/<h1[ >]/g)||[]).length!==1)throw Error('H1 '+r.path);
  if(!s.includes(`href="${SITE+r.path}"`))throw Error('Canonical '+r.path);
  for(const m of s.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs))JSON.parse(m[1]);
  const body=s.match(/<article class="archive-body">(.*?)<\/article>/s)?.[1]||'';
  for(const m of body.matchAll(/href="(\/[^"#?]*)/g)){const f=path.join(OUT,m[1]);if(!fs.existsSync(f)&&!fs.existsSync(path.join(f,'index.html')))throw Error('Broken link '+r.path+' '+m[1]);}
 }
 if(pages.length!==24)throw Error('Unexpected new page count '+pages.length);
 console.log(JSON.stringify({newPlanningAndServicePages:pages.length,newHub:1,enhancedExistingPages:enhanced,searchEntries:search.length,minimumNewPageWords:Math.min(...records.filter(r=>r.path!==BASE).map(r=>r.wordCount))},null,2));
}
