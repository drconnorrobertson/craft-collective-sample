// Regression checks for user-entered quote arithmetic; no salon prices are supplied.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const values=new Map();
const output={textContent:''};
const handlers={};
const form={elements:{namedItem:key=>({value:values.get(key)??''})},addEventListener:(name,fn)=>{handlers[name]=fn;}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/salon-quote-comparison.js'),'utf8'),{document:{getElementById:id=>id==='quote-comparison'?form:output},Intl,Number,Error});
function submit(data){values.clear();for(const [key,value] of Object.entries(data))values.set(key,String(value));handlers.submit({preventDefault(){}});return output.textContent;}
const complete={'a-initial':200,'a-follow':75,'a-count':3,'a-required':25,'b-initial':180,'b-follow':90,'b-count':3,'b-required':0};
assert.match(submit({}),/required costs still unknown/);
assert.doesNotMatch(output.textContent,/totals are equal/);
assert.match(submit(complete),/Option A: \$450\.00/);
assert.match(output.textContent,/totals are equal/);
assert.match(submit({...complete,'b-required':20}),/differ by \$20\.00/);
assert.match(submit({'a-initial':0,'a-count':0,'a-required':0,'b-initial':0,'b-count':0,'b-required':0}),/totals are equal/);
assert.match(submit({...complete,'a-count':1.5}),/whole number/);
assert.match(submit({...complete,'a-required':-1}),/zero or more/);
assert.match(submit({...complete,'a-initial':'Infinity'}),/finite amounts/);
assert.match(submit({...complete,'a-initial':1e100}),/too large/);
handlers.reset();assert.match(output.textContent,/Enter the quotes/);
console.log('Quote worksheet passed: unknown costs, full totals, differences, zero visits, fractional counts, negatives, nonfinite/oversized amounts and reset.');
