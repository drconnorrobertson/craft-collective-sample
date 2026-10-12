import fs from 'node:fs';
import path from 'node:path';

// Existing articles with demonstrated Search Console traffic, September 2026.
const routes = [
 ['why-your-hair-feels-thinner-even-when-you-haven-t-lost-density-and-how-to-restore-fullness','cuts','Hair feels thinner: shape and fullness'],
 ['why-your-hair-looks-healthier-right-after-a-trim-and-how-to-keep-that-freshly-cut-look-longer','cuts','Keeping a freshly trimmed shape'],
 ['why-your-hair-looks-different-after-you-sleep-and-how-to-fix-morning-texture','styling','Refreshing hair after sleep'],
 ['why-your-hair-color-fades-faster-at-the-ends-and-how-to-maintain-even-tone-from-root-to-tip','color','Uneven color fading from roots to ends'],
];
const esc = s => s.replaceAll('&','&amp;').replaceAll('"','&quot;');
export function buildSearchPathways(out) {
 const groups = new Map();
 for (const [slug,topic,label] of routes) {
  const file = path.join(out,'post',slug,'index.html');
  const route = '/pittsburgh-hair-guide/'+topic;
  if (!fs.existsSync(path.join(out,route,'index.html'))) throw Error('Missing topic '+route);
  let html=fs.readFileSync(file,'utf8').replace(/<!-- search-pathways -->.*?<!-- \/search-pathways -->/gs,'');
  const block=`<!-- search-pathways --><section><h2>Keep exploring your hair question</h2><p><a href="${route}">Browse ${topic} questions and appointment guides</a>, or read <a href="/post/why-your-hair-looks-flat-at-the-roots-but-puffy-at-the-ends">why roots look flat while ends look puffy</a> to compare shape and styling concerns.</p></section><!-- /search-pathways -->`;
  if (!html.includes('</article>')) throw Error('Missing article '+slug);
  fs.writeFileSync(file,html.replace('</article>',block+'</article>'));
  if(!groups.has(topic))groups.set(topic,[]);
  groups.get(topic).push([slug,label]);
 }
 for(const [topic,items] of groups){
  const file=path.join(out,'pittsburgh-hair-guide',topic,'index.html');
  let html=fs.readFileSync(file,'utf8').replace(/<!-- search-pathways -->.*?<!-- \/search-pathways -->/gs,'');
  const block=`<!-- search-pathways --><section><h2>More practical reading</h2><ul>${items.map(([slug,label])=>`<li><a href="/post/${slug}">${esc(label)}</a></li>`).join('')}</ul></section><!-- /search-pathways -->`;
  if (!html.includes('</article>')) throw Error('Missing hub article '+topic);
  fs.writeFileSync(file,html.replace('</article>',block+'</article>'));
 }
 // Replace the legacy empty Wix sitemap still registered in Search Console.
 const categories=['/blog','/pittsburgh-hair-guide',...['care','cuts','styling','color','extensions','treatments','comparisons','salons'].map(x=>'/pittsburgh-hair-guide/'+x)];
 fs.writeFileSync(path.join(out,'blog-categories-sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+categories.map(route=>`<url><loc>https://www.craftcollectivesalongroup.com${route}</loc></url>`).join('')+'</urlset>');
 console.log('Search pathways: 4 existing articles, 3 topic hubs; repaired empty category sitemap');
}
