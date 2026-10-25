import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {normalize,searchSite} from './site-search-core.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),out=path.join(root,'dist');
const manifest=JSON.parse(fs.readFileSync(path.join(out,'site-search-manifest.json'),'utf8'));
const records=JSON.parse(fs.readFileSync(path.join(out,manifest.index),'utf8'));
const config=JSON.parse(fs.readFileSync(path.join(root,'vercel.json'),'utf8'));
const redirects=new Set(config.redirects.map(x=>x.source));
assert(records.length>2000);assert.equal(new Set(records.map(x=>x.path)).size,records.length);
for(const record of records){
 assert(!redirects.has(record.path));assert(!['/search','/explore'].includes(record.path));
 assert(record.path.startsWith('/')&&!record.path.startsWith('//'));
 const file=path.join(out,record.path,'index.html');assert(fs.existsSync(file),record.path);
 const html=fs.readFileSync(file,'utf8');assert(html.includes(`href="https://www.craftcollectivesalongroup.com${record.path}"`),record.path);
}
assert.equal(normalize('Grey colour prices'),'gray color price');
assert.equal(normalize('La Pomponnée'),'la pomponnee');
assert.equal(normalize('blow-dry'),'blowout');
const first=query=>searchSite(records,query).results[0]?.path;
assert.equal(first('balayage prices'),'/pricing/balayage-prices-pittsburgh');
assert.equal(first('Canonsburg hours'),'/locations/canonsburg');
assert.equal(first('haircut'),'/services/haircuts-pittsburgh');
assert.equal(first('Sherry'),'/sherry-maiolini');
assert.equal(first('book'),'/book');
assert(searchSite(records,'headspace pricing').results.some(x=>x.path==='/pricing/head-space-salon'));
assert.equal(first('northhills hours'),'/locations/north-hills-pittsburgh');
assert.equal(first('blow dry'),'/services/blowout-pittsburgh');
assert.equal(searchSite(records,'zzznomatch').total,0);
assert.equal(searchSite(records,'').results.length,0);
assert.equal(searchSite(records,'<script>alert(1)</script>').total,0);
const prices=searchSite(records,'balayage',{category:'pricing',limit:3});assert(prices.total>=prices.results.length);assert(prices.results.every(x=>x.category==='pricing'));assert(prices.results.length<=3);
assert(searchSite(records,'keratin cost',{category:'pricing'}).total>0);
assert(searchSite(records,'pomponnee',{category:'pricing'}).results.some(x=>x.path==='/pricing/la-pomponnee'));
const search=fs.readFileSync(path.join(out,'search/index.html'),'utf8'),explore=fs.readFileSync(path.join(out,'explore/index.html'),'utf8');
assert(search.includes('content="noindex, follow"'));assert(search.includes('<noscript>'));assert(explore.includes('href="/locations/canonsburg"'));
for(const name of fs.readdirSync(out).filter(x=>x.endsWith('sitemap.xml')))assert(!fs.readFileSync(path.join(out,name),'utf8').includes('https://www.craftcollectivesalongroup.com/search</loc>'));
assert(fs.readFileSync(path.join(out,'site-pages-sitemap.xml'),'utf8').includes('https://www.craftcollectivesalongroup.com/explore</loc>'));
for(const [route,html] of [['/search',search],['/explore',explore]])for(const [,url] of html.matchAll(/(?:href|src)="(\/[^"?#]*)/g)){
 const file=path.join(out,url);assert(fs.existsSync(file)||fs.existsSync(path.join(file,'index.html')),`${route} -> ${url}`);
}
console.log(`Site search passed: ${records.length} canonical records; service, price, stylist and location ranking; aliases, filters, empty/malicious input, utility indexing rules and browse links.`);
