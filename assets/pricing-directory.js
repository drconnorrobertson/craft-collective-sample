(() => {
 const form=document.getElementById('pricing-filter');
 if(!form)return;
 const search=document.getElementById('pricing-search');
 const items=[...document.querySelectorAll('#pricing-list > li')];
 const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
 function filter(){
  const terms=clean(search.value).split(/\s+/).filter(Boolean);
  let count=0;
  for(const item of items){item.hidden=!terms.every(term=>clean(item.textContent).includes(term));if(!item.hidden)count++;}
  document.getElementById('pricing-count').textContent=`${count} of ${items.length} pricing guides shown. Alphabetical, not ranked.`;
  document.getElementById('pricing-empty').hidden=count!==0;
 }
 search.addEventListener('input',filter);
 form.addEventListener('submit',event=>event.preventDefault());
 form.addEventListener('reset',()=>{search.value='';filter();});
})();
