const aliases={grey:'gray',headspace:'head space',northhills:'north hills',blowouts:'blowout',treatments:'treatment',colour:'color',colours:'color',prices:'price',pricing:'price',cost:'price',costs:'price',quotes:'price',quote:'price',estimates:'price',estimate:'price',cuts:'haircut',cut:'haircut',haircuts:'haircut',curls:'curly',extensions:'extension',highlights:'highlight',weddings:'bridal',wedding:'bridal',children:'child',kids:'child',stylists:'stylist',artists:'stylist',artist:'stylist',directions:'location',locations:'location',studios:'location',studio:'location',appointments:'book',appointment:'book',booking:'book',schedule:'book',comparisons:'compare',comparison:'compare',versus:'compare',vs:'compare'};
const stop=new Set(['the','a','an','and','or','for','in','of','to','at','with','near','me','salon','salons','craft','collective']);
export function normalize(query){return String(query).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\bblow[\s-]?dry\b/g,'blowout').replace(/[’']/g,'').replace(/[^a-z0-9]+/g,' ').trim().split(/\s+/).filter(Boolean).map(x=>aliases[x]||x).filter(x=>!stop.has(x)).join(' ');}
export function searchSite(records,query,{category='all',limit=30}={}){
 const q=normalize(query);if(!q)return {total:0,results:[]};
 const terms=[...new Set(q.split(' '))],scored=[];
 for(const record of records){
  if(category!=='all'&&record.category!==category)continue;
  const title=normalize(record.title),words=title.split(' '),all=normalize(title+' '+record.description+' '+(record.keywords||'')).split(' ');
  if(!terms.every(term=>all.some(word=>word===term||word.startsWith(term))))continue;
  let score=Number(record.priority||0);
  for(const term of terms)score+=words.includes(term)?25:words.some(word=>word.startsWith(term))?12:3;
  if(title===q)score+=100;else if(title.includes(q))score+=35;
  scored.push({record,score});
 }
 scored.sort((a,b)=>b.score-a.score||a.record.title.localeCompare(b.record.title)||a.record.path.localeCompare(b.record.path));
 return {total:scored.length,results:scored.slice(0,Math.max(0,Math.min(limit,100))).map(x=>x.record)};
}
