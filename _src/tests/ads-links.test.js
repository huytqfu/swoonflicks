// Kiểm đổi link ads trong t.js. Chạy: node _src/tests/ads-links.test.js (Node ≥18, không cần cài gì)
const fs = require('fs'), vm = require('vm'), path = require('path'), assert = require('assert');
const SRC = fs.readFileSync(path.join(__dirname, '..', 't.js'), 'utf8');

function run(search, anchors) {
  const listeners = {}, logs = [];
  const doc = {
    readyState: 'complete', referrer: '', cookie: '', head: { appendChild() {} },
    body: { dataset: {}, appendChild() {} },
    createElement() { return {} }, getElementsByTagName() { return [{ parentNode: { insertBefore() {} } }] },
    addEventListener(t, f) { listeners[t] = f },
    querySelectorAll(sel) { return sel === 'a[data-ads-href]' ? anchors.filter(a => a.dataset.adsHref) : [] }
  };
  const store = {}; const ss = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v) } };
  const ctx = { SF: {}, localStorage: null, sessionStorage: ss, navigator: {}, document: doc,
    location: { search, href: 'https://swoonflicks.com/x/' + search, pathname: '/x/', host: 'swoonflicks.com' },
    URL, URLSearchParams, Intl: { DateTimeFormat: () => ({ resolvedOptions: () => ({ timeZone: 'America/New_York' }) }) },
    Blob: class {}, console, Date, Math, JSON, Object, Array, RegExp, crypto: { randomUUID: () => 'id1' } };
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(SRC.replace('(window, document)', '(this, document)'), ctx);
  const clicks = anchors.map(a => { listeners.click({ target: Object.assign(a, { closest() { return a } }) }); return ctx.sfLog[ctx.sfLog.length - 1][1] });
  return { anchors, clicks };
}
const mk = (slug, ads) => ({ href: 'https://r.reelsgo.tv/org-' + slug, dataset: Object.assign({ aff: 'film', film: slug }, ads ? { adsHref: 'https://r.reelsgo.tv/ads-' + slug } : {}) });

// Ca 1: không gclid → giữ link organic, link_kind = organic
let r = run('', [mk('unbound', true)]);
assert.strictEqual(r.anchors[0].href, 'https://r.reelsgo.tv/org-unbound');
assert.strictEqual(r.clicks[0].link_kind, 'organic');

// Ca 2: có gclid, phim có ads link → đổi sang link ads, link_kind = ads
r = run('?gclid=abc', [mk('unbound', true)]);
assert.strictEqual(r.anchors[0].href, 'https://r.reelsgo.tv/ads-unbound');
assert.strictEqual(r.clicks[0].link_kind, 'ads');

// Ca 3: có gclid nhưng phim không có ads link → giữ organic
r = run('?gclid=abc', [mk('dragons', false)]);
assert.strictEqual(r.anchors[0].href, 'https://r.reelsgo.tv/org-dragons');
assert.strictEqual(r.clicks[0].link_kind, 'organic');

// Phụ: utm_source=google & utm_medium=cpc cũng tính là phiên ads; utm_medium khác thì không
assert.strictEqual(run('?utm_source=google&utm_medium=cpc', [mk('mommy', true)]).anchors[0].href, 'https://r.reelsgo.tv/ads-mommy');
assert.strictEqual(run('?utm_source=google&utm_medium=organic', [mk('mommy', true)]).anchors[0].href, 'https://r.reelsgo.tv/org-mommy');
console.log('ads-links: 5/5 OK');
