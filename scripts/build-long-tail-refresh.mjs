import fs from 'node:fs';
import path from 'node:path';
import {posts,serviceUpdates} from './long-tail-refresh-content.mjs';

const SITE='https://www.craftcollectivesalongroup.com';
const DATE='2026-10-10';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const link=([url,label])=>`<a href="${esc(url)}">${esc(label)}</a>`;
const sections=items=>items.map(([heading,text])=>`<section><h2>${esc(heading)}</h2><p>${esc(text)}</p></section>`).join('');
const related=items=>`<section><h2>Explore the next step</h2><ul>${items.map(item=>`<li>${link(item)}</li>`).join('')}</ul></section>`;
const fileFor=(out,route)=>path.join(out,route,'index.html');
function meta(html,title,description){
 html=html.replace(/<title>.*?<\/title>/s,`<title>${esc(title)}</title>`);
 for(const [attr,key,value] of [['name','description',description],['property','og:title',title],['property','og:description',description],['name','twitter:title',title],['name','twitter:description',description]]){
  const re=new RegExp(`(<meta ${attr}="${key}" content=")[^"]*(")`);
  if(re.test(html))html=html.replace(re,(_,a,b)=>a+esc(value)+b);
  else html=html.replace('</head>',`<meta ${attr}="${key}" content="${esc(value)}"></head>`);
 }
 return html;
}
function schema(html,title,description){
 return html.replace(/(<script type="application\/ld\+json">)(.*?)(<\/script>)/gs,(_,a,json,b)=>{
  const data=JSON.parse(json);
  for(const obj of data['@graph']||[data]){
   if(['BlogPosting','Article','WebPage','Service'].includes(obj['@type'])){
    if('headline' in obj)obj.headline=title;
    if('name' in obj)obj.name=title;
    obj.description=description;
    if(obj['@type']!=='Service')obj.dateModified=DATE;
   }
   if(obj['@type']==='BreadcrumbList')obj.itemListElement.at(-1).name=title;
  }
  return a+JSON.stringify(data).replaceAll('</','<\\/')+b;
 });
}

export function buildLongTailRefresh(out){
 const changed=new Set(),report=[];
 const searchFile=path.join(out,'pittsburgh-hair-guide/search-index.json');
 const search=JSON.parse(fs.readFileSync(searchFile,'utf8'));
 for(const post of posts){
  const route='/post/'+post.slug,file=fileFor(out,route);
  let html=fs.readFileSync(file,'utf8');
  const article=html.match(/<article class="archive-body">(.*?)<\/article>/s)?.[1];
  if(!article)throw Error('Missing article '+route);
  // Keep existing portfolio media and all appointment CTAs exactly as authored.
  const media=[...article.matchAll(/<figure\b[^>]*>.*?<\/figure>/gs)].map(m=>m[0]).join('');
  const ctas=[...article.matchAll(/<aside class="archive-cta">.*?<\/aside>/gs)].map(m=>m[0]).filter(s=>!s.includes('<h2>Quick answer</h2>')).join('');
  if(!ctas)throw Error('Missing original CTA '+route);
  const comparison=post.slug.startsWith('the-difference-between-a-blowout')?'<section><h2>Compare the three appointment descriptions</h2><div class="comparison-scroll"><table><thead><tr><th scope="col">Name</th><th scope="col">Main decision</th><th scope="col">Confirm before booking</th></tr></thead><tbody><tr><th scope="row">Regular blowout</th><td>Temporary styled finish</td><td>Shape, finishing and refresh routine</td></tr><tr><th scope="row">Brazilian Blowout</th><td>A branded smoothing system</td><td>Brand availability, intended texture change and aftercare</td></tr><tr><th scope="row">Keratin treatment</th><td>The specific smoothing product proposed</td><td>System, suitability, estimate and upkeep</td></tr></tbody></table></div></section>':'';
  const sources=post.sources?`<section><h2>Further reading</h2><p>Confirm the exact smoothing product and review its instructions with the salon. The FDA explains that ingredient information matters when evaluating smoothing products.</p><ul>${post.sources.map(x=>`<li>${link(x)}</li>`).join('')}</ul></section>`:'';
  const body=`<aside class="archive-cta"><h2>Quick answer</h2><p>${esc(post.answer)}</p></aside>${media}${comparison}${sections(post.sections)}<section><h2>Common questions</h2>${post.questions.map(([q,a])=>`<h3>${esc(q)}</h3><p>${esc(a)}</p>`).join('')}</section>${related(post.links)}${sources}${ctas}`;
  html=html.replace(/<article class="archive-body">.*?<\/article>/s,`<article class="archive-body">${body}</article>`);
  html=html.replace(/<h1\b[^>]*>.*?<\/h1>/s,`<h1>${esc(post.title)}</h1>`);
  html=html.replace(/<p class="archive-meta">.*?<\/p>/s,'<p class="archive-meta">Craft Collective Team · Updated October 10, 2026</p>');
  html=schema(meta(html,post.title,post.description),post.title,post.description);
  fs.writeFileSync(file,html);changed.add(route);
  const record={path:route,title:post.title,primaryKeyword:post.keywords[0],relatedKeywords:post.keywords.slice(1),priority:30};
  const existing=search.findIndex(x=>x.path===route);if(existing>=0)search[existing]=record;else search.push(record);
  report.push({path:route,title:post.title,keywords:post.keywords,action:'Revised existing article; retained original media and appointment CTAs'});
  for(const topic of post.topics){
   const hubRoute='/pittsburgh-hair-guide/'+topic,hubFile=fileFor(out,hubRoute);
   let hub=fs.readFileSync(hubFile,'utf8');
   const block=`<section data-long-tail-refresh><h2>Start with a practical guide</h2><p>${link([route,post.title])}</p></section>`;
   hub=hub.replace('<section><h2>Choose your question</h2>',block+'<section><h2>Choose your question</h2>');
   if(!hub.includes('data-long-tail-refresh'))throw Error('Hub insertion failed '+topic);
   hub=hub.replace(/"dateModified":"[0-9-]+"/g,`"dateModified":"${DATE}"`);
   hub=hub.replace('Updated October 9, 2026','Updated October 10, 2026');
   fs.writeFileSync(hubFile,hub);changed.add(hubRoute);
  }
 }
 for(const service of serviceUpdates){
  const file=fileFor(out,service.path);let html=fs.readFileSync(file,'utf8');
  html=html.replace('<section><h2>Questions before booking</h2>',sections(service.sections)+related(service.links)+'<section><h2>Questions before booking</h2>');
  if(!html.includes(esc(service.sections[0][0])))throw Error('Service insertion failed');
  html=schema(meta(html,service.title,service.description),service.title,service.description);
  html=html.replace('Updated October 9, 2026','Updated October 10, 2026');
  fs.writeFileSync(file,html);changed.add(service.path);
  const record=search.find(x=>x.path===service.path);if(record)Object.assign(record,{title:service.title,primaryKeyword:service.path.includes('gray')?'gray blending pittsburgh':'curly haircuts pittsburgh',relatedKeywords:service.path.includes('gray')?['grey blending pittsburgh','gray blending dark hair','gray blending vs coverage']:['curly hair salon pittsburgh','wavy haircut pittsburgh','curly hair specialist pittsburgh']});
  report.push({path:service.path,title:service.title,action:'Expanded existing service page; retained appointment section'});
 }
 fs.writeFileSync(searchFile,JSON.stringify(search));
 const modifiedSitemaps=[];
 for(const name of fs.readdirSync(out).filter(n=>n.endsWith('sitemap.xml')&&n!=='sitemap.xml')){
  const file=path.join(out,name);let xml=fs.readFileSync(file,'utf8');
  const original=xml;
  xml=xml.replace(/<url>.*?<\/url>/gs,entry=>{
   const loc=entry.match(/<loc>(.*?)<\/loc>/)?.[1];
   if(!loc?.startsWith(SITE)||!changed.has(loc.slice(SITE.length).replace(/\/$/,'')||'/'))return entry;
   return /<lastmod>/.test(entry)?entry.replace(/<lastmod>.*?<\/lastmod>/,`<lastmod>${DATE}</lastmod>`):entry.replace('</url>',`<lastmod>${DATE}</lastmod></url>`);
  });fs.writeFileSync(file,xml);if(xml!==original)modifiedSitemaps.push(name);
 }
 const rootSitemap=path.join(out,'sitemap.xml');
 fs.writeFileSync(rootSitemap,fs.readFileSync(rootSitemap,'utf8').replace(/<sitemap>.*?<\/sitemap>/gs,entry=>{
  if(!modifiedSitemaps.some(name=>entry.includes(SITE+'/'+name)))return entry;
  return entry.includes('<lastmod>')?entry.replace(/<lastmod>.*?<\/lastmod>/,`<lastmod>${DATE}</lastmod>`):entry.replace('</sitemap>',`<lastmod>${DATE}</lastmod></sitemap>`);
 }));
 for(const route of changed){
  const html=fs.readFileSync(fileFor(out,route),'utf8');
  if((html.match(/<h1[ >]/g)||[]).length!==1)throw Error('H1 '+route);
  if(!html.includes(`rel="canonical" href="${SITE+route}"`))throw Error('Canonical '+route);
  for(const m of html.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs))JSON.parse(m[1]);
  for(const m of html.matchAll(/href="(\/[^"#?]*)/g)){
   const target=path.join(out,m[1]);if(!fs.existsSync(target)&&!fs.existsSync(path.join(target,'index.html')))throw Error('Broken link '+route+' '+m[1]);
  }
 }
 console.log(JSON.stringify({longTailRefresh:report,topicHubsLinked:changed.size-report.length,newUrls:0,bookingFlow:'Original CTAs, widget and shared scripts retained'},null,2));
}
