"""Apply user-confirmed roster changes without inventing staff details."""
from pathlib import Path
import re,json,subprocess,html
R=Path(__file__).resolve().parents[1]
tracked=subprocess.check_output(['git','ls-files'],cwd=R,text=True).splitlines()
for name in tracked:
    f=R/name
    if f==Path(__file__).resolve() or f.suffix not in {'.html','.py','.json','.md'} or not f.exists():continue
    s=f.read_text();new=s
    new=re.sub(r'Olivia([\s\u00a0]+)Spearl',r'Olivia\1Sperl',new)
    new=new.replace('Delilah','Delila')
    new=re.sub(r'Ha[\s\u00a0]+Na', 'Hana',new)
    if new!=s:f.write_text(new)

f=R/'meet-the-team/index.html';s=f.read_text()
def card(name,role,anchor,book=False):
    initials=''.join(part[0] for part in name.split())
    return '<div class="team-card" id="'+anchor+'"><div class="team-card-monogram" aria-hidden="true">'+initials+'</div><div class="team-card-content"><h3 class="team-card-name">'+html.escape(name)+'</h3><p class="team-card-role">'+role+'</p>'+('<a class="link-arrow" href="/book">Check booking options &rarr;</a>' if book else '')+'</div></div>'
s=re.sub(r'<!-- cc:newstylist -->.*?<!-- /cc:newstylist -->','',s,flags=re.S)
s=re.sub(r'<!-- cc:assistants -->.*?<!-- /cc:assistants -->','',s,flags=re.S)
hair_marker='<h3 class="section-label team-group">Hair</h3>\n    <div class="team-grid">'
assert hair_marker in s
s=s.replace(hair_marker,hair_marker+'<!-- cc:newstylist -->'+card('Kyra Poskey','Stylist','kyra-poskey',True)+'<!-- /cc:newstylist -->',1)
assistants='<h3 class="section-label team-group" id="assistants-heading">Assistants</h3><div class="team-grid">'+''.join(card(n,'Assistant',n.lower()) for n in ['Kaylan','Ella','Luc'])+'</div>'
marker='  </section>\n\n  <!-- PHILOSOPHY -->';assert marker in s
s=s.replace(marker,'<!-- cc:assistants -->'+assistants+'<!-- /cc:assistants -->\n'+marker,1)
new_names=[('Kyra Poskey','Stylist','kyra-poskey'),('Kaylan','Assistant','kaylan'),('Ella','Assistant','ella'),('Luc','Assistant','luc')]
def schema_update(m):
    data=json.loads(m[1])
    if not isinstance(data,dict) or data.get('@type')!='ItemList':return m[0]
    items=data.get('itemListElement',[])
    items=[i for i in items if i.get('item',{}).get('name') not in {n for n,_,_ in new_names}]
    for name,role,anchor in new_names:
        items.append({'@type':'ListItem','position':len(items)+1,'item':{'@type':'Person','name':name,'jobTitle':role,'worksFor':{'@id':'https://www.craftcollectivesalongroup.com/#organization'},'url':'https://www.craftcollectivesalongroup.com/meet-the-team#'+anchor}})
    data['itemListElement']=items;data['numberOfItems']=len(items)
    return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema_update,s,flags=re.S)
style='<style id="team-roster-oct2026">.team-card-monogram{aspect-ratio:1;display:grid;place-items:center;background:#ede9e1;color:#765329;font-family:Georgia,serif;font-size:3.5rem;letter-spacing:.08em}.team-card:target{outline:3px solid #b89a6a;outline-offset:4px;scroll-margin-top:100px}</style>'
s=re.sub(r'<style id="team-roster-oct2026">.*?</style>','',s,flags=re.S)
s=s.replace('</head>',style+'</head>',1);f.write_text(s)
print('Corrected Olivia Sperl, Delila Keller and Hana Ko across published content; added Kyra Poskey, Kaylan, Ella and Luc to roster and Person schema.')
