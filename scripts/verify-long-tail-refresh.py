"""Regression checks against a build of the previous production source.

Usage: python3 scripts/verify-long-tail-refresh.py ../baseline-dist dist
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json, re, sys
import xml.etree.ElementTree as ET

baseline, output = map(Path, sys.argv[1:3])
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.booking=[]; self.links=[]; self.frames=[]; self.scripts=[]; self.h1=0
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='h1': self.h1+=1
        if tag=='a':
            href=attrs.get('href',''); self.links.append(href)
            if 'phorest' in href: self.booking.append(tuple(sorted(attrs.items())))
        if tag=='iframe': self.frames.append(tuple(sorted(attrs.items())))
        if tag=='script' and 'src' in attrs: self.scripts.append(tuple(sorted(attrs.items())))

before={str(p.relative_to(baseline)):p for p in baseline.rglob('*') if p.is_file()}
after={str(p.relative_to(output)):p for p in output.rglob('*') if p.is_file()}
assert before.keys()==after.keys(), 'Unexpected new/deleted files or URLs'
changed=[key for key in before if before[key].read_bytes()!=after[key].read_bytes()]
assert 'index.html' not in changed, 'Homepage changed'
assert not any(key.startswith(('assets/','book/','team/','meet-the-team/','images/')) for key in changed), 'Booking, team or shared assets changed'
allowed_prefixes=('post/','services/gray-blending-pittsburgh/','services/curly-haircuts-pittsburgh/','pittsburgh-hair-guide/')
html_changes=[]
for key in changed:
    if not key.endswith('.html'): continue
    assert key.startswith(allowed_prefixes), key
    original=Page(before[key].read_text()); html=after[key].read_text(); revised=Page(html)
    assert Counter(original.booking)==Counter(revised.booking), 'Phorest anchors changed: '+key
    assert original.frames==revised.frames, 'Widget changed: '+key
    assert original.scripts==revised.scripts, 'Page scripts changed: '+key
    assert revised.h1==1, key
    route='/'+key.removesuffix('/index.html')
    assert f'rel="canonical" href="https://www.craftcollectivesalongroup.com{route}"' in html, key
    for href in revised.links:
        if href.startswith('/') and not href.startswith('//'):
            target=output/href.lstrip('/').split('?')[0].split('#')[0]
            assert target.exists() or (target/'index.html').exists(), f'Broken link {key}: {href}'
    for schema in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S):
        data=json.loads(schema)
        for item in data.get('@graph',[data]):
            if item.get('@type') in ('BlogPosting','Article') and key.startswith('post/'):
                old_schema=json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>',before[key].read_text(),re.S)[0])
                assert item.get('datePublished')==old_schema.get('datePublished'), 'Publication date changed'
                assert item.get('dateModified')=='2026-10-10', key
    html_changes.append(route)
for key in changed:
    if key.endswith('.xml'): ET.parse(after[key])
index=json.loads((output/'pittsburgh-hair-guide/search-index.json').read_text())
assert len(index)==len({item['path'] for item in index}), 'Duplicate search entries'
assert len([x for x in html_changes if x.startswith('/post/')])==5
assert len([x for x in html_changes if x.startswith('/services/')])==2
print(json.dumps({'result':'PASS','revisedArticles':5,'expandedServicePages':2,'linkedTopicHubs':len(html_changes)-7,'newUrls':0,'homepage':'byte-identical','bookingPageAndSharedAssets':'byte-identical','allExistingPhorestLinksAndWidgets':'unchanged','schemaAndInternalLinks':'valid','changedFiles':changed},indent=2))
