// Apply reviewed Search Console improvements after other renderers.
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
export const config=JSON.parse(readFileSync(new URL('./search-intent-config.json',import.meta.url),'utf8'));
const esc=s=>s.replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
export function optimizeSearchIntent(html,path){
 const c=config[path];if(!c)return html;
 if(c.title){html=html.replace(/<title>[\s\S]*?<\/title>/i,()=>'<title>'+esc(c.title)+'</title>');}
 for(const [key,value] of [['description',c.description],['og:title',c.title],['twitter:title',c.title],['og:description',c.description],['twitter:description',c.description]]){
  if(!value)continue;
  const re=new RegExp('<meta\\s+(?:name|property)="'+key+'"\\s+content="[^"]*"\\s*/?>','i');
  const tag='<meta '+(key.startsWith('og:')?'property':'name')+'="'+key+'" content="'+esc(value)+'">';
  html=re.test(html)?html.replace(re,()=>tag):html.replace('</head>',()=>tag+'\n</head>');
 }
 if(c.h1)html=html.replace(/(<h1\b[^>]*>)[\s\S]*?(<\/h1>)/i,(_,a,b)=>a+esc(c.h1)+b);
 if(c.body){
  const marker=/<!-- search-intent:start -->[\s\S]*?<!-- search-intent:end -->/;
  const block='<!-- search-intent:start --><section class="content-section section" style="max-width:1100px;margin:40px auto;padding:0 24px"><div class="container narrow wrap"><h2>'+esc(c.heading)+'</h2>'+c.body+'</div></section><!-- search-intent:end -->';
  html=marker.test(html)?html.replace(marker,()=>block):html.includes('</main>')?html.replace('</main>',()=>block+'\n</main>'):html.replace(/<footer\b/i,()=>block+'\n<footer');
 }
 return html;
}
if(process.argv.includes('--write'))for(const path of Object.keys(config)){
 const file=root+(process.argv.includes('--public')?'public/':process.argv.includes('--dist')?'dist/':'')+path;const html=readFileSync(file,'utf8');writeFileSync(file,optimizeSearchIntent(html,path));
}
