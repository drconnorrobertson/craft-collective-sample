import {normalize,searchGuides} from './hair-guide-search.mjs';
const field=document.getElementById('guide-search');
const results=document.getElementById('guide-results');
const status=document.getElementById('guide-status');
let dataPromise,version=0,timer;
function updateUrl(value){
 const url=new URL(location.href);
 if(value)url.searchParams.set('q',value);else url.searchParams.delete('q');
 history.replaceState(null,'',url);
}
async function search(){
 const current=++version,q=field.value.trim();results.replaceChildren();updateUrl(q);
 if(q.length<2||!normalize(q)){status.textContent='Enter a service or question, such as gray blending, extension cost or bridal hair.';return;}
 status.textContent='Finding guides…';
 try{
  dataPromise??=fetch('/pittsburgh-hair-guide/search-index.json').then(r=>{if(!r.ok)throw Error('Search unavailable');return r.json();});
  const data=await dataPromise;if(current!==version)return;
  const matches=searchGuides(data,q);
  status.textContent=matches.length?`${matches.length} matching guides. Showing ${Math.min(matches.length,40)}.`:'No matching guides. Try a service name, or browse the topics below.';
  for(const x of matches.slice(0,40)){
   const li=document.createElement('li'),a=document.createElement('a');a.href=x.path;a.textContent=x.title;li.append(a);results.append(li);
  }
 }catch{
  if(current!==version)return;dataPromise=undefined;status.textContent='Search is unavailable. Please use the topic links below.';
 }
}
field.addEventListener('input',()=>{version++;clearTimeout(timer);timer=setTimeout(search,180);});
field.value=new URL(location.href).searchParams.get('q')||'';
search();
