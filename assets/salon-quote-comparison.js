(() => {
  const form=document.getElementById('quote-comparison');
  if(!form)return;
  const output=document.getElementById('quote-result');
  const money=new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'});
  function read(key){
    const values=['initial','follow','count','required'].map(field=>form.elements.namedItem(`${key}-${field}`));
    const nums=values.map(input=>input.value.trim()===''?null:Number(input.value));
    if(nums.some(n=>n!==null&&(!Number.isFinite(n)||n<0)))throw Error('Enter finite amounts of zero or more.');
    if(nums[2]!==null&&!Number.isInteger(nums[2]))throw Error('The number of follow-up visits must be a whole number.');
    const [initial,follow,count,required]=nums;
    const total=(initial??0)+(follow??0)*(count??0)+(required??0);
    if(!Number.isFinite(total)||total>Number.MAX_SAFE_INTEGER)throw Error('The entered total is too large. Check the amounts.');
    const complete=initial!==null&&required!==null&&(count===0||(follow!==null&&count!==null));
    const name=form.elements.namedItem(`${key}-name`).value.trim()||`Option ${key.toUpperCase()}`;
    return {name,total,complete};
  }
  form.addEventListener('submit',event=>{
    event.preventDefault();
    try{
      const a=read('a'),b=read('b');
      const lines=[a,b].map(x=>`${x.name}: ${money.format(x.total)} ${x.complete?'estimated total for your chosen period':'subtotal from entered amounts — required costs still unknown'}.`);
      if(a.complete&&b.complete){const difference=Math.abs(a.total-b.total);lines.push(difference===0?'The entered totals are equal.':`The entered totals differ by ${money.format(difference)}. Compare the included work and upkeep before choosing.`);}
      else lines.push('Complete the missing costs, including an explicit zero where none apply, before comparing full totals.');
      output.textContent=lines.join('\n');
    }catch(error){output.textContent=error.message;}
  });
  form.addEventListener('reset',()=>{output.textContent='Enter the quotes and choose Compare to see the totals.';});
})();
