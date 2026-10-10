import fs from 'node:fs';
import path from 'node:path';
export function buildBuyerIntent(out) {
 const targets=[
 ['the-best-salons-in-pittsburgh-for-curly-hair-and-textured-hair','Plan your curly hair appointment in North Hills','curly-haircuts','Curly haircut and consultation details'],
 ['the-best-men-s-hair-salons-and-grooming-options-in-pittsburgh','Plan your men’s haircut in North Hills','mens-grooming','Men’s haircut and grooming details'],
 ['gray-blending-dimensional-coverage-in-north-hills-natural-confidence-by-craft-collective-salon-gr','Plan your gray blending appointment in North Hills','gray-blending','Gray blending and consultation details']
 ];
 for(const [slug,title,service,label] of targets){
 const file=path.join(out,'post',slug,'index.html');
 if(!fs.existsSync(file))throw Error('Missing buyer intent article: '+slug);
 let html=fs.readFileSync(file,'utf8');
 const block=`<!-- cc:buyer-intent --><aside class="archive-cta" aria-label="Appointment planning"><h2>${title}</h2><p><a href="/services/${service}-pittsburgh">${label}</a>. Have a stylist you already see? Continue with your usual Phorest booking.</p><p><a class="btn-primary" href="https://phorest.com/book/salons/craftcollectivesalongroup" target="_blank" rel="noopener noreferrer">Check North Hills availability</a></p><p>New client or unsure which service or stylist to select? Call <a href="tel:+17245147231">724-514-7231</a> for help matching your goals and confirming the price, appointment length and preparation. Bring inspiration photos and describe your current hair and routine.</p><p>North Hills: 2014D Babcock Blvd, Pittsburgh. Canonsburg: 115 W Pike St; call to schedule.</p></aside><!-- /cc:buyer-intent -->`;
 html=html.replace(/<!-- cc:buyer-intent -->[\s\S]*?<!-- \/cc:buyer-intent -->/g,'');
 html=html.replace(/(<article\b[^>]*>)/,`$1${block}`).replace('</article>',`${block}</article>`);
 fs.writeFileSync(file,html);
 }
 console.log('Buyer intent: booking sections added to 3 existing articles.');
}
