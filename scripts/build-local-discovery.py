"""Build the two-studio visitor directory from existing location information."""
from pathlib import Path
import html, json, re, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
D='https://www.craftcollectivesalongroup.com'
DATE='2026-10-25'
template=(R/'guides/first-salon-visit-checklist-pittsburgh/index.html').read_text()
records=[]
def a(path,label): return f'<a href="{path}">{html.escape(label)}</a>'
def p(text): return '<p>'+text+'</p>'
def section(title,body): return '<h2>'+html.escape(title)+'</h2>'+body
def ul(items): return '<ul>'+''.join('<li>'+x+'</li>' for x in items)+'</ul>'
def publish(slug,title,desc,body):
    url=D+'/locations'
    s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',template,flags=re.S)
    for kind,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('property','og:url',url)]:
        s=re.sub(r'(<meta '+kind+'="'+key+r'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],s)
    s=re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m[1]+url+m[2],s)
    s=re.sub(r'<header class="archive-hero">.*?</header>','<header class="archive-hero"><p>'+a('/','Home')+' / '+a('/locations','Locations')+'</p><h1>'+html.escape(title.split(' | ')[0])+'</h1><p class="archive-meta">Craft Collective Salon Group · October 25, 2026</p></header>',s,flags=re.S)
    cta='<aside class="archive-cta"><h2>Find your next Craft appointment</h2>'+p('Explore '+a('/meet-the-team','our stylists')+', '+a('/hair-salon-gallery-pittsburgh','our work')+' and '+a('/hair-services-pittsburgh','services')+'. Book online for North Hills, or call 724-514-7231 for help with either location. Canonsburg is by appointment only.')+p(a('/book','View booking options'))+'</aside>'
    s=re.sub(r'<article class="archive-body">.*?</article>','<article class="archive-body">'+body+cta+'</article>',s,flags=re.S)
    schema={'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'datePublished':DATE,'dateModified':DATE,'mainEntityOfPage':url,'author':{'@type':'Organization','name':'Craft Collective Salon Group','url':D},'publisher':{'@type':'Organization','name':'Craft Collective Salon Group','url':D}}
    s=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>',s,flags=re.S)
    f=R/'locations'/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s)
    records.append({'path':'/locations','title':title,'description':desc})

def table(caption,heads,rows):
    return '<div class="comparison-scroll" role="region" aria-label="'+html.escape(caption)+'" tabindex="0"><table><caption>'+html.escape(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+html.escape(h)+'</th>' for h in heads)+'</tr></thead><tbody>'+''.join('<tr><th scope="row">'+html.escape(row[0])+'</th>'+''.join('<td>'+html.escape(v)+'</td>' for v in row[1:])+'</tr>' for row in rows)+'</tbody></table></div>'
from urllib.parse import urlencode
studios=[{'slug':'north-hills-pittsburgh','name':'North Hills, Pittsburgh','street':'2014D Babcock Blvd','city':'Pittsburgh','zip':'15209','image':'salon-color-bar-640x480.jpg','booking':'Online booking available; call for help choosing a service.','detail':'Review the North Hills location page for published hours. Monday has limited staff; call ahead for a particular artist.'},{'slug':'canonsburg','name':'Canonsburg','street':'115 W Pike St','city':'Canonsburg','zip':'15317','image':'canonsburg-front-room-640x480.jpg','booking':'By appointment only. Call 724-514-7231 to schedule.','detail':'Confirm the artist and appointment time before traveling. North Hills online availability does not represent the Canonsburg schedule.'}]
body=p('Choose the Craft Collective studio you will visit before reserving your service. We have two physical locations: North Hills Pittsburgh and Canonsburg. Our nearby-area guides help guests plan a visit; they are not additional storefronts.')+'<div class="studio-grid">'
for studio in studios:
 address=studio['street']+', '+studio['city']+', PA '+studio['zip'];directions='https://www.google.com/maps/dir/?'+urlencode({'api':'1','destination':address})
 body+='<section class="studio-card"><img src="/images/'+studio['image']+'" alt="Inside Craft Collective’s '+studio['name']+' studio" width="640" height="480" loading="lazy" decoding="async"><h2>'+studio['name']+'</h2><address>'+studio['street']+'<br>'+studio['city']+', PA '+studio['zip']+'</address>'+p(studio['booking'])+p(studio['detail'])+p(a('/locations/'+studio['slug'],'View studio details')+' · '+a(directions,'Get directions'))+p(a('https://phorest.com/book/salons/craftcollectivesalongroup','Book North Hills online') if studio['slug']=='north-hills-pittsburgh' else a('tel:+17245147231','Call for Canonsburg appointments'))+'</section>'
body+='</div>'
body+=section('Confirm these details before your visit',ul(['The studio address on your reservation.','The artist and the service you are booking.','Whether consultation, toner, cutting and finishing are included.','The complete estimate, appointment duration and preparation instructions.']))
body+=section('Choosing between the studios',p('Start with where your selected artist works and the appointment you need. Check the route from your actual starting point, then allow time for the complete service. If you are unsure about availability or where to book, call '+a('tel:+17245147231','724-514-7231')+' before selecting a service.')+p('For a substantial color change, new extensions or an unfamiliar booking label, explain your starting hair and goal first. The team can help identify which consultation or reservation fits.'))
body+=section('Plan the service and budget',p('Browse '+a('/hair-services-pittsburgh','the service menu')+', '+a('/meet-the-team','our artists')+' and '+a('/hair-salon-gallery-pittsburgh','our work')+'. The '+a('/pricing/craft-collective','Craft pricing guide')+' separates published amounts from services requiring an individual quote. Use the '+a('/guides/first-salon-visit-checklist-pittsburgh','first-visit checklist')+' when preparing for a new artist.'))
publish('','Craft Collective Locations: North Hills & Canonsburg','Choose Craft Collective’s North Hills Pittsburgh or Canonsburg studio. Get directions, confirm your appointment location and find the right booking option.',body)
f=R/'locations/index.html';s=f.read_text().replace('</head>','<link rel="stylesheet" href="/assets/studio-directory.css"></head>')
schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Craft Collective salon locations','url':D+'/locations','dateModified':DATE,'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':x['name'],'url':D+'/locations/'+x['slug']} for i,x in enumerate(studios)]}}
s=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda _: '<script type="application/ld+json">'+json.dumps(schema)+'</script>',s,flags=re.S);f.write_text(s)
# Each storefront gets its own entity, without assigning the group's reviews to a branch.
for x in studios:
 f=R/'locations'/x['slug']/'index.html';s=f.read_text();s=re.sub(r'<!-- cc:studio-schema -->.*?<!-- /cc:studio-schema -->','',s,flags=re.S)
 address=x['street']+', '+x['city']+', PA '+x['zip']
 entity={'@context':'https://schema.org','@type':'HairSalon','@id':D+'/locations/'+x['slug']+'#salon','name':'Craft Collective Salon Group — '+x['name'],'url':D+'/locations/'+x['slug'],'telephone':'+17245147231','parentOrganization':{'@id':D+'/#organization'},'address':{'@type':'PostalAddress','streetAddress':x['street'],'addressLocality':x['city'],'addressRegion':'PA','postalCode':x['zip'],'addressCountry':'US'},'image':D+'/images/'+x['image'],'hasMap':'https://www.google.com/maps/search/?'+urlencode({'api':'1','query':address})}
 if x['slug']=='canonsburg':entity['description']='Craft Collective Canonsburg studio. Visits are by appointment; call to confirm the stylist and schedule.';s=s.replace('<meta name="geo.placename" content="Pittsburgh"','<meta name="geo.placename" content="Canonsburg"')
 block='<!-- cc:studio-schema --><script type="application/ld+json">'+json.dumps(entity)+'</script><!-- /cc:studio-schema -->';s=s.replace('</head>',block+'</head>',1)
 nav='<!-- cc:studio-navigation --><section class="archive-body"><h2>Confirm your studio and route</h2>'+p(a('/locations','Compare both Craft locations')+' · '+a('https://www.google.com/maps/dir/?'+urlencode({'api':'1','destination':address}),'Get directions to this studio'))+'</section><!-- /cc:studio-navigation -->'
 s=re.sub(r'<!-- cc:studio-navigation -->.*?<!-- /cc:studio-navigation -->','',s,flags=re.S)
 s=s.replace('<footer',nav+'<footer',1);f.write_text(s)
# Put the location choice before the online widget; retain the existing booking system.
f=R/'book/index.html';s=f.read_text();s=re.sub(r'<!-- cc:booking-location-choice -->.*?<!-- /cc:booking-location-choice -->','',s,flags=re.S)
s=s.replace('<div class="location-card">','<div class="location-card" id="north-hills-booking">',1)
start=s.index('id="north-hills-booking"');i=s.find('<div class="location-card">',start)
if i!=-1:s=s[:i]+s[i:].replace('<div class="location-card">','<div class="location-card" id="canonsburg-booking">',1)
block='<!-- cc:booking-location-choice --><section class="archive-body" aria-labelledby="booking-studio-choice"><h2 id="booking-studio-choice">Which studio are you booking?</h2>'+p('The online booking window below is for North Hills. For Canonsburg, '+a('tel:+17245147231','call 724-514-7231')+' to confirm the appointment.')+p(a('#north-hills-booking','North Hills address and hours')+' · '+a('#canonsburg-booking','Canonsburg appointment details')+' · '+a('/locations','Compare both studios'))+'</section><!-- /cc:booking-location-choice -->'
s=s.replace('<!-- PHOREST BOOKING EMBED -->',block+'<!-- PHOREST BOOKING EMBED -->',1);assert block in s;f.write_text(s)
# Add the visitor directory to the existing sitemap.
NS='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',NS);f=R/'site-pages-sitemap.xml';t=ET.parse(f);rt=t.getroot()
if D+'/locations' not in [n.text for n in rt.findall('.//{'+NS+'}loc')]:
 n=ET.SubElement(rt,'{'+NS+'}url');ET.SubElement(n,'{'+NS+'}loc').text=D+'/locations';ET.SubElement(n,'{'+NS+'}lastmod').text=DATE
for n in rt:
 loc=n.find('{'+NS+'}loc')
 if loc is not None and loc.text in [D+'/book',D+'/locations/north-hills-pittsburgh',D+'/locations/canonsburg']:
  lm=n.find('{'+NS+'}lastmod')
  if lm is None:lm=ET.SubElement(n,'{'+NS+'}lastmod')
  lm.text=DATE
t.write(f,encoding='UTF-8',xml_declaration=True)
print('Built two-studio visitor directory, branch schemas and booking-location choice.')
