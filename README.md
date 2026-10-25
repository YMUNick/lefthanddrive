# Lefthand Drive

Official static website and bilingual EPK for the five-piece rock band based in Singapore.

Website: https://ymunick.github.io/lefthanddrive/
Contact: mrwaitforplayers@gmail.com

## Edit content / 更新內容

Edit content/band.json, then rebuild. This is the shared source for biographies, members, music, live videos, shows and technical notes. Generated HTML and downloads are committed for GitHub Pages.

    python scripts/build.py
    node --test tests/site.test.mjs
    python scripts/check.py
    python -m http.server 8765

Open http://localhost:8765. Python 3.10+ and Node 18+ are sufficient; no package installation is needed. GitHub Pages can serve the root of main after merging the PR.

The site supports English and Traditional Chinese, responsive layouts, keyboard navigation, reduced motion, deferred YouTube players and print styles. Language preference is stored only in the browser. Show labels use Singapore dates and retain month-only precision.

## EPK / 樂團介紹包

The ZIP in downloads/ includes a portable HTML EPK with embedded photos, editable English and Chinese biographies, technical discussion notes, six original photos and a readme. Open the HTML in a browser and use Print / Save as PDF. The online edition is epk.html.

### Still needed / 待樂團提供

1. Titles and listening links for two additional tracks. Replace the two pending entries in tracks with title, HTTPS url and status: published.
2. Final technical rider, input list, equipment, monitors, power, soundcheck, changeover and set duration. The present stage plan is a proposal, not a band-approved specification.
3. Photographer credits and publication permissions.

The band supplied the second video tLV0B2nNNFU. Its YouTube title is 9 October 2026; no event date or venue is inferred. Audio quality has not been certified.

## Files

- scripts/build.py: generates the three pages and EPK downloads.
- scripts/check.py: checks internal links and archive integrity.
- assets/site.css: responsive editorial design and print layout.
- assets/site.mjs: language, navigation, show labels and videos.
- assets/core.mjs: tested date/language helpers.
- booking.html and google-apps-script.js: existing rehearsal service, preserved.
- UI/: historical Spotify-inspired reference files, retained.

The homepage record graphic is decorative, not official cover artwork. Real band photographs and music links carry the band's identity.
