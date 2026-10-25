"""Check pricing output against the researched rows and the existing Craft menu."""
from pathlib import Path
import html,json,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
out=root/'dist'
manifest=json.loads((root/'scripts/pricing-expansion-manifest.json').read_text())
research=json.loads((root/'scripts/pricing-research.json').read_text())
assert len(manifest['pages'])==28
assert len(research['salons'])==20
for row in manifest['pages']:
    page=out/row['path'].lstrip('/')/'index.html'
    text=page.read_text()
    assert len(re.findall(r'<h1(?:>| )',text))==1,page
    assert 'href="https://www.craftcollectivesalongroup.com'+row['path']+'"' in text,page
    for script in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):
        json.loads(script)
        assert '"Offer"' not in script and '"AggregateOffer"' not in script,page
    for url in re.findall(r'(?:href|src)="(/[^"?#]*)',text):
        target=out/url.lstrip('/')
        assert target.is_file() or (target/'index.html').is_file() or target.with_suffix('.html').is_file(),(page,url)
    assert len(re.sub('<[^>]+>',' ',re.search(r'<article class="archive-body">(.*?)</article>',text,re.S)[1]).split())>=400,page
for salon in research['salons']:
    text=html.unescape((out/'pricing'/salon['slug']/'index.html').read_text())
    assert salon['source'] in text,salon['slug']
    for row in salon['rows']:
        assert all(cell in text for cell in row[1:]),(salon['slug'],row)
    comparison=(out/salon['comparison'].lstrip('/')/'index.html').read_text()
    assert 'href="/pricing/'+salon['slug']+'"' in comparison,salon['slug']
ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
urls=[node.text for node in ET.parse(out/'salon-pricing-sitemap.xml').findall('.//'+ns+'loc')]
assert len(urls)==len(set(urls))==28
assert 'https://www.craftcollectivesalongroup.com/salon-pricing-sitemap.xml' in (out/'sitemap.xml').read_text()
for row in manifest['pages']:assert 'https://www.craftcollectivesalongroup.com'+row['path'] in urls
craft=html.unescape((out/'pricing/craft-collective/index.html').read_text())
source=(root/'hair-services-pittsburgh/index.html').read_text()
price_rows=0
for block in re.findall(r'<div class="service-item">(.*?)</div>',source,re.S):
    label=re.search(r'<h3 class="service-item-name">(.*?)</h3>',block,re.S)
    value=re.search(r'<p class="service-item-duration">(.*?)</p>',block,re.S)
    if label and value and '$' in value[1]:
        assert html.unescape(label[1]).strip() in craft
        assert html.unescape(value[1]).strip() in craft
        price_rows+=1
assert price_rows==manifest['craftPublishedPriceRows']==19
print('Passed: 28 pages, 20 researched salon menus, 19 Craft price entries, schemas, canonicals, links, pricing pathways and sitemaps.')
