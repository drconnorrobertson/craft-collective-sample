import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const SITE='https://www.craftcollectivesalongroup.com',DATE='2026-10-25';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const decode=s=>s.replace(/&(?:amp|quot|lt|gt|apos|#39|#x27|#8217);/g,x=>({'&amp;':'&','&quot;':'"','&lt;':'<','&gt;':'>','&apos;':"'",'&#39;':"'",'&#x27;':"'",'&#8217;':'’'}[x]));
const link=(url,title)=>`<a href="${esc(url)}">${esc(title)}</a>`;
const hash=s=>createHash('sha256').update(s).digest('hex').slice(0,12);
export function buildSiteSearch(root,out){
 const config=JSON.parse(fs.readFileSync(path.join(root,'vercel.json'),'utf8'));
 const redirects=new Set(config.redirects.map(x=>x.source));
 const records=[];
 for(const relative of fs.readdirSync(out,{recursive:true})){
  if(!relative.endsWith('/index.html')&&relative!=='index.html')continue;
  const route='/'+relative.replaceAll(path.sep,'/').replace(/\/index\.html$/,'').replace(/^index\.html$/,'');
  if(redirects.has(route)||['/search','/explore'].includes(route))continue;
  const html=fs.readFileSync(path.join(out,relative),'utf8');
  const canonical=html.match(/<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"/)?.[1];
  if(canonical!==SITE+route||/<meta\b[^>]*name="robots"[^>]*content="[^"]*noindex/i.test(html))continue;
  const title=decode(html.match(/<title>(.*?)<\/title>/s)?.[1]||'').replace(/\s*[|—]\s*Craft Collective.*$/,'').trim();
  if(!title)continue;
  const description=decode(html.match(/<meta\b[^>]*name="description"[^>]*content="([^"]*)"/)?.[1]||'Explore this Craft Collective page.');
  let category='guides',priority=25,keywords='';
  if(route.startsWith('/pricing')){category='pricing';priority=95;keywords+=' prices cost estimates quote';}
  else if(route.startsWith('/services/')||route==='/hair-services-pittsburgh'){category='services';priority=/^\/services\/(haircuts|balayage|highlights|hair-color|hair-extensions|keratin-treatment|blowout|bridal-hair|mens-grooming)-pittsburgh$/.test(route)?125:100;}
  else if(route.startsWith('/locations')){category='locations';const physical=/\/(canonsburg|north-hills-pittsburgh)$/.test(route);priority=physical?125:route==='/locations'?110:55;keywords+=physical||route==='/locations'?' location directions hours address phone book':' service area travel';}
  else if(route.startsWith('/team/')||['/meet-the-team','/derek-piekarski','/sherry-maiolini','/artist-team'].includes(route)){category='artists';priority=90;keywords+=' stylist artist team';}
  else if(route.startsWith('/post/')||route.startsWith('/blog/')){category='articles';priority=20;}
  else if(route.startsWith('/pittsburgh-hair-guide/')){priority=5;}
  else if(route.startsWith('/pittsburgh-salon-planning')){priority=65;if(/(?:cost|prices)/.test(route))category='pricing';}
  if(route.startsWith('/guides/craft-collective-vs-')||route.startsWith('/pittsburgh-hair-guide/salons/craft-collective-vs-'))priority=105;
  if(route==='/services/haircuts-pittsburgh')keywords+=' women womens men mens child children kids';
  if(route==='/services/blowout-pittsburgh'||route==='/pricing/blowout-styling-prices-pittsburgh')keywords+=' blow dry blowdry';
  if(route==='/book'){category='services';priority=115;keywords+=' book appointment schedule availability north hills canonsburg';}
  if(route==='/pricing/craft-collective'){priority=115;keywords+=' haircut hair color balayage highlight blow dry starting';}
  if(route==='/locations/canonsburg')keywords+=' call appointments pike street';
  if(route==='/locations/north-hills-pittsburgh')keywords+=' babcock booking';
  records.push({path:route,title,description,category,priority,keywords});
 }
 records.sort((a,b)=>a.path.localeCompare(b.path));
 const core=fs.readFileSync(path.join(root,'scripts/site-search-core.mjs'),'utf8'),coreName=`site-search-core.${hash(core)}.mjs`;
 const client=fs.readFileSync(path.join(root,'scripts/site-search-client.mjs'),'utf8').replace('./site-search-core.mjs','./'+coreName),clientName=`site-search-client.${hash(client)}.mjs`;
 const index=JSON.stringify(records),indexName=`site-search-index.${hash(index)}.json`;
 for(const [name,content] of [[coreName,core],[clientName,client],[indexName,index]])fs.writeFileSync(path.join(out,'assets',name),content);
 const template=fs.readFileSync(path.join(root,'guides/first-salon-visit-checklist-pittsburgh/index.html'),'utf8');
 function page(route,title,description,body,{noindex=false}={}){
  let html=template.replace(/<title>.*?<\/title>/s,`<title>${esc(title)}</title>`);
  for(const [kind,key,value] of [['name','description',description],['property','og:title',title],['property','og:description',description],['property','og:url',SITE+route]])html=html.replace(new RegExp(`(<meta ${kind}="${key}" content=")[^"]*(")`),(_,a,b)=>a+esc(value)+b);
  html=html.replace(/(<link rel="canonical" href=")[^"]*(")/,`$1${SITE+route}$2`);
  html=html.replace(/<header class="archive-hero">.*?<\/header>/s,`<header class="archive-hero"><p>${link('/','Home')} / ${esc(title)}</p><h1>${esc(title)}</h1><p>Find your next service, artist or appointment.</p></header>`);
  html=html.replace(/<article class="archive-body">.*?<\/article>/s,`<article class="archive-body">${body}</article>`);
  html=html.replace(/<script type="application\/ld\+json">.*?<\/script>/gs,'');
  if(noindex)html=html.replace(/<meta\b[^>]*name="robots"[^>]*>/g,'').replace('</head>','<meta name="robots" content="noindex, follow"></head>');
  const schema={'@context':'https://schema.org','@type':noindex?'WebPage':'CollectionPage',name:title,url:SITE+route,description,dateModified:DATE};
  html=html.replace('</head>',`<link rel="stylesheet" href="/assets/site-search.css"><script type="application/ld+json">${JSON.stringify(schema).replaceAll('</','<\\/')}</script></head>`);
  if(noindex)html=html.replace('</body>',`<script type="module" src="/assets/${clientName}"></script></body>`);
  const file=path.join(out,route,'index.html');fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,html);
 }
 const quick=`<section><h2>Popular starting points</h2><ul class="site-search-shortcuts"><li>${link('/locations','Choose a studio')}</li><li>${link('/book','Booking options')}</li><li>${link('/pricing/craft-collective','Craft prices')}</li><li>${link('/meet-the-team','Find an artist')}</li><li>${link('/pricing','Salon price comparisons')}</li><li>${link('/guides/pittsburgh-salon-alternatives','Salon alternatives')}</li></ul></section>`;
 const browse=`<section><h2>Browse instead</h2><p>${link('/explore','Explore services, artists and planning guides')} or ${link('/hair-services-pittsburgh','open the full service menu')}. For help choosing a reservation, call ${link('tel:+17245147231','724-514-7231')}.</p><p>North Hills offers online booking. Canonsburg is by appointment; call to confirm the artist and schedule.</p></section>`;
 page('/search','Search Craft Collective','Find Craft Collective services, stylists, prices, studio details and hair guides in one place.',`<form id="site-search" data-index="/assets/${indexName}" role="search"><label for="site-search-query">Service, stylist, price or question</label><input type="search" id="site-search-query" name="q" maxlength="200" placeholder="Try balayage prices, Canonsburg or a stylist name" aria-controls="site-search-results"><label for="site-search-category">Topic</label><select id="site-search-category"><option value="all">All topics</option><option value="services">Services and booking</option><option value="pricing">Prices</option><option value="locations">Locations</option><option value="artists">Stylists</option><option value="guides">Planning guides</option><option value="articles">Articles</option></select><button type="submit">Search</button><button type="reset">Clear</button><p id="site-search-status" role="status" aria-live="polite">Enter a search or browse below.</p></form><ul id="site-search-results" class="site-search-results"></ul><noscript><style>#site-search{display:none}</style><p>Search requires JavaScript. Use the directory links below to browse every main service and artist.</p></noscript>${quick}${browse}`,{noindex:true});
 const sections=[['services','Services and appointment options'],['artists','Stylists and professional background'],['pricing','Published prices and salon comparisons']];
 let directory=`<p>Use this directory to browse the main Craft Collective services, artist pages and price guides. For a specific question, ${link('/search','search the whole site')}.</p><section><h2>Two studios</h2><p>Craft has two physical studios: ${link('/locations/north-hills-pittsburgh','North Hills Pittsburgh')} and ${link('/locations/canonsburg','Canonsburg')}. Nearby-area pages describe travel and service areas, not additional storefronts.</p><p>${link('/locations','Compare studios and get directions')} · ${link('/book','Check booking options')}</p></section>`;
 for(const [category,label] of sections){
  const selected=records.filter(x=>x.category===category).sort((a,b)=>b.priority-a.priority||a.title.localeCompare(b.title));
  directory+=`<section><h2>${esc(label)}</h2><ul class="site-explore-list">${selected.map(x=>`<li>${link(x.path,x.title)}</li>`).join('')}</ul></section>`;
 }
 directory+=`<section><h2>Planning and hair questions</h2><ul class="site-explore-list">${[['/guides','Salon planning guides'],['/pittsburgh-salon-planning','Detailed appointment planning'],['/pittsburgh-hair-guide','Search hair questions and comparisons'],['/guides/pittsburgh-salon-alternatives','Local salon alternatives'],['/blog','Hair articles'],['/reviews','Guest reviews'],['/hair-salon-gallery-pittsburgh','Work gallery']].map(([url,label])=>`<li>${link(url,label)}</li>`).join('')}</ul></section>`;
 page('/explore','Explore Craft Collective','Browse Craft Collective services, stylist pages, prices, studios and planning guides. Find a clear next step for your Pittsburgh or Canonsburg appointment.',directory);
 // Search is an internal utility, deliberately kept out of XML sitemaps.
 const sitemap=path.join(out,'site-pages-sitemap.xml');let xml=fs.readFileSync(sitemap,'utf8');
 if(!xml.includes(SITE+'/explore</loc>'))xml=xml.replace('</urlset>',`<url><loc>${SITE}/explore</loc><lastmod>${DATE}</lastmod></url></urlset>`);fs.writeFileSync(sitemap,xml);
 let connected=0;
 for(const relative of fs.readdirSync(out,{recursive:true}).filter(x=>x.endsWith('.html'))){
  const file=path.join(out,relative);let html=fs.readFileSync(file,'utf8');
  if(!html.includes('>Search the Site</a>')){
   const links=`<li>${link('/search','Search the Site')}</li><li>${link('/explore','Explore Craft')}</li>`;
   if(html.includes('>Salon Pricing</a>'))html=html.replace(/(<li><a href="\/pricing"[^>]*>Salon Pricing<\/a><\/li>)/,`$1${links}`);
   else html=html.replace(/(<li><a href="\/hair-care-tips"[^>]*>)/,`<li>${link('/pricing','Salon Pricing')}</li>${links}$1`);
  }
  if(['index.html','guides/index.html','pricing/index.html','pittsburgh-hair-guide/index.html'].includes(relative)){
   const block=`<section class="archive-body"><h2>Find the page you need</h2><p>${link('/search','Search services, stylists, prices and guides')} or ${link('/explore','browse the Craft Collective directory')}.</p></section>`;
   html=html.includes('</main>')?html.replace('</main>',block+'</main>'):html.replace('<footer',block+'<footer');
  }
  fs.writeFileSync(file,html);if(html.includes('>Search the Site</a>'))connected++;
 }
 fs.writeFileSync(path.join(out,'site-search-manifest.json'),JSON.stringify({date:DATE,index:'/assets/'+indexName,client:'/assets/'+clientName,core:'/assets/'+coreName,records:records.length,categories:Object.fromEntries([...new Set(records.map(x=>x.category))].map(c=>[c,records.filter(x=>x.category===c).length]))},null,2));
 console.log(JSON.stringify({siteSearch:{records:records.length,indexBytes:Buffer.byteLength(index),footerPages:connected,utility:'/search',directory:'/explore'}}));
}
