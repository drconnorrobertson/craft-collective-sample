"""Read-only production verification for the search and browse utilities."""
from pathlib import Path
import json,re,urllib.request,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
site='https://www.craftcollectivesalongroup.com'
def read(route):
    with urllib.request.urlopen(site+route,timeout=30) as response:
        assert response.status==200,(route,response.status)
        return response.read().decode()
search=read('/search?q=balayage%20prices')
assert 'content="noindex, follow"' in search
index=re.search(r'data-index="([^"]+)"',search)[1]
records=json.loads(read(index))
local=json.loads((root/'dist/site-search-manifest.json').read_text())
assert len(records)==local['records']
assert len({r['path'] for r in records})==len(records)
assert any(r['path']=='/pricing/balayage-prices-pittsburgh' for r in records)
for key in ['client','core']:assert read(local[key])
assert read('/assets/site-search.css')
explore=read('/explore');assert 'Explore Craft Collective' in explore
assert 'href="/locations/canonsburg"' in explore
assert 'href="/search"' in read('/')
xml=read('/site-pages-sitemap.xml');ET.fromstring(xml)
assert site+'/explore</loc>' in xml
assert site+'/search</loc>' not in xml
print(f'Live search checks passed: {len(records)} records; query page, fingerprinted assets, noindex rule, directory, homepage link and sitemap.')
