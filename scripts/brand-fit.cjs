const fs=require('node:fs'),path=require('node:path');
const root=process.argv[2]||'.';
const rows=JSON.parse(fs.readFileSync(path.join(__dirname,'brand-fit.json'),'utf8'));
for(const row of rows){const file=path.join(root,row.file);let html=fs.readFileSync(file,'utf8');
 html=html.replace(/<!-- brand-fit:start -->[\s\S]*?<!-- brand-fit:end -->/g,'');
 const block='<!-- brand-fit:start --><section id="brand-fit"><h2>'+row.heading+'</h2>'+row.body+'</section><!-- brand-fit:end -->';
 if(!html.includes(row.anchor))throw Error('Missing content anchor '+row.file);
 html=html.replace(row.anchor,row.anchor+block);fs.writeFileSync(file,html);
 console.log('Updated brand fit: '+row.file);
}
