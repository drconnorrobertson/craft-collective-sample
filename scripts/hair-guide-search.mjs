const aliases={grey:'gray',colour:'color',colours:'color',colors:'color',prices:'cost',price:'cost',pricing:'cost',quotes:'cost',quote:'cost',estimates:'cost',estimate:'cost',inexpensive:'affordable',budget:'affordable',curls:'curly',cuts:'haircut',cut:'haircut',haircuts:'haircut',extensions:'extension',highlights:'highlight',wedding:'bridal',weddings:'bridal',children:'kids',child:'kids',late:'evening',comparisons:'compare',comparison:'compare',versus:'compare',vs:'compare'};
const stop=new Set(['the','a','an','and','or','for','in','of','to','at','with','near','me','hair','salon','salons']);
export function normalize(query){
 return String(query).toLowerCase().replace(/[’']/g,'').replace(/[^a-z0-9]+/g,' ').trim().split(/\s+/).filter(Boolean).map(w=>aliases[w]||w).filter(w=>!stop.has(w)).join(' ');
}
export function searchGuides(records,query){
 const q=normalize(query);if(!q)return [];
 const terms=[...new Set(q.split(' '))];
 const scored=[];
 for(const r of records){
  const title=normalize(r.title),primary=normalize(r.primaryKeyword||''),related=normalize((r.relatedKeywords||[]).join(' '));
  const all=(title+' '+primary+' '+related).split(' ');
  if(!terms.every(t=>all.some(w=>w===t||w.startsWith(t))))continue;
  let score=Number(r.priority||0);
  for(const t of terms)score+=title.split(' ').some(w=>w===t)?10:primary.split(' ').includes(t)?5:2;
  if(title.includes(q))score+=20;
  scored.push({record:r,score});
 }
 return scored.sort((a,b)=>b.score-a.score||a.record.title.localeCompare(b.record.title)).map(x=>x.record);
}
