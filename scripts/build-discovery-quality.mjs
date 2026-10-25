import fs from 'node:fs';
import path from 'node:path';
const SITE='https://www.craftcollectivesalongroup.com';
const normalizeArticle=html=>{
 const article=html.match(/<article\b[^>]*>(.*?)<\/article>/s)?.[1];
 if(!article)throw Error('Missing article for duplicate verification');
 return article.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
};
export function buildDiscoveryQuality(root,out){
 const {redirects}=JSON.parse(fs.readFileSync(path.join(root,'scripts/verified-duplicate-redirects.json'),'utf8'));
 const config=JSON.parse(fs.readFileSync(path.join(root,'vercel.json'),'utf8'));
 for(const [from,to] of Object.entries(redirects)){
  const a=fs.readFileSync(path.join(root,from,'index.html'),'utf8');
  const b=fs.readFileSync(path.join(root,to,'index.html'),'utf8');
  if(normalizeArticle(a)!==normalizeArticle(b))throw Error('Duplicate content changed; review redirect '+from);
  if(!config.redirects.some(x=>x.source===from&&x.destination===to&&x.permanent))throw Error('Missing permanent redirect '+from);
 }
 let navCount=0,rewritten=0;
 for(const relative of fs.readdirSync(out,{recursive:true})){
  if(!relative.endsWith('.html'))continue;
  const file=path.join(out,relative);let html=fs.readFileSync(file,'utf8'),before=html;
  // Only the main navigation label changes destination; individual studio links stay specific.
  html=html.replace(/<a\b[^>]*href="\/locations\/north-hills-pittsburgh"[^>]*>\s*Locations\s*<\/a>/g,match=>{navCount++;return match.replace('href="/locations/north-hills-pittsburgh"','href="/locations"');});
  for(const [from,to] of Object.entries(redirects)){
   if(html.includes(`href="${from}"`))rewritten++;
   html=html.replaceAll(`href="${from}"`,`href="${to}"`).replaceAll(`href="${SITE+from}"`,`href="${SITE+to}"`);
   if(relative.replaceAll(path.sep,'/')===from.slice(1)+'/index.html')html=html.replaceAll(SITE+from,SITE+to);
  }
  if(html!==before)fs.writeFileSync(file,html);
 }
 let removed=0;
 for(const relative of fs.readdirSync(out).filter(x=>x.endsWith('sitemap.xml'))){
  const file=path.join(out,relative);let xml=fs.readFileSync(file,'utf8');
  xml=xml.replace(/<(?:\w+:)?url\b[^>]*>.*?<\/(?:\w+:)?url>/gs,entry=>{
   const loc=entry.match(/<(?:\w+:)?loc>(.*?)<\/(?:\w+:)?loc>/)?.[1];
   if(loc&&Object.keys(redirects).some(from=>loc===SITE+from)){removed++;return '';}
   return entry;
  });fs.writeFileSync(file,xml);
 }
 console.log(JSON.stringify({discoveryQuality:{exactDuplicateRedirects:Object.keys(redirects).length,duplicateSitemapEntriesRemoved:removed,mainNavigationLocationsUpdated:navCount,pagesWithDuplicateLinksRewritten:rewritten}}));
}
