"""Build the dependency-free GitHub Pages site and portable press kit."""
import base64
import html
import hashlib
import json
import mimetypes
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'content/band.json').read_text(encoding='utf-8'))
ASSET_VERSION = hashlib.sha256(b''.join((ROOT / path).read_bytes() for path in ['assets/site.css', 'assets/site.mjs', 'assets/core.mjs'])).hexdigest()[:12]


def esc(value):
    return html.escape(str(value), quote=True)


def t(en, zh):
    return f'<span lang="en" data-lang="en">{esc(en)}</span><span lang="zh-Hant" data-lang="zh-Hant">{esc(zh)}</span>'


ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>'
DOWN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="m9 5 11 7-11 7z"/></svg>'
MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 7h18M3 16h18"/></svg>'


def link(url, label, cls='', icon=ARROW, external=False, download=False):
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ''
    if download:
        attrs += ' download'
    return f'<a href="{esc(url)}" class="{cls}"{attrs}>{label}{icon}</a>'


def header(current='home'):
    nav = [('Music', '音樂', 'index.html#music'), ('Live', '現場', 'index.html#live'),
           ('About', '樂團', 'index.html#about'), ('Shows', '演出', 'index.html#shows'),
           ('EPK', 'EPK', 'epk.html'), ('Contact', '聯絡', 'index.html#contact')]
    links = ''.join(f'<a href="{url}"{chr(32) + "aria-current=page" if current == "epk" and en == "EPK" else ""}>{t(en,zh)}</a>' for en,zh,url in nav)
    return f'''<a class="skip-link" href="#main">{t('Skip to content','跳至主要內容')}</a>
<header class="site-header"><div class="wrap header-inner">
<a class="wordmark" href="index.html" aria-label="Lefthand Drive home"><span class="brand-symbol" aria-hidden="true">↙</span><span>LEFTHAND DRIVE<small>INDEPENDENT ROCK · SINGAPORE</small></span></a>
<nav class="desktop-nav" aria-label="Main navigation">{links}</nav>
{link('booking.html',t('Book rehearsal','預約排練室'),'button primary header-booking')}
<button class="language-toggle" type="button" data-language-toggle aria-label="Switch to Traditional Chinese">繁中</button>
<button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="mobile-menu">{MENU}</button>
<nav class="mobile-nav" id="mobile-menu" aria-label="Mobile navigation" hidden>{links}</nav>
</div></header>'''


def footer():
    return f'''<footer class="site-footer"><div class="wrap footer-inner"><span>© <span data-year>2026</span> Lefthand Drive. {t('All rights reserved.','保留所有權利。')}</span><div class="footer-links"><a href="epk.html">{t('Press & booking','媒體與邀演')}</a><a href="booking.html">{t('Rehearsal room','排練室預約')}</a><a href="index.html#main">{t('Back to top ↑','回到頂端 ↑')}</a></div><span class="micro">SINGAPORE · UTC +08:00</span></div></footer>'''


def rehearsal_section():
    return f'''<section class="rehearsal-section" id="rehearsal" aria-labelledby="rehearsal-title"><div class="wrap rehearsal-grid"><div><p class="micro">06 / {t('The rehearsal room','排練室預約')}</p><h2 id="rehearsal-title">{t('YOUR NEXT SESSION.','下一次排練，從這裡開始。')}</h2><p class="rehearsal-copy">{t('A space to make some noise. Book our rehearsal room at Da Jin Factory, Singapore, and make time for your next session.','在新加坡 Da Jin Factory，給音樂一個盡情發聲的空間。預約排練室，準備好下一次合奏。')}</p></div><div class="rehearsal-card"><h3>{t('Plug in. Play together.','接上樂器，一起開練。')}</h3><dl class="rehearsal-facts"><div><dt>{t('Room rate','租借費用')}</dt><dd>$20 <span>{t('/ hour','／小時')}</span></dd></div><div><dt>{t('Minimum session','最短時段')}</dt><dd>{t('2 hours','2 小時')}</dd></div></dl><p>{t('Drums, amps, PA system and microphones.','備有鼓組、音箱、PA 系統與麥克風。')}</p>{link('booking.html',t('Check availability & book','查看時段並預約'),'button rehearsal-cta')}<p class="rehearsal-location">Da Jin Factory · Singapore</p></div></div></section>'''


def shell(title, description, body, current='home'):
    page = 'epk.html' if current == 'epk' else 'band.html' if current == 'band' else ''
    url = DATA['website'] + page
    structured = {'@context':'https://schema.org','@type':'MusicGroup','name':DATA['name'],
                  'url':DATA['website'],'genre':'Rock','foundingDate':DATA['formed'],
                  'email':DATA['email'],'sameAs':list(DATA['socials'].values()),
                  'member':[{'@type':'Person','name':m['name']} for m in DATA['members']]}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#101110"><title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{DATA['website']}images/group.jpg"><meta property="og:image:alt" content="Lefthand Drive, five-piece rock band from Singapore"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="assets/site.css?v={ASSET_VERSION}"><script type="application/ld+json">{json.dumps(structured,ensure_ascii=False)}</script>
</head><body>{header(current)}<noscript><style>.menu-toggle,.language-toggle{{display:none!important}}</style><nav class="no-js-note no-js-nav" aria-label="Navigation without JavaScript"><a href="index.html#music">Music</a> · <a href="index.html#live">Live</a> · <a href="band.html">Band</a> · <a href="index.html#shows">Shows</a> · <a href="epk.html">EPK</a> · <a href="index.html#contact">Contact</a><br><a href="downloads/Lefthand-Drive-EPK.html">Bilingual printable EPK / 中英文資料包</a></nav></noscript>{body}{footer()}
<script type="application/json" id="band-data">{json.dumps(DATA,ensure_ascii=False).replace('<','&lt;')}</script><script type="module" src="assets/site.mjs?v={ASSET_VERSION}"></script></body></html>'''


def socials():
    icons = {
        'Instagram': '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor" stroke="none"/>',
        'YouTube': '<path d="M21 8a3 3 0 0 0-2-3c-4-.5-10-.5-14 0a3 3 0 0 0-2 3c-.3 2.7-.3 5.3 0 8a3 3 0 0 0 2 3c4 .5 10 .5 14 0a3 3 0 0 0 2-3c.3-2.7.3-5.3 0-8Z"/><path d="m10 9 5 3-5 3Z" fill="currentColor" stroke="none"/>',
        'Spotify': '<circle cx="12" cy="12" r="9"/><path d="M6.5 9.3c3.7-1.1 7.7-.8 11 1M7.4 12.4c3.1-.9 6.4-.6 9.2.9M8.2 15.4c2.5-.6 5-.4 7.3.7"/>',
        'Facebook': '<path d="M14 22v-9h3l.5-4H14V7c0-1.2.3-2 2-2h2V1.5c-.8-.1-1.8-.2-3-.2-3 0-5 1.8-5 5V9H7v4h3v9Z" fill="currentColor" stroke="none"/>',
    }
    return '<div class="social-links">' + ''.join(link(url, f'<svg class="social-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{icons[name]}</svg><span>{esc(name)}</span>', 'social-link', external=True) for name,url in DATA['socials'].items()) + '</div>'


def stage_plan():
    instruments = {
        'drums': '<circle cx="32" cy="40" r="13"/><circle cx="32" cy="40" r="8"/><rect x="17" y="18" width="13" height="13" rx="3"/><rect x="34" y="18" width="13" height="13" rx="3"/><ellipse cx="10" cy="15" rx="8" ry="3"/><ellipse cx="54" cy="12" rx="8" ry="3"/><path d="M10 18v29m-5 6 5-6 5 6M54 15v32m-5 6 5-6 5 6M22 49l-3 7m23-7 3 7M24 10l7 7m9-9-7 9"/>',
        'guitar': '<path d="m37 26 13-16 5 4-13 16c4 5 4 10 0 14-3 3-6 2-7 5-2 5-8 7-14 2s-7-11-2-14c3-2 3-5 6-8 4-4 8-5 12-3Z"/><path d="m29 39 23-27m-3-4 8 6M24 44l5 4m10-30 5 4"/><circle cx="31" cy="37" r="3"/>',
        'vocals': '<rect x="25" y="7" width="14" height="26" rx="7"/><path d="M19 24v3a13 13 0 0 0 26 0v-3M32 40v15m-10 2 10-2 10 2M29 13h6m-6 5h6"/>',
        'bass': '<path d="m36 30 16-22 5 4-16 22c5 6 5 11 1 15-3 3-5 1-7 4-3 4-8 5-14 0s-7-10-2-14c3-2 1-4 5-8 3-3 7-4 12-1Z"/><path d="m28 43 26-32m-5-5 10 7M25 47l5 4m-2-16 6 5"/>',
    }
    positions = [('drums','VIJAY','Drums','鼓'), ('guitar','CY','Guitar','吉他'), ('vocals','NICK','Vocals','主唱'), ('guitar','JULIAN','Guitar','吉他'), ('bass','WEI LIANG','Bass','貝斯')]
    nodes = ''.join(f'<div class="stage-position stage-position-{i}"><span class="stage-instrument"><svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{instruments[kind]}</svg></span><strong>{name}</strong><span class="stage-role">{t(en,zh)}</span></div>' for i,(kind,name,en,zh) in enumerate(positions))
    return f'''<figure class="stage-plan"><figcaption class="stage-caption"><div><span class="micro accent">LEFTHAND DRIVE</span><strong>{t('STAGE PLOT','舞台配置圖')}</strong></div><span class="stage-draft">{t('Proposed · unconfirmed','建議配置・待確認')}</span></figcaption><div class="stage-deck"><span class="stage-rear micro">{t('Upstage / rear','舞台後方')}</span><div class="stage-centerline" aria-hidden="true"></div>{nodes}<span class="stage-edge" aria-hidden="true"></span></div><div class="stage-audience"><span aria-hidden="true">↓</span><span>{t('Audience / front of stage','觀眾／舞台前方')}</span><span aria-hidden="true">↓</span></div><p class="stage-note">{t('Position reference only · not to scale','僅供站位參考・未依比例繪製')}</p></figure>'''


def videos(offline=False):
    cards = []
    for v in DATA['videos']:
        url = f'https://www.youtube.com/watch?v={v["id"]}'
        stage = '' if offline else f'''<div class="video-stage"><img src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy"><button class="video-play" type="button" data-video="{v['id']}" aria-label="Play {esc(v['title'])}"><span class="play-disc">{PLAY}</span></button></div>'''
        cards.append(f'''<article class="video-card" data-watch-url="{url}">{stage}<div class="video-meta"><div><h3>{t(v['title'],v['title_zh'])}</h3><p>{t(v['note_en'],v['note_zh'])}</p></div>{link(url,'YouTube','video-fallback',external=True)}</div></article>''')
    return '<div class="video-grid">' + ''.join(cards) + '</div>'


def show_rows():
    rows=[]
    for show in sorted(DATA['shows'],key=lambda s:s['date'],reverse=True):
        date=show['date']
        from datetime import date as Date
        parsed=Date.fromisoformat(date if len(date)==10 else date+'-01')
        en=parsed.strftime('%d %b %Y') if len(date)==10 else parsed.strftime('%b %Y')
        zh=f'{parsed.year}／{parsed.month:02}／{parsed.day:02}' if len(date)==10 else f'{parsed.year}／{parsed.month:02}'
        rows.append(f'''<div class="show-row" data-show-date="{date}"><time datetime="{date}">{t(en,zh)}</time><div class="show-venue">{esc(show['venue'])}</div><div class="show-country">{t(show['country'],show['country_zh'])}</div><span class="show-status" data-status="past">{t('Archive','演出紀錄')}</span></div>''')
    return '<div class="shows-table">' + ''.join(rows) + '</div>'


def home():
    return shell('Lefthand Drive — Independent Rock from Singapore', 'Five musicians. Different roots. One rock band. Discover Lefthand Drive’s music, live performances and bilingual press kit.', f'''
<main id="main"><section class="hero wrap" aria-labelledby="hero-title">
<div class="hero-meta"><p class="eyebrow">{t('Independent rock · Singapore','獨立搖滾・新加坡')}</p><span class="micro muted">FIVE MUSICIANS. ONE FREQUENCY.</span></div>
<div class="hero-grid"><div><h1 id="hero-title"><span>LEFTHAND</span><span class="outline">DRIVE.</span></h1><p class="hero-copy">{t('Different roots. A shared sound. Five musicians finding common ground in rock.','不同的來處，共同的聲音。五位音樂人，在搖滾之中相遇。')}</p><div class="actions">{link('#music',t('Hear the music','聽我們的音樂'),'button primary',PLAY)}{link('epk.html',t('Explore the EPK','查看樂團 EPK'),'button')}</div></div>
<figure class="hero-photo" style="margin:0"><img src="images/group.jpg" width="1390" height="966" alt="The five members of Lefthand Drive together in Singapore" fetchpriority="high"><div class="photo-corner" aria-hidden="true">FIVE<br>IN ONE.</div><figcaption class="photo-caption"><span>LEFTHAND DRIVE / SINGAPORE</span><span>EST. 2023</span></figcaption></figure></div>
<div class="hero-bottom">{socials()}<a class="micro muted" href="#live">{t('Meet us where it’s loud ↓','在現場相遇 ↓')}</a></div></section>
<div class="marquee"><div class="marquee-inner" aria-hidden="true">{''.join('<div class="marquee-group"><span>FIVE MUSICIANS</span><span>DIFFERENT ROOTS</span><span>ONE SHARED SOUND</span><span>LEFTHAND DRIVE</span></div>' for _ in range(3))}</div><button class="marquee-toggle" type="button" data-marquee-toggle aria-label="Pause text animation" aria-pressed="false" hidden><svg class="marquee-pause" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 6h3v12H7zm7 0h3v12h-3z"/></svg><svg class="marquee-play" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="m9 5 11 7-11 7z"/></svg></button></div>
<section id="music" class="section wrap" aria-labelledby="music-title"><div class="section-head"><div><p class="eyebrow">01 / {t('The music','音樂作品')}</p><h2 id="music-title">{t('TURN IT UP.','把音量打開。')}</h2></div><p class="section-intro">{t('Start with Paradise. Our released single, out now on Spotify.','從〈Paradise〉開始，認識我們。已發行單曲，現於 Spotify 上架。')}</p></div>
<div class="release-grid"><div class="release-visual" aria-hidden="true"><span class="micro">LEFTHAND DRIVE / SINGLE</span><span class="display">PARA<br>DISE.</span><div class="record"><div class="record-label">LEFTHAND<br>DRIVE</div></div><span class="micro">SINGAPORE · INDEPENDENT ROCK</span></div><div class="release-body"><p class="micro accent">{t('Available now','現已上架')}</p><h3>Paradise</h3><p>{t('Five individual perspectives, brought together in one track. Take a listen and step into our sound.','把五個人的音樂觀點，收進同一首歌。按下播放，走進我們的聲音。')}</p><div class="actions">{link(DATA['tracks'][0]['url'],t('Listen on Spotify','在 Spotify 收聽'),'button primary',external=True)}</div><iframe class="spotify-embed" title="Paradise by Lefthand Drive on Spotify" src="https://open.spotify.com/embed/track/0d3qWfMjt3fZFFHP6RL3d5?theme=0" loading="lazy" allow="encrypted-media; fullscreen; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin"></iframe></div></div></section>
<section id="live" class="section video-section" aria-labelledby="live-title"><div class="wrap"><div class="section-head"><div><p class="eyebrow">02 / {t('On stage','現場演出')}</p><h2 id="live-title">{t('IN THE MOMENT.','此刻，現場。')}</h2></div><p class="section-intro">{t('The songs, the room, the five of us. Get to know Lefthand Drive through our live footage.','歌曲、空間，以及台上的五個人。透過現場影像，認識 Lefthand Drive。')}</p></div>{videos()}</div></section>
<section id="about" class="section wrap" aria-labelledby="about-title"><div class="about-grid"><figure class="about-photo" style="margin:0"><img src="images/group.jpg" width="1390" height="966" alt="Lefthand Drive band portrait" loading="lazy"><figcaption class="photo-caption">{t('Different backgrounds. Common ground.','不同背景，共同頻率。')}</figcaption></figure><div class="about-copy"><p class="eyebrow">03 / {t('The band','關於樂團')}</p><h2 id="about-title">{t('DIFFERENT ROOTS.','不同來處。')}<br><span class="accent">{t('SAME DRIVE.','同一股衝勁。')}</span></h2><p>{t(DATA['bio']['short_en'],DATA['bio']['short_zh'])}</p><div class="actions">{link('band.html',t('Meet the five','認識五位團員'),'text-link')}</div><div class="fact-strip"><div><strong>05</strong><span>{t('Members','位團員')}</span></div><div><strong>2023</strong><span>{t('Formed in Singapore','成立於新加坡')}</span></div><div><strong>ROCK</strong><span>{t('Our common language','共同語言')}</span></div></div></div></div></section>
<hr class="rule wrap"><section id="shows" class="section wrap" aria-labelledby="shows-title"><div class="section-head"><div><p class="eyebrow">04 / {t('Out in the world','走向各地')}</p><h2 id="shows-title">{t('LIVE & LOUD.','音樂，就在現場。')}</h2></div><p class="section-intro">{t('From rooms in Singapore to a stage in Cambodia. A selection of our shows so far.','從新加坡的現場，到柬埔寨的舞台。這是我們走過的部分演出。')}</p></div>{show_rows()}<div class="tour-note"><p data-upcoming-note>{t('For upcoming dates and new announcements, follow our Instagram.','最新演出消息，請追蹤我們的 Instagram。')}</p>{link(DATA['socials']['Instagram'],t('Follow the next chapter','追蹤下一站'),'text-link',external=True)}</div></section>
<section class="epk-banner" aria-labelledby="press-title"><div class="wrap"><div><p class="micro">{t('For programmers, promoters & press','給策展人、主辦與媒體')}</p><h2 id="press-title" style="margin-top:15px">{t('ALL IN ONE PLACE.','認識我們，從這裡開始。')}</h2><p>{t('Bilingual biographies, music, live footage, press photos and technical information. Meet your next live act.','中英文團介、作品、現場影片、宣傳照與演出技術資料，集中於一份 EPK。')}</p></div>{link('epk.html',t('Open the press kit','開啟樂團資料包'),'button')}</div></section>
<section id="contact" class="contact wrap" aria-labelledby="contact-title"><div class="contact-top"><div><p class="eyebrow">05 / {t('Let’s make something happen','一起創造下一場演出')}</p><h2 id="contact-title" style="margin-top:25px">{t('LET’S TALK.','聊聊合作。')}</h2></div><p class="contact-copy">{t('Festival stages, intimate rooms and cross-border collaborations. Tell us what you have in mind.','音樂節舞台、近距離的場館演出，或跨國音樂合作。歡迎與我們分享你的想法。')}</p></div>{link('mailto:'+DATA['email']+'?subject=Lefthand%20Drive%20-%20Performance%20enquiry',esc(DATA['email']),'contact-mail')}<div class="actions">{link('downloads/Lefthand-Drive-EPK.zip',t('Download EPK · ZIP','下載 EPK・ZIP'),'button',DOWN,download=True)}{link('epk.html#technical',t('Technical information','演出技術資料'),'button')}</div></section>{rehearsal_section()}</main>''')


def epk_body(offline=False):
    photos=[('images/group.jpg','Band portrait','樂團合照')]+[(m['photo'],m['name']+' · '+m['role_en'],m['name']+'・'+m['role_zh']) for m in DATA['members']]
    photo_html=''.join(f'''<figure><img src="{p}" alt="{esc(en)}" width="600" height="450" loading="lazy"><figcaption>{t(en,zh)}<br>{link(p,t('Download original','下載原圖'),'text-link',DOWN,download=True)}</figcaption></figure>''' for p,en,zh in photos)
    bio=DATA['bio']
    tracks=''
    for i,track in enumerate(DATA['tracks'],1):
        if track['status']=='published':
            tracks+=f'<div class="track-row"><span class="micro muted">0{i}</span><div><h3>{esc(track["title"])}</h3><p class="micro">{t("Released single","已發行單曲")}</p></div>{link(track["url"],t("Listen on Spotify","在 Spotify 收聽"),"text-link",external=True)}</div>'
        else:
            tracks+=f'<div class="track-row pending"><span class="micro">0{i}</span><div><h3>{t("Selection to be supplied","代表作待提供")}</h3><p class="micro">{t("Title and listening link pending","待補曲名與收聽連結")}</p></div></div>'
    tech=DATA['technical']
    downloads='' if offline else f'''<div class="download-grid">{link('downloads/Lefthand-Drive-EPK.zip',t('Complete EPK · ZIP','完整 EPK・ZIP'),'button primary',DOWN,download=True)}{link('downloads/Lefthand-Drive-EPK.html',t('Printable bilingual EPK','可列印中英文 EPK'),'button',external=True)}{link('downloads/Biographies-EN-ZH.md',t('Editable biographies · EN / 中文','可編輯團介・EN／中文'),'button',DOWN,download=True)}{link('downloads/Technical-Rider-DRAFT.md',t('Technical draft · EN / 中文','技術需求草案・EN／中文'),'button',DOWN,download=True)}</div>'''
    return f'''<main id="main"><div class="wrap"><section class="page-hero"><p class="eyebrow">LEFTHAND DRIVE / {t('Electronic press kit','樂團媒體資料包')}</p><h1>{t('THE PRESS KIT.','樂團資料包。')}</h1><p class="lead">{t('Music, people and everything behind the stage. An introduction for festivals, venues, collaborators and press.','音樂、團員，以及舞台背後的準備。給音樂節、場館、合作夥伴與媒體的完整介紹。')}</p><div class="actions no-print">{link('downloads/Lefthand-Drive-EPK.zip',t('Download the EPK','下載 EPK'),'button primary',DOWN,download=True)}<button type="button" class="button" data-print>{t('Print / Save as PDF','列印／另存 PDF')}{DOWN}</button></div><p class="micro muted" style="margin-top:22px">{t('English + Traditional Chinese · Updated','英文＋繁體中文・更新日期')} {DATA['updated']}</p></section>
<div class="epk-layout"><aside class="epk-sidebar no-print"><p class="micro">{t('Inside the kit','資料索引')}</p>{''.join(f'<a href="#{id}">{t(en,zh)}</a>' for id,en,zh in [('bio','01 / Biography','01／樂團介紹'),('repertoire','02 / Music','02／代表作品'),('footage','03 / Live footage','03／現場影片'),('photos','04 / Press photos','04／宣傳照片'),('history','05 / Shows','05／演出紀錄'),('technical','06 / Technical','06／技術資料'),('downloads','07 / Downloads','07／下載與聯絡')])}</aside><div>
<figure class="epk-hero-photo"><img src="images/group.jpg" width="1390" height="966" alt="Lefthand Drive — five-piece rock band, Singapore"><figcaption class="photo-caption">LEFTHAND DRIVE · SINGAPORE · EST. 2023</figcaption></figure>
<section class="epk-section" id="bio"><h2>{t('01 / THE BAND','01／關於樂團')}</h2><div class="bio-columns"><article lang="en"><h3>SHORT BIO / ENGLISH</h3><p>{esc(bio['short_en'])}</p></article><article lang="zh-Hant"><h3>短版團介／繁體中文</h3><p>{esc(bio['short_zh'])}</p></article></div><details class="bio-long"><summary>{t('Read the full biography · English / 中文','閱讀完整團介・English／中文')}</summary><div class="bio-columns"><p lang="en">{esc(bio['long_en'])}</p><p lang="zh-Hant">{esc(bio['long_zh'])}</p></div></details><dl class="facts"><div><dt>{t('Based in','所在地')}</dt><dd>{t('Singapore','新加坡')}</dd></div><div><dt>{t('Genre','曲風')}</dt><dd>{t('Rock','搖滾')}</dd></div><div><dt>{t('Formed','成立年份')}</dt><dd>2023</dd></div><div><dt>{t('Vocals','主唱')}</dt><dd>Nick</dd></div><div><dt>{t('Guitars','吉他')}</dt><dd>CY · Julian</dd></div><div><dt>{t('Rhythm section','節奏組')}</dt><dd>Wei Liang · Vijay</dd></div></dl></section>
<section class="epk-section" id="repertoire"><h2>{t('02 / SELECTED MUSIC','02／代表作品')}</h2>{tracks}<p class="status-note">{t('One released track is currently linked. Two additional representative selections are awaiting the band’s titles and listening links.','目前已收錄一首已發行作品；另外兩首代表作待樂團提供曲名與收聽連結。')}</p></section>
<section class="epk-section" id="footage"><h2>{t('03 / LIVE FOOTAGE','03／現場影片')}</h2>{videos(offline)}<p class="print-only">Live videos: https://www.youtube.com/watch?v=LCzkbeM5O3M · https://www.youtube.com/watch?v=tLV0B2nNNFU</p></section>
<section class="epk-section" id="photos"><h2>{t('04 / PRESS PHOTOS','04／宣傳照片')}</h2><p style="margin-bottom:25px">{t('Original files from the band’s website. For publication permissions and photographer credits, please contact the band.','照片原檔來自樂團網站。刊登授權與攝影者署名，請洽樂團確認。')}</p><div class="press-photo-grid">{photo_html}</div></section>
<section class="epk-section" id="history"><h2>{t('05 / SELECTED SHOWS','05／演出紀錄')}</h2>{show_rows()}<p class="muted" style="font-size:12px;margin-top:15px">{t('October 2025 is recorded to month precision; no exact day has been supplied.','2025 年 10 月的演出紀錄僅確認月份，尚未提供確切日期。')}</p></section>
<section class="epk-section" id="technical"><h2>{t('06 / ON STAGE','06／舞台與設備')}</h2><h3>{t(tech['lineup_en'],tech['lineup_zh'])}</h3><p>{t(tech['note_en'],tech['note_zh'])}</p>{stage_plan()}<ul class="technical-list">{''.join('<li>'+t(item['en'],item['zh'])+'</li>' for item in tech['items'])}</ul><div class="status-note">{t('Set duration, changeover time, input list, monitor mixes and equipment models: to be confirmed. Please request the final rider before advancing a show.','演出長度、換場時間、輸入通道、監聽路數與器材型號：待確認。演出製作前請向樂團索取正式技術需求表。')}</div></section>
<section class="epk-section" id="downloads"><h2>{t('07 / GET IN TOUCH','07／下載與聯絡')}</h2><p>{t('For performance enquiries, festival submissions, interviews and collaborations.','演出洽詢、音樂節提案、採訪與合作，請聯絡我們。')}</p>{link('mailto:'+DATA['email'],esc(DATA['email']),'contact-mail')}{downloads}<div class="epk-checklist" style="margin-top:30px"><div><h3>{t('Included in this edition','本版已收錄')}</h3><ul><li>{t('English and Traditional Chinese biographies','英文及繁體中文團介')}</li><li>{t('Paradise + two live-video links','〈Paradise〉及兩支現場影片連結')}</li><li>{t('Six original photos and show history','六張照片原檔及演出紀錄')}</li></ul></div><div><h3>{t('To complete before submission','正式投遞前待補')}</h3><ul><li>{t('Two additional representative tracks','另外兩首代表作')}</li><li>{t('Confirmed technical rider and set duration','確認過的技術需求與演出長度')}</li><li>{t('Photo credits and publication permissions','照片署名與刊登授權')}</li></ul></div></div><p class="print-only" style="margin-top:20px">Official website: {DATA['website']}<br>Instagram: {DATA['socials']['Instagram']}<br>Booking: {DATA['email']}</p></section>
</div></div></div></main>'''


def band():
    members=''.join(f'''<article class="member-card member-{m['name'].lower().replace(' ','-')}"><img src="{m['photo']}" width="450" height="600" alt="{esc(m['name'])}, {esc(m['role_en'])}" loading="lazy"><h2>{esc(m['name'])}</h2><p>{t(m['role_en'],m['role_zh'])}</p></article>''' for m in DATA['members'])
    return shell('The Band — Lefthand Drive', 'Meet Nick, CY, Julian, Wei Liang and Vijay: the five musicians behind Singapore rock band Lefthand Drive.', f'''<main id="main" class="wrap"><section class="page-hero"><p class="eyebrow">{t('The people behind the sound','聲音背後的五個人')}</p><h1>{t('FIVE IN ONE.','五人，同一個聲音。')}</h1><p class="lead">{t('Different backgrounds. A common language. Meet Lefthand Drive.','不同的背景，共同的音樂語言。這就是 Lefthand Drive。')}</p></section><section class="members-grid" aria-label="Band members">{members}</section><section class="band-story"><p>{t(DATA['bio']['long_en'],DATA['bio']['long_zh'])}</p><div class="actions">{link('index.html#live',t('See us live','觀看現場'),'button primary',PLAY)}{link('epk.html',t('Read the press kit','查看 EPK'),'button')}</div></section></main>''',current='band')


def build():
    (ROOT/'downloads').mkdir(exist_ok=True)
    (ROOT/'index.html').write_text(home(),encoding='utf-8',newline='\n')
    (ROOT/'epk.html').write_text(shell('EPK — Lefthand Drive | English / 繁體中文','Biographies, music, live videos, press photographs and technical information for Lefthand Drive, Singapore.',epk_body(),current='epk'),encoding='utf-8',newline='\n')
    (ROOT/'band.html').write_text(band(),encoding='utf-8',newline='\n')
    bio=DATA['bio']
    bio_md=f"# Lefthand Drive — Biographies / 中英文團介\n\nUpdated: {DATA['updated']}\n\n## Short biography / English\n\n{bio['short_en']}\n\n## 短版團介／繁體中文\n\n{bio['short_zh']}\n\n## Full biography / English\n\n{bio['long_en']}\n\n## 完整團介／繁體中文\n\n{bio['long_zh']}\n\nBooking: {DATA['email']}\nWebsite: {DATA['website']}\n"
    (ROOT/'downloads/Biographies-EN-ZH.md').write_text(bio_md,encoding='utf-8',newline='\n')
    tech=DATA['technical']
    tech_md=f"# Lefthand Drive — Technical discussion draft / 技術需求討論草案\n\nNOT A CONFIRMED RIDER / 尚非正式技術需求表\n\n{tech['note_en']}\n\n{tech['note_zh']}\n\n## Lineup / 編制\n\n{tech['lineup_en']}\n\n{tech['lineup_zh']}\n\n## Equipment to discuss / 待議設備\n\n"+'\n'.join('- '+i['en']+' / '+i['zh'] for i in tech['items'])+f"\n\nSet duration, input list, stage dimensions, backline models, monitor mixes, power, soundcheck and changeover: TO BE CONFIRMED.\n\n演出長度、輸入通道、舞台尺寸、器材型號、監聽路數、電源、試音與換場：待樂團確認。\n\nContact: {DATA['email']}\n"
    (ROOT/'downloads/Technical-Rider-DRAFT.md').write_text(tech_md,encoding='utf-8',newline='\n')
    css=(ROOT/'assets/site.css').read_text(encoding='utf-8')
    css=re.sub(r'^@import[^\n]*\n', '',css,flags=re.MULTILINE)
    portable=f'''<!doctype html><html lang="en" class="bilingual"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lefthand Drive — Bilingual EPK / 中英文資料包</title><style>{css}\n.epk-layout{{display:block}}.no-print,.epk-sidebar{{display:none!important}}.page-hero h1{{font-size:clamp(65px,10vw,120px)}}.wrap{{max-width:1100px}}</style></head><body>{epk_body(offline=True).replace('<details class="bio-long">','<details class="bio-long" open>')}<script>document.querySelectorAll('details').forEach(function(d){{d.open=true}})</script></body></html>'''
    # Embed photos so the HTML can be attached or printed without a server or network.
    for path in sorted((ROOT/'images').iterdir()):
        if path.is_file() and f'src="images/{path.name}"' in portable:
            uri='data:'+mimetypes.guess_type(path.name)[0]+';base64,'+base64.b64encode(path.read_bytes()).decode()
            portable=portable.replace(f'src="images/{path.name}"',f'src="{uri}"')
    portable=re.sub(r'<a [^>]*download[^>]*>.*?</a>','',portable,flags=re.DOTALL)
    (ROOT/'downloads/Lefthand-Drive-EPK.html').write_text(portable,encoding='utf-8',newline='\n')
    instructions=f'''Lefthand Drive — Electronic Press Kit / 樂團資料包
Updated / 更新: {DATA['updated']}

Open Lefthand-Drive-EPK.html in a browser. Both biographies are included. Print or save as PDF using the browser's Print command. Photos are embedded for offline use.
以瀏覽器開啟 Lefthand-Drive-EPK.html，內含中英文團介。可使用瀏覽器列印功能另存 PDF，照片已內嵌，可離線閱讀。

Included: bilingual printable EPK, editable biographies, provisional technical notes, six original photographs.
已收錄：中英文可列印 EPK、可編輯團介、技術需求草案、六張照片原檔。

PENDING: two representative tracks, final technical rider, set duration, photo credits and publication permissions. These are not presented as confirmed.
待補：另外兩首代表作、正式技術需求、演出長度、照片署名與刊登授權。

Videos are online references; no audio-quality certification is implied. Contact the band for original media.
影片為線上參考連結，不代表已通過收音品質認證。原始媒體請洽樂團。

Contact / 聯絡: {DATA['email']}
Website / 官網: {DATA['website']}
'''
    (ROOT/'downloads/READ-ME.txt').write_text(instructions,encoding='utf-8',newline='\n')
    photo_files=['images/group.jpg']+[m['photo'] for m in DATA['members']]
    with zipfile.ZipFile(ROOT/'downloads/Lefthand-Drive-EPK.zip','w',zipfile.ZIP_DEFLATED) as z:
        for file in ['Lefthand-Drive-EPK.html','Biographies-EN-ZH.md','Technical-Rider-DRAFT.md','READ-ME.txt']:
            info=zipfile.ZipInfo(file,tuple(map(int,DATA['updated'].split('-')))+(0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3
            info.external_attr=0o644 << 16
            z.writestr(info,(ROOT/'downloads'/file).read_bytes())
        for file in photo_files:
            info=zipfile.ZipInfo(file,tuple(map(int,DATA['updated'].split('-')))+(0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3
            info.external_attr=0o644 << 16
            z.writestr(info,(ROOT/file).read_bytes())
    print('Built index.html, band.html, epk.html and portable EPK (10 files).')


if __name__=='__main__':
    build()
