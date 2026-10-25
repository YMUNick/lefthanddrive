# Lefthand Drive: international website and EPK

## Purpose
Give listeners a strong introduction to the band and help festival programmers, venues and funding assessors find verified music, live footage, biographies, photos and production information.

## Design decision
Use an editorial rock direction: charcoal, warm paper, a restrained acid-yellow accent, oversized condensed headlines, authentic photography, generous spacing and fine rules. Keep the existing static GitHub Pages deployment; no framework or runtime service is needed. English is the initial language, with a persistent Traditional Chinese option. The existing rehearsal-room booking service stays available through an explicitly labelled link.

## Deliverables
- Rebuilt home and band pages, shared accessible responsive styling and mobile navigation.
- A bilingual EPK page and downloadable self-contained ZIP: printable bilingual EPK, editable biographies, original photographs and clearly marked provisional technical information.
- Three repertoire slots and two live-video slots. Only the existing Paradise track and Phil Studio live video are verified; other slots explicitly await band-supplied material. Do not fabricate titles, reviews, awards, audiences, nationalities, set duration or confirmed equipment.
- Show status determined from Singapore calendar dates. Month-only historical dates must retain their precision.
- Lightweight local generation script and tests for date, language and content integrity. Check real pages at desktop and mobile sizes, language persistence, navigation, downloads and print presentation.

## Execution
1. Test date/language behaviour, implement shared content and helpers.
2. Build the static pages and downloadable EPK from one content file.
3. Verify links, photos, responsive rendering, keyboard/menu behaviour and bilingual print layout; obtain an independent code review.
4. Commit and propose the change through a GitHub pull request, preserving the live main branch for review.
