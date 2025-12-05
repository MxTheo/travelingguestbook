const COOKIE_NAME = 'site_cookie_consent_v1';
const EXPIRES_DAYS = 365;

function setCookieJSON(name, obj, days) {
  const value = encodeURIComponent(JSON.stringify(obj));
  const maxAge = (days||0) * 24 * 60 * 60;
  document.cookie = `${name}=${value}; path=/; SameSite=Lax; max-age=${maxAge}; ${location.protocol==='https:'?'Secure':''}`;
}
function getCookieJSON(name) {
  const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  if (!m) return null;
  try { return JSON.parse(decodeURIComponent(m[2])); } catch { return null; }
}
function deleteCookie(name) {
  document.cookie = name + '=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax;';
}

function applyConsent(consent) {
  window.cookieConsent = consent || { necessary: true };
  if (consent && consent.analytics) loadAnalytics();
}

function showBanner() { document.getElementById('cookie-consent').hidden = false; }
function hideBanner() { document.getElementById('cookie-consent').hidden = true; }

// load analytics only when GA id present and consent.analytics true
function loadAnalytics() {
  if (window._analyticsLoaded) return;
  const banner = document.getElementById('cookie-consent');
  const gaId = banner && banner.dataset && banner.dataset.ga ? banner.dataset.ga : '';
  if (!gaId) return;
  const s = document.createElement('script');
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  window.gtag = gtag;
  gtag('js', new Date());
  gtag('config', gaId, { 'anonymize_ip': true });
  window._analyticsLoaded = true;
}

document.addEventListener('DOMContentLoaded', () => {
  const existing = getCookieJSON(COOKIE_NAME);
  if (existing) {
    applyConsent(existing);
  } else {
    showBanner();
  }

  document.getElementById('cc-manage').addEventListener('click', () => {
    const panel = document.getElementById('cc-panel');
    panel.hidden = !panel.hidden;
  });

  document.getElementById('cc-accept-all').addEventListener('click', () => {
    const consent = { necessary: true, functional: true, analytics: true, marketing: true };
    setCookieJSON(COOKIE_NAME, consent, EXPIRES_DAYS);
    applyConsent(consent);
    hideBanner();
  });

  document.getElementById('cc-reject').addEventListener('click', () => {
    const consent = { necessary: true, functional: false, analytics: false, marketing: false };
    setCookieJSON(COOKIE_NAME, consent, EXPIRES_DAYS);
    applyConsent(consent);
    hideBanner();
  });

  document.getElementById('cc-save').addEventListener('click', () => {
    const form = document.getElementById('cc-form');
    const consent = {
      necessary: true,
      functional: !!form.elements['functional'].checked,
      analytics: !!form.elements['analytics'].checked,
      marketing: !!form.elements['marketing'].checked
    };
    setCookieJSON(COOKIE_NAME, consent, EXPIRES_DAYS);
    applyConsent(consent);
    hideBanner();
  });

  document.getElementById('cc-revoke').addEventListener('click', () => {
    // intrekken: verwijder cookie en (optioneel) meld server
    deleteCookie(COOKIE_NAME);
    window.cookieConsent = { necessary: true };
    // je kunt server endpoint aanroepen om dit te loggen; hier reloaden we de pagina
    location.reload();
  });

  document.getElementById('cc-cancel').addEventListener('click', () => {
    document.getElementById('cc-panel').hidden = true;
  });
});