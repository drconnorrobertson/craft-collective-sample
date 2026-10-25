// Production release checks: use only checked-in evidence and built output.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),out=path.join(root,'dist');
const read=file=>fs.readFileSync(path.join(out,file),'utf8');
const site='https://www.craftcollectivesalongroup.com';
const config=JSON.parse(fs.readFileSync(path.join(root,'vercel.json'),'utf8'));
const mapping=JSON.parse(fs.readFileSync(path.join(root,'scripts/verified-duplicate-redirects.json'),'utf8')).redirects;
const booking=JSON.parse(fs.readFileSync(path.join(root,'scripts/craft-booking-prices.json'),'utf8'));
const pricing=JSON.parse(fs.readFileSync(path.join(root,'scripts/pricing-expansion-manifest.json'),'utf8'));
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;').replaceAll("'",'&#x27;');
assert(!config.redirects.some(r=>r.source==='/locations'),'Location directory must not redirect to one branch');
const craft=read('pricing/craft-collective/index.html');
assert.equal(booking.rows.length,22);
for(const row of booking.rows)for(const cell of row.slice(1))assert(craft.includes(esc(cell)),'Missing checked booking evidence: '+cell);
assert(!booking.rows.some(row=>/\$0(?:\.00)?(?:\b|$)/.test(row[2])),'Do not publish placeholder zero amounts as completed hair-service prices');
for(const row of pricing.pages){
 const file=row.path.replace(/^\//,'')+'/index.html',html=read(file);
 assert.equal((html.match(/<h1(?:>| )/g)||[]).length,1,file);
 assert(html.includes(`href="${site+row.path}"`),'Wrong canonical '+file);
 for(const match of html.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs))JSON.parse(match[1]);
}
const xml=read('salon-pricing-sitemap.xml');
for(const entry of xml.matchAll(/<url>(.*?)<\/url>/gs)){
 const date=entry[1].match(/<lastmod>(.*?)<\/lastmod>/)?.[1];
 assert(date>=pricing.date,'Pricing sitemap regressed before declared update '+date);
}
for(const [slug,city] of [['north-hills-pittsburgh','Pittsburgh'],['canonsburg','Canonsburg']]){
 const html=read(`locations/${slug}/index.html`);
 const entities=[...html.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs)].map(m=>JSON.parse(m[1])).filter(x=>x['@type']==='HairSalon');
 assert.equal(entities.length,1);assert.equal(entities[0].address.addressLocality,city);assert(!entities[0].aggregateRating,'No unverified branch rating');
}
const book=read('book/index.html');
assert(book.indexOf('id="booking-studio-choice"')<book.indexOf('class="booking-embed"'));
for(const id of ['canonsburg-booking','north-hills-booking'])assert.equal(book.split(`id="${id}"`).length-1,1);
for(const [from,to] of Object.entries(mapping)){
 assert(config.redirects.some(r=>r.source===from&&r.destination===to&&r.permanent));
 assert(read(from.slice(1)+'/index.html').includes(`rel="canonical" href="${site+to}"`));
}
let pages=0;
for(const relative of fs.readdirSync(out,{recursive:true})){
 if(relative.endsWith('sitemap.xml')){
  const text=read(relative);for(const source of Object.keys(mapping))assert(!text.includes(site+source+'</loc>'),'Redirect remains in sitemap '+source);
 }
 if(!relative.endsWith('.html'))continue;
 const html=read(relative);pages++;
 for(const source of Object.keys(mapping))assert(!html.includes(`href="${source}"`),'Internal link to duplicate '+relative);
 assert(!/href="\/locations\/north-hills-pittsburgh"[^>]*>\s*Locations\s*<\/a>/.test(html),'Locations nav bypasses chooser '+relative);
}
console.log(`Release checks passed: ${pages} HTML pages; checked North Hills prices; pricing dates; two salon entities; booking paths; duplicate consolidation.`);
