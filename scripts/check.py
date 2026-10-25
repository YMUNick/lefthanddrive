"""Verify generated local links, content disclosures and ZIP integrity."""
from html.parser import HTMLParser
import json
from pathlib import Path
import zipfile
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.refs=[]
        self.ids=set()
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs['id'])
        for key in ('href','src'):
            if key in attrs:
                self.refs.append(attrs[key])

def check():
    data=json.loads((ROOT/'content/band.json').read_text(encoding='utf-8'))
    assert len(data['members'])==5
    assert len(data['tracks'])==3
    assert len(data['videos'])==2
    for track in data['tracks']:
        if track['status']=='published':
            assert track['title'] and track['url'].startswith('https://')
        else:
            assert track['status']=='pending' and not track['title'] and not track['url']
    pages={p:Page((ROOT/p).read_text(encoding='utf-8')) for p in ['index.html','band.html','epk.html','booking.html','downloads/Lefthand-Drive-EPK.html']}
    checked=0
    for filename,page in pages.items():
        for ref in page.refs:
            parts=urlsplit(ref)
            if parts.scheme or parts.netloc:
                continue
            assert ref and ref!='#',f'{filename}: empty link'
            target=(ROOT/filename).parent/unquote(parts.path) if parts.path else ROOT/filename
            assert target.is_file(),f'{filename}: missing {ref}'
            if parts.fragment and target.suffix=='.html':
                parsed=Page(target.read_text(encoding='utf-8'))
                assert unquote(parts.fragment) in parsed.ids,f'{filename}: missing anchor {ref}'
            checked+=1
    portable=(ROOT/'downloads/Lefthand-Drive-EPK.html').read_text(encoding='utf-8')
    assert '@import' not in portable and ':root{' in portable
    assert 'src="images/' not in portable, 'Portable photos must be embedded'
    assert portable.count('src="data:image/')==7
    assert data['bio']['short_en'] in portable and data['bio']['short_zh'] in portable
    assert '代表作待提供' in portable and 'Selection to be supplied' in portable
    assert '並非正式技術需求表' in portable
    with zipfile.ZipFile(ROOT/'downloads/Lefthand-Drive-EPK.zip') as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==10
        assert archive.read('Lefthand-Drive-EPK.html')==(ROOT/'downloads/Lefthand-Drive-EPK.html').read_bytes()
    print(f'PASS: {len(pages)} pages, {checked} internal references, 10 ZIP entries, bilingual content and pending-data labels.')

if __name__=='__main__':
    check()
