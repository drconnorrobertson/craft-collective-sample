import {searchSite,normalize} from './site-search-core.mjs';
const form=document.getElementById('site-search'),field=document.getElementById('site-search-query'),filter=document.getElementById('site-search-category'),list=document.getElementById('site-search-results'),status=document.getElementById('site-search-status');
let request,version=0,timer;
const labels={services:'Service',pricing:'Pricing',locations:'Location',artists:'Stylist',guides:'Guide',articles:'Article'};
function writeUrl(){const url=new URL(location.href);if(field.value.trim())url.searchParams.set('q',field.value.trim());else url.searchParams.delete('q');if(filter.value!=='all')url.searchParams.set('type',filter.value);else url.searchParams.delete('type');history.replaceState(null,'',url);}
async function update(){
 const current=++version;list.replaceChildren();writeUrl();
 const query=field.value.trim();
 if(query.length<2||!normalize(query)){status.textContent='Enter a service, stylist, price question or location. You can also browse the links below.';return;}
 status.textContent='Searching Craft Collective…';
 try{
  request??=fetch(form.dataset.index).then(response=>{if(!response.ok)throw Error('Unavailable');return response.json();});
  const records=await request;if(current!==version)return;
  const {total,results}=searchSite(records,query,{category:filter.value,limit:30});
  status.textContent=total?`${total} matches. Showing ${results.length}.`:'No matches. Try a shorter phrase, choose All topics, or browse below.';
  for(const result of results){
   const li=document.createElement('li'),link=document.createElement('a'),tag=document.createElement('span'),description=document.createElement('p');
   link.href=result.path;link.textContent=result.title;tag.className='search-result-type';tag.textContent=labels[result.category]||'Page';description.textContent=result.description;
   li.append(tag,link,description);list.append(li);
  }
 }catch{if(current!==version)return;request=undefined;status.textContent='Search is temporarily unavailable. Use the directory links below or call 724-514-7231 for help.';}
}
form.addEventListener('submit',event=>{event.preventDefault();clearTimeout(timer);update();});
field.addEventListener('input',()=>{version++;clearTimeout(timer);timer=setTimeout(update,160);});
filter.addEventListener('change',()=>{clearTimeout(timer);update();});
form.addEventListener('reset',()=>{version++;clearTimeout(timer);field.value='';filter.value='all';update();});
window.addEventListener('popstate',()=>{const params=new URLSearchParams(location.search);field.value=params.get('q')||'';filter.value=[...filter.options].some(o=>o.value===params.get('type'))?params.get('type'):'all';update();});
const params=new URLSearchParams(location.search);field.value=params.get('q')||'';if([...filter.options].some(o=>o.value===params.get('type')))filter.value=params.get('type');update();
