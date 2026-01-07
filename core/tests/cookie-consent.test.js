/* eslint-env jest */

describe('cookie-consent.js (frontend)', () => {
  const COOKIE_NAME = 'site_cookie_consent_v1';
  let originalDocument;
  let originalLocation;
  let handlers;
  let elements;
  let appendedScripts;
  let originalCookieDescriptor; 

  beforeEach(() => {
    jest.resetModules();

    originalDocument = global.document;
    originalLocation = global.location;

    handlers = {};
    appendedScripts = [];

    const makeEl = (id) => ({
      id,
      dataset: {},
      hidden: true,
      addEventListener: jest.fn((evt, cb) => { handlers[`${id}:${evt}`] = cb; }),
      removeEventListener: jest.fn()
    });

    elements = {
      'cookie-consent': makeEl('cookie-consent'),
      'cc-manage': makeEl('cc-manage'),
      'cc-accept-all': makeEl('cc-accept-all'),
      'cc-reject': makeEl('cc-reject'),
      'cc-save': makeEl('cc-save'),
      'cc-revoke': makeEl('cc-revoke'),
      'cc-cancel': makeEl('cc-cancel'),
      'cc-panel': makeEl('cc-panel'),
      'cc-form': { elements: {
        functional: { checked: false },
        analytics: { checked: false },
        marketing: { checked: false }
      }, addEventListener: jest.fn() }
    };

    // Use spies on the real jsdom document rather than replacing it entirely
    // emulate cookie storage so tests observe deletions correctly
    let cookieStore = '';
    originalCookieDescriptor = Object.getOwnPropertyDescriptor(global.document, 'cookie');
    Object.defineProperty(global.document, 'cookie', {
      configurable: true,
      get: () => cookieStore,
      set: (val) => {
        // basic assignment parsing to support set and delete semantics
        const m = String(val).match(/^\s*([^=;]+)=([^;]*)/);
        if (!m) return;
        const name = m[1];
        const value = m[2];
        // deletion if expires in the past or max-age=0
        if (/expires=Thu, 01 Jan 1970|max-age=0/i.test(val)) {
          const re = new RegExp('(?:^|;\\s*)' + name + '=[^;]*');
          cookieStore = cookieStore.replace(re, '').replace(/(^;\\s*)|(;\\s*$)/g, '').trim();
        } else {
          const re = new RegExp('(?:^|;\\s*)' + name + '=[^;]*');
          cookieStore = cookieStore.replace(re, '').replace(/(^;\\s*)|(;\\s*$)/g, '').trim();
          cookieStore = cookieStore ? cookieStore + '; ' + name + '=' + value : name + '=' + value;
        }
      }
    });
    jest.spyOn(global.document.head, 'appendChild').mockImplementation((n) => appendedScripts.push(n));
    jest.spyOn(global.document, 'addEventListener').mockImplementation((evt, cb) => {
      if (evt === 'DOMContentLoaded') cb();
    });
    jest.spyOn(global.document, 'getElementById').mockImplementation((id) => elements[id] || null);

    // Ensure location.reload is mockable; some jsdom environments make it non-writable
    try {
      global.location.reload = jest.fn();
      global.location.protocol = 'http:';
    } catch (e) {
      Object.defineProperty(global, 'location', {
        value: Object.assign({}, originalLocation, { reload: jest.fn(), protocol: 'http:' }),
        writable: true,
      });
    }

    delete global.window.cookieConsent;
    delete global.window.gtag;
    delete global.window._analyticsLoaded;
  });

  afterEach(() => {
    // restore original cookie descriptor if we replaced it
    if (originalCookieDescriptor) {
      Object.defineProperty(global.document, 'cookie', originalCookieDescriptor);
    } else {
      delete global.document.cookie;
    }
    global.document = originalDocument;
    global.location = originalLocation;
    jest.restoreAllMocks();
  });


  test('shows banner when no cookie exists', () => {
    require('../../static/js/cookie-consent.js');
    // sanity check: the cookie banner element should have been queried and updated
    expect(global.document.getElementById).toHaveBeenCalledWith('cookie-consent');
    expect(elements['cookie-consent'].hidden).toBe(false);
  });

  test('applies existing consent and loads analytics when analytics true and GA id present', () => {
    const consent = { necessary: true, analytics: true };
    global.document.cookie = `${COOKIE_NAME}=${encodeURIComponent(JSON.stringify(consent))}; path=/;`;
    elements['cookie-consent'].dataset.ga = 'G-TEST';

    require('../../static/js/cookie-consent.js');

    expect(global.window.cookieConsent).toEqual(consent);
    expect(appendedScripts.length).toBe(1);
    expect(typeof global.window.gtag).toBe('function');
    expect(global.window._analyticsLoaded).toBe(true);
  });

  test('accept-all sets cookie, applies consent and hides banner', () => {
    require('../../static/js/cookie-consent.js');
    const handler = handlers['cc-accept-all:click'];
    expect(typeof handler).toBe('function');

    handler();

    expect(global.document.cookie).toMatch(new RegExp(`${COOKIE_NAME}=`));
    expect(global.window.cookieConsent).toMatchObject({ analytics: true, marketing: true, functional: true });
    expect(elements['cookie-consent'].hidden).toBe(true);
  });

  test('reject sets cookie (no analytics) and hides banner', () => {
    require('../../static/js/cookie-consent.js');
    const handler = handlers['cc-reject:click'];
    handler();

    expect(global.document.cookie).toMatch(new RegExp(`${COOKIE_NAME}=`));
    expect(global.window.cookieConsent.analytics).toBe(false);
    expect(elements['cookie-consent'].hidden).toBe(true);
  });

  test('save reads form values, sets cookie and hides banner', () => {
    elements['cc-form'].elements.functional.checked = true;
    elements['cc-form'].elements.analytics.checked = false;
    elements['cc-form'].elements.marketing.checked = true;

    require('../../static/js/cookie-consent.js');
    const handler = handlers['cc-save:click'];
    handler();

    expect(global.document.cookie).toMatch(new RegExp(`${COOKIE_NAME}=`));
    expect(global.window.cookieConsent).toMatchObject({ functional: true, analytics: false, marketing: true });
    expect(elements['cookie-consent'].hidden).toBe(true);
  });

  test('manage toggles the cc-panel hidden state', () => {
    require('../../static/js/cookie-consent.js');
    const handler = handlers['cc-manage:click'];

    expect(elements['cc-panel'].hidden).toBe(true);
    handler();
    expect(elements['cc-panel'].hidden).toBe(false);
    handler();
    expect(elements['cc-panel'].hidden).toBe(true);
  });

  test('loadAnalytics does nothing when GA id missing and avoids double loads', () => {
    require('../../static/js/cookie-consent.js');
    const accept = handlers['cc-accept-all:click'];
    accept();
    expect(appendedScripts.length).toBe(0);

    elements['cookie-consent'].dataset.ga = 'G-NEW';
    elements['cc-form'].elements.analytics.checked = true;
    const save = handlers['cc-save:click'];
    save();

    expect(appendedScripts.length).toBe(1);
    expect(global.window._analyticsLoaded).toBe(true);

    const acceptAgain = handlers['cc-accept-all:click'];
    acceptAgain();
    expect(appendedScripts.length).toBe(1);
  });
});
