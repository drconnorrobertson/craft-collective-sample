(() => {
  const form=document.getElementById('salon-directory-filter');
  if(!form)return;
  const search=document.getElementById('salon-search');
  const items=[...document.querySelectorAll('#salon-directory > li')];
  const count=document.getElementById('salon-count');
  const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const filter=()=>{
    const terms=normalize(search.value).split(/\s+/).filter(Boolean);
    let visible=0;
    for(const item of items){item.hidden=!terms.every(t=>normalize(item.textContent).includes(t));if(!item.hidden)visible++;}
    count.textContent=`${visible} of ${items.length} salon comparisons shown. Alphabetical, not ranked.`;
    document.getElementById('salon-empty').hidden=visible!==0;
  };
  form.addEventListener('submit',e=>e.preventDefault());
  search.addEventListener('input',filter);
  form.addEventListener('reset',()=>{search.value='';filter();});
})();
