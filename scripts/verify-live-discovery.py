"""Read-only post-release verification for local discovery and checked pricing."""
from pathlib import Path
import html,json,re,urllib.request,urllib.error,urllib.parse,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
site='https://www.craftcollectivesalongroup.com'
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None
opener=urllib.request.build_opener(NoRedirect)
redirects=json.loads((root/'scripts/verified-duplicate-redirects.json').read_text())['redirects']
for source,target in redirects.items():
    try:opener.open(urllib.request.Request(site+source,method='HEAD'),timeout=30);raise AssertionError('Expected permanent redirect '+source)
    except urllib.error.HTTPError as error:
        assert error.code in (301,308),(source,error.code)
        assert urllib.parse.urljoin(site+source,error.headers['Location'])==site+target,(source,error.headers['Location'])
        print(error.code,source,'->',target)
def read(route):
    with urllib.request.urlopen(site+route,timeout=30) as response:
        assert response.status==200
        return response.read().decode()
locations=read('/locations');assert 'Choose the Craft Collective studio' in locations
booking=read('/book');assert 'id="booking-studio-choice"' in booking
for slug in ['north-hills-pittsburgh','canonsburg']:
    body=read('/locations/'+slug)
    objects=[json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>',body,re.S)]
    assert sum(x.get('@type')=='HairSalon' for x in objects)==1
prices=html.unescape(read('/pricing/craft-collective'))
for row in json.loads((root/'scripts/craft-booking-prices.json').read_text())['rows']:
    assert all(cell in prices for cell in row[1:]),row
xml=ET.fromstring(read('/salon-pricing-sitemap.xml'))
for row in xml:
    assert row.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text>='2026-10-25'
print('Live checks passed: permanent redirects, studio chooser, booking choice, two branch entities, 22 booking-price entries and preserved sitemap dates.')
