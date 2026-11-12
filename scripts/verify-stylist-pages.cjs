// Keep every rostered artist discoverable at one canonical profile URL.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),out=process.argv.includes('--source')?root:path.join(root,'dist');
const site='https://www.craftcollectivesalongroup.com';
const read=file=>fs.readFileSync(path.join(out,file),'utf8');
const schemas=html=>[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(m=>JSON.parse(m[1]));
const roster=read('meet-the-team/index.html');
const artists=schemas(roster).find(d=>d['@type']==='ItemList').itemListElement.map(x=>x.item).filter(x=>x.jobTitle!=='Assistant');
const titles=new Set(),urls=new Set();
const sitemapFiles=fs.readdirSync(out).filter(p=>p.endsWith('sitemap.xml'));
const sitemap=sitemapFiles.map(read).join('\n');
for(const artist of artists){
 const route=artist.url.slice(site.length);
 assert(artist.url.startsWith(site+'/')&&!route.includes('#'),artist.name+' needs a dedicated page');
 assert(!urls.has(route),'Duplicate roster profile: '+route);urls.add(route);
 assert(roster.includes('href="'+route+'"'),'Missing roster link: '+route);
 const html=read(route.slice(1)+'/index.html');
 const canonical=[...html.matchAll(/<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"/g)];
 assert.equal(canonical.length,1);assert.equal(canonical[0][1],artist.url);
 assert(!/<meta\b[^>]*name="robots"[^>]*content="[^"]*noindex/i.test(html));
 const title=html.match(/<title>(.*?)<\/title>/)[1];assert(title.includes(artist.name));assert(!titles.has(title));titles.add(title);
 assert.equal([...html.matchAll(/<h1\b/g)].length,1);
 const heading=html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/)[1].replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();assert.equal(heading,artist.name);
 const profile=schemas(html).find(d=>d['@type']==='ProfilePage');assert(profile,'Missing ProfilePage: '+route);
 assert.equal(profile.url,artist.url);assert.equal(profile.mainEntity.name,artist.name);assert.equal(profile.mainEntity.url,artist.url);
 for(const social of profile.mainEntity.sameAs||[])assert(html.includes('href="'+social+'"'),'Structured social link must be visible: '+route);
 assert(sitemap.includes('<loc>'+artist.url+'</loc>'),'Missing sitemap entry: '+route);
 assert(/href="(?:https:\/\/phorest.com\/book\/salons\/craftcollectivesalongroup|\/book)"/.test(html),'Missing booking pathway: '+route);
}
for(const entry of fs.readdirSync(path.join(out,'meet-the-team'),{withFileTypes:true}).filter(e=>e.isDirectory())){
 const file='meet-the-team/'+entry.name+'/index.html';if(!fs.existsSync(path.join(out,file)))continue;
 const html=read(file),canonical=html.match(/<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"/);
 if(canonical&&urls.has(canonical[1].slice(site.length)))assert(!sitemap.includes('<loc>'+site+'/meet-the-team/'+entry.name+'</loc>'),'Duplicate legacy profile in sitemap: '+entry.name);
}
console.log('Validated '+artists.length+' dedicated artist profiles: roster links, unique titles, canonical URLs, ProfilePage/Person schema, visible social links, booking paths, and sitemap coverage.');
