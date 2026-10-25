import { normalizeLanguage, singaporeDate, classifyShow } from './core.mjs';

const root = document.documentElement;
const storageKey = 'lefthanddrive-language';
const toggle = document.querySelector('[data-language-toggle]');
let language = 'en';
try { language = normalizeLanguage(localStorage.getItem(storageKey)); } catch { /* Storage is optional. */ }

function setLanguage(value) {
  language = normalizeLanguage(value);
  root.lang = language;
  if (toggle) {
    toggle.textContent = language === 'en' ? '繁中' : 'EN';
    toggle.setAttribute('aria-label', language === 'en' ? 'Switch to Traditional Chinese' : 'Switch to English');
  }
  const menu = document.querySelector('.menu-toggle');
  if (menu) menu.setAttribute('aria-label', language === 'en' ? 'Open navigation' : '開啟導覽');
  const motionToggle = document.querySelector('[data-marquee-toggle]');
  if (motionToggle) {
    const paused = motionToggle.getAttribute('aria-pressed') === 'true';
    motionToggle.setAttribute('aria-label', language === 'en' ? (paused ? 'Resume text animation' : 'Pause text animation') : (paused ? '繼續文字動畫' : '暫停文字動畫'));
  }
  try { localStorage.setItem(storageKey, language); } catch { /* Content remains usable in private modes. */ }
}
setLanguage(language);
toggle?.addEventListener('click', () => setLanguage(language === 'en' ? 'zh-Hant' : 'en'));

const motionToggle = document.querySelector('[data-marquee-toggle]');
if (motionToggle) {
  const marquee = motionToggle.closest('.marquee');
  motionToggle.hidden = false;
  marquee.classList.add('is-animated');
  motionToggle.addEventListener('click', () => {
    const paused = marquee.classList.toggle('is-paused');
    motionToggle.setAttribute('aria-pressed', String(paused));
    motionToggle.setAttribute('aria-label', language === 'en' ? (paused ? 'Resume text animation' : 'Pause text animation') : (paused ? '繼續文字動畫' : '暫停文字動畫'));
  });
}

const menuButton = document.querySelector('.menu-toggle');
const mobileMenu = document.querySelector('#mobile-menu');
function closeMenu(restoreFocus = false) {
  if (!menuButton || !mobileMenu) return;
  mobileMenu.hidden = true;
  menuButton.setAttribute('aria-expanded','false');
  document.body.classList.remove('menu-open');
  menuButton.setAttribute('aria-label', language === 'en' ? 'Open navigation' : '開啟導覽');
  if (restoreFocus) menuButton.focus();
}
menuButton?.addEventListener('click', () => {
  const opening = mobileMenu.hidden;
  mobileMenu.hidden = !opening;
  menuButton.setAttribute('aria-expanded',String(opening));
  menuButton.setAttribute('aria-label', opening ? (language === 'en' ? 'Close navigation' : '關閉導覽') : (language === 'en' ? 'Open navigation' : '開啟導覽'));
  document.body.classList.toggle('menu-open',opening);
});
mobileMenu?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && mobileMenu && !mobileMenu.hidden) closeMenu(true);
  // Keep focus inside the expanded mobile header; the menu is visually modal.
  if (event.key === 'Tab' && mobileMenu && !mobileMenu.hidden) {
    const focusable = [...document.querySelectorAll('.header-inner a, .header-inner button')].filter(el => el.getClientRects().length);
    const first = focusable[0], last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
});
window.matchMedia('(min-width:1101px)').addEventListener('change', event => { if (event.matches) closeMenu(); });

const statusLabels={past:['Past','已演出'],today:['Today','今日演出'],upcoming:['Upcoming','即將演出'],announced:['Date TBC','日期待確認']};
const today=singaporeDate();
document.querySelectorAll('[data-show-date]').forEach(row=>{
  const status=classifyShow({date:row.dataset.showDate},today);
  const badge=row.querySelector('.show-status');
  badge.dataset.status=status;
  badge.querySelector('[data-lang=en]').textContent=statusLabels[status][0];
  badge.querySelector('[data-lang=zh-Hant]').textContent=statusLabels[status][1];
});
document.querySelectorAll('[data-year]').forEach(el=>{el.textContent=today.slice(0,4);});

document.querySelectorAll('[data-video]').forEach(button=>{
  button.addEventListener('click',()=>{
    const id=button.dataset.video;
    if (!/^[a-zA-Z0-9_-]{11}$/.test(id)) return;
    const frame=document.createElement('iframe');
    frame.src=`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
    frame.title=button.getAttribute('aria-label');
    frame.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';
    frame.allowFullscreen=true;
    frame.referrerPolicy='strict-origin-when-cross-origin';
    frame.tabIndex=0;
    button.closest('.video-stage').replaceChildren(frame);
    frame.focus();
  });
});

document.querySelector('[data-print]')?.addEventListener('click',()=>window.print());
let printLanguage;
window.addEventListener('beforeprint',()=>{
  printLanguage=root.lang;
  // The printed EPK includes both biographies, in either interface language.
  document.querySelectorAll('.bio-long').forEach(details=>{details.dataset.wasOpen=String(details.open);details.open=true;});
});
window.addEventListener('afterprint',()=>{
  if (printLanguage) root.lang=printLanguage;
  document.querySelectorAll('.bio-long').forEach(details=>{details.open=details.dataset.wasOpen==='true';});
});
