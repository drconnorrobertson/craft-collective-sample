"""Build source-linked salon pricing pages, a directory and service-price comparisons."""
from pathlib import Path
import html, json, re, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
D='https://www.craftcollectivesalongroup.com'
DATE='2026-10-24'
template=(R/'guides/first-salon-visit-checklist-pittsburgh/index.html').read_text()
records=[]
def a(path,label): return f'<a href="{path}">{html.escape(label)}</a>'
def p(text): return '<p>'+text+'</p>'
def section(title,body): return '<h2>'+html.escape(title)+'</h2>'+body
def ul(items): return '<ul>'+''.join('<li>'+x+'</li>' for x in items)+'</ul>'
def publish(slug,title,desc,body):
    url=D+'/pricing'+('/'+slug if slug else '')
    s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',template,flags=re.S)
    for kind,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('property','og:url',url)]:
        s=re.sub(r'(<meta '+kind+'="'+key+r'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],s)
    s=re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m[1]+url+m[2],s)
    s=re.sub(r'<header class="archive-hero">.*?</header>','<header class="archive-hero"><p>'+a('/','Home')+' / '+a('/pricing','Salon pricing')+'</p><h1>'+html.escape(title.split(' | ')[0])+'</h1><p class="archive-meta">Craft Collective Salon Group · October 24, 2026</p></header>',s,flags=re.S)
    cta='<aside class="archive-cta"><h2>Find your next Craft appointment</h2>'+p('Explore '+a('/meet-the-team','our stylists')+', '+a('/hair-salon-gallery-pittsburgh','our work')+' and '+a('/hair-services-pittsburgh','services')+'. Book online for North Hills, or call 724-514-7231 for help with either location. Canonsburg is by appointment only.')+p(a('/book','View booking options'))+'</aside>'
    s=re.sub(r'<article class="archive-body">.*?</article>','<article class="archive-body">'+body+cta+'</article>',s,flags=re.S)
    schema={'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'datePublished':DATE,'dateModified':DATE,'mainEntityOfPage':url,'author':{'@type':'Organization','name':'Craft Collective Salon Group','url':D},'publisher':{'@type':'Organization','name':'Craft Collective Salon Group','url':D}}
    s=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>',s,flags=re.S)
    f=R/'pricing'/slug/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s)
    records.append({'path':'/pricing'+('/'+slug if slug else ''),'title':title,'description':desc})

def table(caption,heads,rows):
    return '<div class="comparison-scroll" role="region" aria-label="'+html.escape(caption)+'" tabindex="0"><table><caption>'+html.escape(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+html.escape(h)+'</th>' for h in heads)+'</tr></thead><tbody>'+''.join('<tr><th scope="row">'+html.escape(row[0])+'</th>'+''.join('<td>'+html.escape(v)+'</td>' for v in row[1:])+'</tr>' for row in rows)+'</tbody></table></div>'
research=json.loads((R/'scripts/pricing-research.json').read_text())
salons=research['salons']
assert len(salons)==20

def pricing_links():
    return section('Continue your comparison',ul([a('/pricing','Browse the salon pricing directory'),a('/pricing/craft-collective','Craft Collective prices and estimates'),a('/guides/salon-quote-comparison-tool','Compare two complete quotes'),a('/guides/pittsburgh-salon-alternatives','Explore salon alternatives')]))

for c in salons:
    title=c['name']+' Pricing: Published Menu & Cost Guide'
    body=p('Searching for '+html.escape(c['name'])+' prices near '+html.escape(c['area'])+'? Use the published examples below to identify the right questions for your appointment. The exact service label, artist level and included finish matter as much as the number beside the service.')
    body+=p('This guide is published by Craft Collective Salon Group. Source reviewed October 24, 2026: '+a(c['source'],c['name']+' official menu or business booking page')+'. Amounts describe that source, not a guaranteed quote. We have not independently ranked the salon or established that Craft costs less.')
    body+=section('Published menu examples',table(c['name']+' selected pricing',['Menu item','Published amount or status','Scope to confirm'],[(row[1],row[2],row[3]) for row in c['rows']]))
    body+=p('Pricing structure: '+html.escape(c['model'])+'. “Quote not established here” means the reviewed page did not establish a numerical quote for that item; it is not a claim that no price exists elsewhere. A plus sign or “from” amount is a starting figure, not a ceiling.')
    body+=section(c['focus'],p(html.escape(c['detail'])))
    body+=section('Request the complete appointment total',p('Send the salon a current photo, your recent color or treatment history and a description of the result you want. Say whether you are maintaining the current look or asking for a substantial change. Ask which artist and reservation fit that starting point, then request a complete estimate.')+ul(['Is the listed amount for my chosen stylist and appointment location?','Does the quote include consultation, toning, cutting and the finish I want?','What additional time, product or preparation could change the estimate?','Which follow-up services should I budget for after this visit?']))
    body+=section('Compare with a Craft Collective appointment',p('Craft lists selected skincare, brow and lash prices on its '+a('/hair-services-pittsburgh','service menu')+'. Its reviewed hair menu does not establish fixed dollar quotes for most color, cut or extension appointments. '+a('/pricing/craft-collective','Craft’s pricing guide')+' separates published amounts from services needing an individual estimate.')+p('Use the same goal and inclusions when requesting a Craft quote. North Hills has online booking; Canonsburg is by appointment and should be confirmed by phone at 724-514-7231. A missing public number cannot be treated as zero or as evidence that one salon is less expensive.'))
    body+=section('Check the repeat-visit budget',p('Ask about maintenance after the initial result, including which smaller services might be needed between larger visits. For extensions, separate hair purchase, installation, adjustments and removal. Compare totals over the same period and keep optional purchases separate. Confirm deposits and cancellation terms before reserving; a deposit credited toward the service is not an extra service charge.'))
    body+=p(a(c['comparison'],'Read the '+c['name']+' vs. Craft Collective comparison')+'.')+pricing_links()
    publish(c['slug'],title,'Explore '+c['name']+' published prices, service inclusions and estimate questions. Compare the full appointment with Craft Collective.',body)

# Craft's prices come directly from the existing services menu; don't fill gaps with invented rates.
menu=(R/'hair-services-pittsburgh/index.html').read_text()
craft_rows=[]
for block in re.findall(r'<div class="service-item">(.*?)</div>',menu,re.S):
    name=re.search(r'<h3 class="service-item-name">(.*?)</h3>',block,re.S)
    duration=re.search(r'<p class="service-item-duration">(.*?)</p>',block,re.S)
    if name and duration:
        label=html.unescape(re.sub('<[^>]+>','',name[1])).strip()
        value=html.unescape(re.sub('<[^>]+>','',duration[1])).strip()
        if '$' in value:craft_rows.append((label,value))
assert len(craft_rows)>=15
body=p('Find Craft Collective’s published service prices and the next step for an individual hair-service estimate. Review the amounts listed on our services page below. For haircuts, color and extensions, request an individual quote matched to your stylist and service.')
body+=section('Published prices from the Craft service menu',p('Source: '+a('/hair-services-pittsburgh','Craft Collective services')+', checked October 24, 2026. Confirm your provider, location and current reservation amount before booking.')+table('Craft Collective published prices',['Service','Menu amount and duration'],craft_rows))
body+=section('Hair services that need an individual estimate',table('Hair-service pricing status',['Service','Current public-menu status','What to clarify'],[
['Haircuts and styling','Durations listed; fixed dollar quote not established here','Stylist, cut, shampoo and finish'],['Balayage and highlights','Individual estimate needed','Coverage, tone, root work, cut and finish'],['Full color and root work','Individual estimate needed','Maintenance or transformation; complete inclusions'],['Gloss and toner','Individual estimate needed','Standalone or add-on; finish'],['Extensions','Consultation required','Hair, installation, upkeep and removal'],['Keratin and smoothing','Individual estimate needed','Specific treatment, time and aftercare'],['Nail appointments','Confirm chosen provider and service','Shape, removal, art and finish']]))
body+=section('How to get an accurate hair quote',p('Explain your current length, density, recent color or treatments and desired result. Bring daylight photos and identify what you want to preserve. Ask for the service components, expected total, appointment time and upkeep plan. If a menu label is unfamiliar, call rather than choosing a shorter reservation that may not fit your goal.'))
body+=section('Confirm the studio before booking',p('North Hills is at 2014D Babcock Boulevard, Pittsburgh, and offers online booking. Canonsburg is at 115 W Pike Street and is by appointment; call 724-514-7231. Confirm which studio and artist are on your reservation. A time shown online for North Hills is not a Canonsburg appointment.'))
body+=section('Compare prices for the same work',p('A published skincare price does not establish a hair-service rate. Likewise, a competitor’s balayage starting amount does not establish the finished total for your hair. Use the same service brief and ask about toning, cutting and finishing at each salon. Our '+a('/guides/salon-quote-comparison-tool','quote worksheet')+' lets you compare the complete initial and maintenance estimates you actually receive.'))
body+=pricing_links()
publish('craft-collective','Craft Collective Pricing: Services, Published Prices & Hair Estimates','See Craft Collective published skincare, brow and lash prices, plus how to request hair-service estimates for North Hills and Canonsburg.',body)

service_info={
'cut':('haircut-prices-pittsburgh','Pittsburgh Haircut Prices: Compare Published Salon Menus',
'Compare the actual haircut reservation, not just the lowest number in a salon menu. A scissor cut, a clipper cut, a curl-focused appointment and a quick maintenance trim may involve different time and finishing. The selected examples below preserve those labels so you can see what you are comparing.',
'Is a wash and finish included?',
'Ask whether the reservation includes shampoo, consultation and the way you want your hair styled. A dry cut may have its own arrival instructions, while an express trim may be restricted to existing clients. Explain if you want a new shape, need a curl assessment or usually wear your hair both natural and straight. Those details can change the appointment that fits.',
'Choosing a haircut artist',
'Compare examples on a similar length and texture and discuss the parts of your current shape you want to keep. For a short cut, show the side and back outline as well as the front. Ask how the result will behave with your normal styling routine. A higher or lower artist level is a pricing category, not proof of the result you will receive.'),
'balayage':('balayage-prices-pittsburgh','Pittsburgh Balayage Prices: Published Packages & Starting Rates',
'Balayage and blonding prices become useful only when the amount of work is clear. A face-framing refresh, a full lightening visit and a package with a haircut are different appointments. These published examples keep their original scope and qualifiers rather than turning them into a citywide average.',
'Lightening is only part of the finished plan',
'Ask whether the quote includes the brightness you want, toning, a root blend, cutting and the final style. Describe previous permanent color and home color before asking for a total. A soft-rooted photograph does not tell the salon how much lightening your starting point needs. Ask what is realistic at the first visit and what may need later work.',
'Compare upkeep separately from installation of the look',
'Ask which feature needs refreshing first: tone, face frame, root transition or all-over brightness. A larger initial appointment and a smaller follow-up may form one plan; another may involve a different sequence. Use the same comparison period for both estimates instead of assuming the salon with the lower opening figure will cost less over time.'),
'highlights':('highlights-prices-pittsburgh','Pittsburgh Highlights Prices: Full, Partial & Blonding Packages',
'Compare full highlights, partial highlights and complete blonding packages with care. They describe different amounts of placement and may include different finishing services. The table preserves those distinctions and links the published source so you can check the current menu.',
'Which sections will actually be lightened?',
'Describe where you want brightness visible: around the face, across the crown, underneath or throughout the head. Ask the stylist which placement plan matches that goal. A partial appointment can mean a different set of sections at another salon. If the underneath area matters when you tie your hair up, discuss it before choosing a lower-priced label.',
'Keep root coverage and toning in the estimate',
'Ask whether covering gray roots is separate from highlighting, and whether toner or a gloss is included. A foiling price may cover placement without the full finish shown in your reference. Compare the complete proposed result, then ask how maintenance differs from the first visit. Bring current photographs so the appointment is planned from your actual color.'),
'root':('root-touch-up-color-prices-pittsburgh','Pittsburgh Root Touch-Up & Color Prices: Compare Service Scope',
'A root touch-up, all-over color and color-and-cut package are not interchangeable prices. Before comparing the listed amounts, decide whether you want to maintain regrowth coverage, change tone through the lengths or combine color with a new haircut. The published labels below remain visible for that reason.',
'Coverage and blending are different goals',
'Explain whether you want opaque coverage, a softer gray blend or a tonal change. Tell the stylist how long it has been since the last color and whether the ends also need attention. Ask if the quote is only for regrowth or includes refreshing the lengths. If additional light pieces are part of the goal, request the combined plan.',
'Ask what happens between full appointments',
'Confirm how regrowth will be maintained and whether a gloss, cut or larger color refresh is expected later. Use the routine recommended for your own starting point rather than a general internet schedule. Keep the comparison consistent: color with a haircut should be measured against another complete cut-and-color quote, not a root-only base service.'),
'gloss':('gloss-toner-prices-pittsburgh','Pittsburgh Gloss & Toner Prices: Add-Ons vs. Complete Visits',
'A toner add-on during lightening and a standalone gloss appointment can have different costs because the surrounding services differ. The examples below keep the add-on and standalone labels visible. Ask which appointment addresses the tone you want to change.',
'Distinguish tone from additional brightness',
'Describe what changed after the previous appointment: unwanted warmth, a darker appearance, faded ends or uneven tone. Show comparable daylight photographs. Ask whether the goal is a tonal refresh or whether lightening or other color work is needed. A toner label should not be used to reserve a short visit for a larger transformation.',
'Finishing changes the complete visit',
'Ask whether a wash, haircut or styled finish is included. An add-on price may assume another service is already taking place; it is not automatically the total for a separate appointment. Confirm the recommended home routine, then ask what future tone maintenance would involve. Use the estimate for your own plan rather than adding unrelated menu items yourself.'),
'blowout':('blowout-styling-prices-pittsburgh','Pittsburgh Blowout Prices: Styling, Finishing & Service Estimates',
'A blowout is a styling reservation; a smoothing treatment is a different service. Compare whether the quoted appointment includes a wash, drying and the tool work needed for your chosen finish. These published examples keep the original labels and starting-price language.',
'Explain the finish and the occasion',
'Say whether you want smoothness, volume, waves or a style for an event. Ask whether hot-tool work is included or separately priced. If your reference needs pins, braids or an updo, confirm that a standard blowout reservation is the right choice. Mention your length, density and departure deadline before selecting an opening.',
'Plan around the complete appointment',
'Confirm when to arrive, whether to come with clean dry hair or expect a shampoo, and how long the visit takes. Ask about an additional service only after the salon has reserved enough time. A style for a wedding party has different scheduling needs from one everyday blowout. Compare the actual finish and provider you would book.')}
for category,(slug,title,intro,heading,detail,heading2,detail2) in service_info.items():
    rows=[]
    for c in salons:
        for row in c['rows']:
            if row[0]==category:
                rows.append((c,row))
    assert len(rows)>=8,(category,len(rows))
    body=p(intro)+p('Selected official menus and business booking pages were reviewed October 24, 2026. This is a Craft Collective guide, not a market average or a ranking. Artist levels, included work and publication formats differ; confirm the current complete estimate directly.')
    t='<div class="comparison-scroll" role="region" aria-label="Published service price examples" tabindex="0"><table><caption>Selected published '+html.escape(category)+' menu entries</caption><thead><tr><th scope="col">Salon and menu item</th><th scope="col">Published amount or status</th><th scope="col">Scope and source</th></tr></thead><tbody>'
    for c,row in rows:
        t+='<tr><th scope="row">'+a('/pricing/'+c['slug'],c['name'])+'<br>'+html.escape(row[1])+'</th><td>'+html.escape(row[2])+'</td><td>'+html.escape(row[3])+'. '+a(c['source'],'Official source')+'</td></tr>'
    body+=section('Published examples to compare',t+'</tbody></table></div>')
    body+=section(heading,p(detail))+section(heading2,p(detail2))
    body+=section('What does Craft Collective charge?',p('Craft’s reviewed hair menu does not establish a fixed dollar quote for this appointment. Ask for the individual stylist, studio, full service scope and estimate. See '+a('/pricing/craft-collective','Craft’s published prices and hair-estimate guide')+'. North Hills can be booked online; call 724-514-7231 for Canonsburg or help choosing a reservation.'))
    body+=section('Use the same service brief',ul(['Share your starting hair, recent service history and reference photographs.','Name the finish you want and the inclusions you expect.','Ask for the complete first visit and the suggested upkeep.','Confirm the artist, location and current policies before reserving.'])+p('Use the '+a('/guides/salon-quote-comparison-tool','quote worksheet')+' to compare actual proposals over the same period. Unknown costs remain unknown until the salon confirms them; they are not zero-dollar services.'))
    body+=pricing_links()
    publish(slug,title,'Compare selected published Pittsburgh '+category+' prices, service packages and estimate questions, with official sources and Craft booking guidance.',body)

# Central directory links every new page and gives pricing questions one clear entry point.
body=p('Find Pittsburgh salon pricing pages, compare published menu examples by service, and see which Craft Collective prices are already listed. Use this directory to gather the actual appointment details before comparing totals.')
body+=section('Start with Craft Collective',p(a('/pricing/craft-collective','Craft Collective published prices and hair estimates')+' separates the skincare, brow and lash amounts on our menu from hair services requiring an individual quote. '+a('/guides/salon-quote-comparison-tool','Compare two complete salon quotes')+' once you have the inclusions and maintenance plan.'))
body+=section('Browse competitor pricing guides','<form id="pricing-filter" role="search"><label for="pricing-search">Search salons, areas or pricing structures</label><input type="search" id="pricing-search" aria-controls="pricing-list" placeholder="Try Wexford, hourly, packages or a salon name"><button type="reset" class="worksheet-button">Clear search</button><p id="pricing-count" role="status" aria-live="polite">20 salon pricing guides, listed alphabetically.</p></form><ul id="pricing-list" class="salon-directory">'+''.join('<li>'+a('/pricing/'+c['slug'],c['name']+' prices')+'<p>'+html.escape(c['area'])+' · '+html.escape(c['model'])+'</p></li>' for c in sorted(salons,key=lambda x:x['name'].casefold()))+'</ul><p id="pricing-empty" hidden>No pricing guides match this search. Clear the search to browse all salons.</p>')
body+=section('Compare published prices by service',ul([a('/pricing/'+v[0],v[1]) for v in service_info.values()]))
body+=section('How this directory treats prices',p('Each competitor page links the official menu or business booking page reviewed October 24, 2026. Starting figures, ranges, artist levels and exclusions remain attached to the published service. Conflicting amounts are identified rather than silently choosing the lower number. A quote not established on the reviewed page is not described as a free service or as proof that no pricing exists elsewhere.')+p('The service tables are selected examples, not a complete market survey. They do not establish an average Pittsburgh rate, a cheapest provider or a price advantage for Craft. A color package with finishing and a base lightening charge have different scope. Use the linked sources and ask the salon to confirm what applies to your own appointment.'))
body+=section('Turn the research into a booking decision',p('Choose the relevant service and artist first, then compare the full appointment and expected maintenance over the same period. Ask about toner, cutting, finishing, added hair and any separate provider you want to see. Confirm the final studio address and policies before reserving.')+p('Explore '+a('/guides/pittsburgh-salon-alternatives','salon alternatives and comparisons')+', '+a('/guides/salon-price-comparison-pittsburgh','the full estimate checklist')+' and '+a('/guides/switching-hair-salons-pittsburgh','the switching-salons guide')+' to prepare.'))
publish('','Pittsburgh Salon Pricing Directory | Craft Collective','Browse 20 salon pricing guides, Craft Collective published prices and six service-price comparisons with linked official menus and estimate checklists.',body)
f=R/'pricing/index.html';s=f.read_text().replace('</head>','<link rel="stylesheet" href="/assets/salon-comparison-tools.css"><link rel="stylesheet" href="/assets/pricing-directory.css"></head>').replace('</body>','<script src="/assets/pricing-directory.js" defer></script></body>')
graph={'@context':'https://schema.org','@graph':[{'@type':'CollectionPage','name':'Pittsburgh Salon Pricing Directory','url':D+'/pricing','dateModified':DATE},{'@type':'ItemList','name':'Salon pricing guides','itemListElement':[{'@type':'ListItem','position':i+1,'name':c['name']+' pricing','url':D+'/pricing/'+c['slug']} for i,c in enumerate(sorted(salons,key=lambda x:x['name'].casefold()))]}]}
s=re.sub(r'<script type="application/ld\+json">.*?</script>',lambda _: '<script type="application/ld+json">'+json.dumps(graph)+'</script>',s,flags=re.S);f.write_text(s)

# Add navigation at the homepage, main service menu, comparison hub, blog and relevant sources.
paths=['index.html','hair-services-pittsburgh/index.html','guides/index.html','blog/index.html','guides/pittsburgh-salon-alternatives/index.html','guides/salon-price-comparison-pittsburgh/index.html','locations/north-hills-pittsburgh/index.html','locations/canonsburg/index.html']
paths += [c['comparison'].lstrip('/')+'/index.html' for c in salons if c['comparison'].startswith('/guides/')]
for relative in paths:
    f=R/relative
    if not f.exists():continue
    s=f.read_text();s=re.sub(r'<!-- cc:pricing-expansion -->.*?<!-- /cc:pricing-expansion -->','',s,flags=re.S)
    block='<!-- cc:pricing-expansion --><section class="archive-body"><h2>Explore salon prices before booking</h2>'+p(a('/pricing','Pittsburgh salon pricing directory')+' · '+a('/pricing/craft-collective','Craft Collective prices and estimates')+' · '+a('/guides/salon-quote-comparison-tool','Compare complete quotes'))+'</section><!-- /cc:pricing-expansion -->'
    s=s.replace('</main>',block+'</main>',1) if '</main>' in s else s.replace('<footer',block+'<footer',1)
    assert block in s,relative;f.write_text(s)
# Add a direct pricing link to each source comparison that exists on disk.
for c in salons:
    f=R/c['comparison'].lstrip('/')/'index.html'
    if not f.exists():continue
    s=f.read_text();s=re.sub(r'<!-- cc:salon-pricing -->.*?<!-- /cc:salon-pricing -->','',s,flags=re.S)
    block='<!-- cc:salon-pricing --><section class="archive-body"><h2>'+html.escape(c['name'])+' pricing details</h2>'+p(a('/pricing/'+c['slug'],'Read the published-price and estimate guide')+' for source-linked menu examples, inclusions and current-quote questions.')+'</section><!-- /cc:salon-pricing -->'
    s=s.replace('</main>',block+'</main>',1) if '</main>' in s else s.replace('<footer',block+'<footer',1);f.write_text(s)
NS='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',NS)
root=ET.Element('{'+NS+'}urlset')
for row in records:
    node=ET.SubElement(root,'{'+NS+'}url');ET.SubElement(node,'{'+NS+'}loc').text=D+row['path'];ET.SubElement(node,'{'+NS+'}lastmod').text=DATE
ET.ElementTree(root).write(R/'salon-pricing-sitemap.xml',encoding='UTF-8',xml_declaration=True)
f=R/'sitemap.xml';tree=ET.parse(f);root=tree.getroot()
if D+'/salon-pricing-sitemap.xml' not in [n.text for n in root.findall('.//{'+NS+'}loc')]:
    node=ET.SubElement(root,'{'+NS+'}sitemap');ET.SubElement(node,'{'+NS+'}loc').text=D+'/salon-pricing-sitemap.xml'
tree.write(f,encoding='UTF-8',xml_declaration=True)
(R/'scripts/pricing-expansion-manifest.json').write_text(json.dumps({'date':DATE,'pages':records,'salons':len(salons),'craftPublishedPriceRows':len(craft_rows),'serviceComparisons':len(service_info)},indent=2)+'\n')
print(f'Created {len(records)} pricing pages for {len(salons)} salons, with {len(craft_rows)} existing Craft price entries.')
