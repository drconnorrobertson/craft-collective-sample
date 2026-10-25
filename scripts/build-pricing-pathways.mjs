import fs from 'node:fs';
import path from 'node:path';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
export function buildPricingPathways(root,out){
 const research=JSON.parse(fs.readFileSync(path.join(root,'scripts/pricing-research.json'),'utf8'));
 let linked=0;
 for(const salon of research.salons){
  const file=path.join(out,salon.comparison,'index.html');
  if(!fs.existsSync(file))throw Error('Missing comparison for pricing pathway: '+salon.comparison);
  let html=fs.readFileSync(file,'utf8');
  if(!html.includes(`href="/pricing/${salon.slug}"`)){
   const block=`<section class="archive-body"><h2>${esc(salon.name)} pricing details</h2><p><a href="/pricing/${esc(salon.slug)}">Read the source-linked pricing guide</a> for published menu examples, inclusions and estimate questions.</p></section>`;
   if(!html.includes('</article>'))throw Error('Missing comparison article '+salon.comparison);
   html=html.replace('</article>',block+'</article>');fs.writeFileSync(file,html);
  }
  linked++;
 }
 const file=path.join(out,'pittsburgh-hair-guide/salons/index.html');
 let html=fs.readFileSync(file,'utf8');
 if(!html.includes('href="/pricing"')){
  html=html.replace('</article>','<section><h2>Compare published salon prices</h2><p><a href="/pricing">Browse the Pittsburgh salon pricing directory</a> and <a href="/pricing/craft-collective">Craft Collective published prices and estimate guidance</a>.</p></section></article>');
  fs.writeFileSync(file,html);
 }
 // Keep pricing available from the shared Resources footer across the built site.
 let footerCount=0;
 for(const relative of fs.readdirSync(out,{recursive:true})){
  if(!relative.endsWith('.html'))continue;
  const page=path.join(out,relative);let markup=fs.readFileSync(page,'utf8');
  if(markup.includes('>Salon Pricing</a>'))continue;
  const updated=markup.replace(/(<li><a href="\/hair-care-tips"[^>]*>)/,'<li><a href="/pricing">Salon Pricing</a></li>$1');
  if(updated!==markup){fs.writeFileSync(page,updated);footerCount++;}
 }
 console.log(`Pricing footer links: ${footerCount} pages.`);
 console.log(`Pricing pathways: ${linked} salon comparisons linked to dedicated pricing pages.`);
}
