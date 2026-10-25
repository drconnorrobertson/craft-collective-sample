"""Regression checks for duplicate consolidation, location discovery and sitemap dates."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
out=root/'dist'
site='https://www.craftcollectivesalongroup.com'
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
redirects=json.loads((root/'scripts/verified-duplicate-redirects.json').read_text())['redirects']
config=json.loads((root/'vercel.json').read_text())
assert not any(r['source']=='/locations' for r in config['redirects'])
for source,target in redirects.items():
    assert any(r['source']==source and r['destination']==target and r['permanent'] for r in config['redirects'])
    assert f'rel="canonical" href="{site+target}"' in (out/source.lstrip('/')/'index.html').read_text()
    assert (out/target.lstrip('/')/'index.html').is_file()
for sitemap in out.glob('*sitemap.xml'):
    ET.parse(sitemap)
    assert not any(site+source+'</loc>' in sitemap.read_text() for source in redirects)
for row in ET.parse(out/'salon-pricing-sitemap.xml').getroot():
    assert row.find(ns+'lastmod').text>='2026-10-24'
for slug,city,street in [('north-hills-pittsburgh','Pittsburgh','2014D Babcock Blvd'),('canonsburg','Canonsburg','115 W Pike St')]:
    html=(out/'locations'/slug/'index.html').read_text()
    data=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)]
    branches=[s for s in data if s.get('@type')=='HairSalon']
    assert len(branches)==1
    entity=branches[0]
    assert entity['address']['addressLocality']==city
    assert entity['address']['streetAddress']==street
    assert entity['telephone']=='+17245147231'
    assert 'aggregateRating' not in entity
    assert entity['address']['streetAddress'] in html
for relative in ['locations/index.html','book/index.html']:
    html=(out/relative).read_text()
    assert len(re.findall(r'<h1(?:>| )',html))==1
    for url in re.findall(r'(?:href|src)="(/[^"?#]*)',html):
        target=out/url.lstrip('/')
        assert target.is_file() or (target/'index.html').is_file() or target.with_suffix('.html').is_file(),url
    for data in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S):json.loads(data)
booking=(out/'book/index.html').read_text()
assert booking.index('id="booking-studio-choice"') < booking.index('class="booking-embed"')
for anchor in ['north-hills-booking','canonsburg-booking']:
    assert booking.count('id="'+anchor+'"')==1
    assert 'href="#'+anchor+'"' in booking
for page in out.rglob('*.html'):
    html=page.read_text()
    assert not re.search(r'href="/locations/north-hills-pittsburgh"[^>]*>\s*Locations\s*</a>',html),page
    for source in redirects:assert 'href="'+source+'"' not in html,page
print('Passed: duplicate redirect/canonical/link/sitemap alignment; 28 pricing dates; two branch entities; studio directory and booking location choice.')
