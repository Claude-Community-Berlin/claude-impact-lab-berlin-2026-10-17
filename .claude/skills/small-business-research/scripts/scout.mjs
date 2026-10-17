#!/usr/bin/env node
// Collects a small business's public footprint. Zero npm dependencies: needs Node 22+
// and, for `page`/`maps`, a local Chrome/Chromium (driven over the DevTools protocol).
//
//   node scout.mjs page <url> [<url>...] [--check-links] [--max-chars=15000] [--wait=2500]
//   node scout.mjs maps <google-maps-url | "business name, street, city">
//   node scout.mjs instagram <handle | profile-url>
//   node scout.mjs places "<business name, street, city>"   (needs GOOGLE_MAPS_API_KEY)
//
// Prints JSON to stdout. Never tries to get past captchas, bot checks or login walls:
// it reports them as `blocked` so the caller can note the gap and move on.

import { spawn } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [cmd, ...rest] = process.argv.slice(2);
const flags = Object.fromEntries(rest.filter(a => a.startsWith('--')).map(a => {
  const [k, v] = a.slice(2).split('=');
  return [k, v ?? true];
}));
const inputs = rest.filter(a => !a.startsWith('--'));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const BROWSER_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36';
const PREVIEW_UA = 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)';

const BLOCKED_RE = /unusual traffic|verify (that )?you are (a )?human|are you a robot|checking your browser|establishing a secure connection|complete the captcha|attention required|access denied|enable javascript and cookies to continue/i;

const PLATFORMS = {
  instagram: /instagram\.com/, facebook: /facebook\.com|fb\.me/, tiktok: /tiktok\.com/, youtube: /youtube\.com|youtu\.be/,
  linkedin: /linkedin\.com/, x_twitter: /(^|\.)x\.com|twitter\.com/, pinterest: /pinterest\./, whatsapp: /wa\.me|whatsapp\.com/,
  linktree: /linktr\.ee|linkin\.bio/, google_maps: /google\.[a-z.]+\/maps|maps\.app\.goo\.gl|goo\.gl\/maps|g\.page/,
  booking: /treatwell|booksy|fresha|planity|shore\.com|salonized|calendly|doctolib|opentable|quandoo|resmio|thefork|bookatable|sevenrooms|tablein|simplybook|acuityscheduling|setmore|eversports|urban-?sports|timify|etermin/,
  delivery_or_marketplace: /lieferando|wolt\.com|ubereats|deliveroo|etsy\.com|ebay\.|amazon\.|shopify|airbnb|booking\.com|getyourguide/,
  reviews: /tripadvisor|yelp\.|trustpilot|provenexpert|golocal|restaurantguru|wanderlog/,
  events: /eventbrite|rausgegangen|meetup\.com|tixforgigs|ticketmaster|eventim/,
};
const TECH = {
  WordPress: /wp-content|wp-json/, Wix: /wixstatic\.com|wix\.com/, Squarespace: /squarespace/, Shopify: /cdn\.shopify\.com/,
  Webflow: /webflow/, Jimdo: /jimdo/, Framer: /framerusercontent|framer\.com/, Lovable: /lovable\.dev|gptengineer/,
  'IONOS site builder': /mywebsite-editor|ionos/, Strato: /strato/, Weebly: /weebly/, GoDaddy: /godaddy|wsimg\.com/,
};

function findChrome() {
  return [
    process.env.CHROME_PATH,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ].filter(Boolean).find(p => existsSync(p));
}

async function launchBrowser() {
  const bin = findChrome();
  if (!bin) throw new Error('No Chrome/Chromium found. Set CHROME_PATH, or fall back to WebFetch/curl (JS-only sites will look empty).');
  const profile = mkdtempSync(join(tmpdir(), 'scout-'));
  const proc = spawn(bin, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
    '--mute-audio', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--window-size=1280,1800', '--lang=en-US', 'about:blank'],
    { stdio: 'ignore' });
  let port;
  for (let i = 0; i < 150 && !port; i++) {
    await sleep(100);
    const f = join(profile, 'DevToolsActivePort');
    if (existsSync(f)) port = readFileSync(f, 'utf8').split('\n')[0].trim();
  }
  if (!port) { proc.kill(); throw new Error('Chrome did not start'); }
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });

  let nextId = 0;
  const pending = new Map();
  const listeners = new Map();
  ws.addEventListener('message', e => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    if (m.method) for (const cb of listeners.get(m.method) || []) cb(m.params);
  });
  const send = (method, params = {}) => new Promise(r => {
    const id = ++nextId; pending.set(id, r); ws.send(JSON.stringify({ id, method, params }));
  });
  const on = (method, cb) => listeners.set(method, [...(listeners.get(method) || []), cb]);
  const once = method => new Promise(r => {
    const cb = p => { listeners.set(method, listeners.get(method).filter(f => f !== cb)); r(p); };
    on(method, cb);
  });
  const evaluate = async expression => {
    const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description || 'evaluate failed');
    return r.result?.result?.value;
  };

  await send('Network.enable');
  await send('Page.enable');
  const { result: version } = await send('Browser.getVersion');
  await send('Network.setUserAgentOverride', { userAgent: version.userAgent.replace('HeadlessChrome', 'Chrome'), acceptLanguage: 'en-US,en;q=0.9' });
  // Records "reject all" on Google's EU consent screen so Maps loads; this declines tracking, it does not log in.
  for (const domain of ['.google.com', '.google.de']) {
    await send('Network.setCookie', { name: 'SOCS', value: 'CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg', domain, path: '/', secure: true });
  }

  let docStatus = {};
  on('Network.responseReceived', p => { if (p.type === 'Document') docStatus[p.response.url] = p.response.status; });

  async function open(url, waitMs) {
    docStatus = {};
    const loaded = once('Page.loadEventFired');
    await send('Page.navigate', { url });
    await Promise.race([loaded, sleep(20000)]);
    await sleep(waitMs);
    const finalUrl = await evaluate('location.href');
    return { finalUrl, status: docStatus[finalUrl] ?? docStatus[url] ?? Object.values(docStatus).at(-1) ?? null };
  }

  async function close() {
    try { ws.close(); } catch {}
    proc.kill();
    await sleep(300);
    rmSync(profile, { recursive: true, force: true });
  }
  return { open, evaluate, close };
}

function classifyLinks(links, origin) {
  const out = { internal: [], files: [], emails: [], phones: [], platforms: {}, other_external: [] };
  for (const href of links) {
    if (href.startsWith('mailto:')) { out.emails.push(href.slice(7).split('?')[0]); continue; }
    if (href.startsWith('tel:')) { out.phones.push(href.slice(4)); continue; }
    let u; try { u = new URL(href); } catch { continue; }
    if (!/^https?:$/.test(u.protocol)) continue;
    if (u.origin === origin) {
      (/\.(pdf|jpe?g|png|docx?|xlsx?)$/i.test(u.pathname) ? out.files : out.internal).push(u.href.split('#')[0]);
      continue;
    }
    const platform = Object.keys(PLATFORMS).find(k => PLATFORMS[k].test(u.hostname + u.pathname));
    if (platform) (out.platforms[platform] ||= []).push(u.href);
    else out.other_external.push(u.href);
  }
  for (const k of Object.keys(out)) if (Array.isArray(out[k])) out[k] = [...new Set(out[k])];
  for (const k of Object.keys(out.platforms)) out.platforms[k] = [...new Set(out.platforms[k])];
  return out;
}

async function rawHtml(url) {
  try {
    const r = await fetch(url, { headers: { 'user-agent': BROWSER_UA }, redirect: 'follow' });
    return { status: r.status, html: await r.text() };
  } catch (e) { return { status: null, html: '', error: String(e) }; }
}
const textOf = html => html.replace(/<(script|style|noscript)[^>]*>[\s\S]*?<\/\1>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

async function scoutPage() {
  if (!inputs.length) throw new Error('usage: scout.mjs page <url> [<url>...]');
  const maxChars = Number(flags['max-chars'] || 15000);
  const waitMs = Number(flags.wait || 2500);
  const b = await launchBrowser();
  const results = [];
  try {
    for (const url of inputs) {
      const { finalUrl, status } = await b.open(url, waitMs);
      // Scroll to the bottom so lazy-loaded sections render.
      await b.evaluate(`(async () => { for (let y = 0; y < document.body.scrollHeight && y < 30000; y += 900) { scrollTo(0, y); await new Promise(r => setTimeout(r, 150)); } scrollTo(0, 0); })()`);
      await new Promise(r => setTimeout(r, 800));
      const page = await b.evaluate(`(() => {
        const meta = {};
        document.querySelectorAll('meta[name], meta[property]').forEach(m => {
          const k = m.getAttribute('name') || m.getAttribute('property');
          if (/^(description|generator|author|keywords|og:|twitter:site)/i.test(k)) meta[k] = m.content;
        });
        const jsonld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => { try { return JSON.parse(s.textContent); } catch { return s.textContent.slice(0, 2000); } });
        return {
          title: document.title, lang: document.documentElement.lang || null, meta, jsonld,
          headings: [...document.querySelectorAll('h1,h2,h3')].map(h => h.innerText.trim()).filter(Boolean).slice(0, 60),
          text: document.body ? document.body.innerText : '',
          links: [...document.querySelectorAll('a[href]')].map(a => a.href),
          iframes: [...document.querySelectorAll('iframe[src]')].map(f => f.src),
          images_without_alt: [...document.querySelectorAll('img')].filter(i => !i.alt).length,
          html: document.documentElement.outerHTML.slice(0, 400000),
        };
      })()`);
      const origin = new URL(finalUrl).origin;
      const raw = await rawHtml(finalUrl);
      const rawText = textOf(raw.html);
      const tech = Object.keys(TECH).filter(k => TECH[k].test(page.html + JSON.stringify(page.meta)));
      const entry = {
        url, final_url: finalUrl, status, title: page.title, lang: page.lang, meta: page.meta,
        blocked: BLOCKED_RE.test(page.text.slice(0, 3000)),
        tech,
        needs_javascript: rawText.length < 300 && page.text.length > 800,
        raw_html_text_chars: rawText.length, rendered_text_chars: page.text.length,
        headings: page.headings, jsonld: page.jsonld,
        links: classifyLinks([...page.links, ...page.iframes], origin),
        images_without_alt: page.images_without_alt,
        text: page.text.length > maxChars ? page.text.slice(0, maxChars) + `\n…[truncated, ${page.text.length} chars total]` : page.text,
      };
      if (flags['check-links']) {
        // Fetch each internal page directly (no JS). JS-only sites often 404 on direct visits:
        // shared links, Google results and legal pages (Impressum) then break.
        const targets = [...entry.links.internal, ...entry.links.files].filter(u => new URL(u).pathname !== '/').slice(0, 30);
        entry.link_check = [];
        for (const u of targets) {
          const r = await rawHtml(u);
          entry.link_check.push({ url: u, status: r.status });
        }
      }
      results.push(entry);
    }
  } finally { await b.close(); }
  return results.length === 1 ? results[0] : results;
}

// The panel lists reviews (with reviewer names) after the "Sort" button. Keep the summary above it
// and the topic chips right after it ("Alle / bar 15 / abend 6 / … / +6"), drop the rest.
function splitPanel(text) {
  const m = text.match(/\n\s*(Sort|Sortieren|Trier|Ordenar|Ordina|Sorteren)\s*\n/);
  if (!m) return { panel_text: text, review_topics: [] };
  // Maps renders icons as private-use glyphs; strip them so they don't break the line pairing.
  const tail = text.slice(m.index + m[0].length).split('\n')
    .map(s => s.replace(/[-​-‏]/g, '').trim()).filter(Boolean).slice(0, 40);
  const review_topics = [];
  for (let i = 0; i < tail.length; i++) {
    if (/^\+\d+$/.test(tail[i])) break;
    if (/^[\d.,]+$/.test(tail[i + 1] || '')) { review_topics.push(`${tail[i]} (${tail[i + 1]})`); i++; }
    else if (review_topics.length) break;
  }
  return { panel_text: text.slice(0, m.index), review_topics };
}

async function scoutMaps() {
  const q = inputs.join(' ');
  if (!q) throw new Error('usage: scout.mjs maps <google-maps-url | "name, street, city">');
  const url = /^https?:\/\//.test(q) ? q : `https://www.google.com/maps/search/${encodeURIComponent(q)}`;
  // Google's logged-out Maps alternates between a full view (Reviews tab, review texts) and a
  // "limited view" (rating, a few quoted snippets, no review list). It varies per load, so retry once.
  const extract = `(async () => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const main = document.querySelector('div[role=main]') || document.body;
    const weekdays = /monday|tuesday|wednesday|thursday|friday|saturday|sunday|montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag/gi;
    const details = {};
    main.querySelectorAll('[data-item-id]').forEach(el => {
      const label = el.getAttribute('aria-label') || el.innerText;
      if (label) details[el.getAttribute('data-item-id').split(':')[0]] = label.trim();
    });
    const hours = [...main.querySelectorAll('[aria-label]')].map(e => e.getAttribute('aria-label'))
      .map(l => [l, (l.match(weekdays) || []).length]).sort((a, b) => b[1] - a[1]).find(([, n]) => n > 0)?.[0]
      || main.querySelector('table')?.innerText || null;
    const info = {
      name: main.querySelector('h1')?.innerText || null,
      rating_summary: main.querySelector('div.F7nice')?.innerText.replace(/\\s+/g, ' ') || null,
      category: main.querySelector('button[jsaction*="category"]')?.innerText || null,
      details, hours,
      panel_text: main.innerText.slice(0, 6000),
      limited_view: /limited view of Google Maps|Ansicht ist beschränkt|vue limitée|vista limitada|visualizzazione limitata/i.test(document.body.innerText),
    };
    const reviewWord = /review|rezension|bewertung|avis|reseñ|recensi|beoordel/i;
    const tab = [...document.querySelectorAll('[role=tab]')].find(b => reviewWord.test((b.getAttribute('aria-label') || '') + b.innerText));
    info.reviews = [];
    if (tab) {
      tab.click(); await sleep(2500);
      const pane = () => [...document.querySelectorAll('div.m6QErb')].find(d => d.scrollHeight > d.clientHeight + 50);
      for (let i = 0; i < 12; i++) { const p = pane(); if (!p) break; p.scrollTop = p.scrollHeight; await sleep(700); }
      document.querySelectorAll('button.w8nwRe').forEach(b => b.click());
      await sleep(500);
      const seen = new Set();
      // Reviewer names are deliberately not collected.
      info.reviews = [...document.querySelectorAll('[data-review-id]')].map(el => ({
        id: el.getAttribute('data-review-id'),
        rating: [...el.querySelectorAll('[role=img][aria-label]')].map(i => i.getAttribute('aria-label')).find(l => /\\d/.test(l)) || null,
        date: el.querySelector('.rsqaWe')?.innerText || null,
        text: el.querySelector('.wiI7pd')?.innerText || null,
        owner_reply: el.querySelector('.CDe7pd')?.innerText || null,
      })).filter(r => r.id && (r.text || r.rating) && !seen.has(r.id) && seen.add(r.id)).map(({ id, ...r }) => r);
    }
    return info;
  })()`;
  const b = await launchBrowser();
  try {
    let { finalUrl } = await b.open(url, 5000);
    // A search that matches several places shows a list; follow the first match.
    const candidates = await b.evaluate(`[...document.querySelectorAll('a[href*="/maps/place/"]')].map(a => ({ name: a.getAttribute('aria-label'), url: a.href })).slice(0, 5)`);
    if (!finalUrl.includes('/maps/place/') && candidates.length) ({ finalUrl } = await b.open(candidates[0].url, 5000));
    let data = await b.evaluate(extract);
    if (!data.reviews.length) {
      ({ finalUrl } = await b.open(finalUrl, 5000));
      const retry = await b.evaluate(extract);
      if (retry.reviews.length || !retry.limited_view) data = retry;
    }
    const blocked = BLOCKED_RE.test(data.panel_text) || /consent\.google|sorry\/index/.test(finalUrl);
    Object.assign(data, splitPanel(data.panel_text));
    return {
      query: q, final_url: finalUrl, blocked, other_candidates: candidates.slice(1), ...data,
      note: data.reviews.length ? undefined : (data.limited_view
        ? 'Google served its logged-out "limited view": rating, review count and a few quoted snippets, but no review list. Try again later, use `places` (API key), a signed-in browser, or other review sites.'
        : 'No reviews extracted; the Reviews tab was missing or its layout changed. panel_text may still hold quoted snippets.'),
    };
  } finally { await b.close(); }
}

function parseCount(s) {
  if (!s) return null;
  const m = s.trim().match(/^([\d.,]+)\s*([KkMm]?)/);
  if (!m) return null;
  let n = m[1];
  if (m[2]) n = n.replace(',', '.'); else n = n.replace(/[.,](?=\d{3}\b)/g, '');
  return Math.round(parseFloat(n) * (/k/i.test(m[2]) ? 1e3 : /m/i.test(m[2]) ? 1e6 : 1));
}

async function scoutInstagram() {
  const handle = (inputs[0] || '').replace(/^https?:\/\/(www\.)?instagram\.com\//, '').replace(/^@/, '').split(/[/?]/)[0];
  if (!handle) throw new Error('usage: scout.mjs instagram <handle | profile-url>');
  const url = `https://www.instagram.com/${handle}/`;
  // Instagram serves logged-out browsers a login wall, but gives link-preview crawlers the profile's meta tags.
  const r = await fetch(url, { headers: { 'user-agent': PREVIEW_UA, 'accept-language': 'en-US,en;q=0.9' } });
  const html = await r.text();
  const meta = name => {
    const m = html.match(new RegExp(`<meta[^>]+property="${name}"[^>]+content="([^"]*)"`));
    return m ? m[1].replace(/&#064;/g, '@').replace(/&#x2022;/g, '•').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#039;/g, "'") : null;
  };
  const title = meta('og:title');
  const desc = meta('og:description');
  const grab = re => parseCount(desc?.match(re)?.[1]);
  const followers = grab(/([\d.,]+\s*[KkMm]?)\s+Followers/);
  const following = grab(/([\d.,]+\s*[KkMm]?)\s+Following/);
  return {
    handle, url, http_status: r.status, found: Boolean(desc),
    display_name: title?.replace(/\s*\(@.*$/, '') || null,
    followers, following, posts: grab(/([\d.,]+\s*[KkMm]?)\s+Posts/),
    following_to_followers: followers && following != null ? +(following / followers).toFixed(2) : null,
    og_description: desc,
    note: 'Logged-out access exposes only these counts. Bio, post dates and captions need a signed-in browser or a search for the handle.',
  };
}

async function scoutPlaces() {
  const key = process.env.GOOGLE_MAPS_API_KEY || process.env.GOOGLE_PLACES_API_KEY;
  if (!key) return { available: false, note: 'Set GOOGLE_MAPS_API_KEY (Places API (New) enabled) to get rating, review count and up to 5 review texts.' };
  const fields = ['id', 'displayName', 'formattedAddress', 'primaryTypeDisplayName', 'types', 'rating', 'userRatingCount', 'reviews',
    'regularOpeningHours.weekdayDescriptions', 'websiteUri', 'nationalPhoneNumber', 'googleMapsUri', 'priceLevel', 'editorialSummary', 'businessStatus']
    .map(f => 'places.' + f).join(',');
  const r = await fetch('https://places.googleapis.com/v1/places:searchText', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'X-Goog-Api-Key': key, 'X-Goog-FieldMask': fields },
    body: JSON.stringify({ textQuery: inputs.join(' '), languageCode: 'en' }),
  });
  const body = await r.json();
  if (!r.ok) return { available: false, http_status: r.status, error: body.error?.message || body };
  return {
    available: true,
    places: (body.places || []).slice(0, 3).map(p => ({
      name: p.displayName?.text, address: p.formattedAddress, type: p.primaryTypeDisplayName?.text, types: p.types,
      rating: p.rating, review_count: p.userRatingCount, price_level: p.priceLevel, status: p.businessStatus,
      summary: p.editorialSummary?.text, website: p.websiteUri, phone: p.nationalPhoneNumber, maps_url: p.googleMapsUri,
      hours: p.regularOpeningHours?.weekdayDescriptions,
      // Google returns at most 5 reviews ("most relevant"); author names are dropped on purpose.
      reviews: (p.reviews || []).map(v => ({
        rating: v.rating, when: v.relativePublishTimeDescription, published: v.publishTime,
        text: v.originalText?.text || v.text?.text, language: v.originalText?.languageCode || v.text?.languageCode,
      })),
    })),
  };
}

const commands = { page: scoutPage, maps: scoutMaps, instagram: scoutInstagram, places: scoutPlaces };
if (!commands[cmd]) {
  console.error('usage: scout.mjs <page|maps|instagram|places> ...');
  process.exit(2);
}
try {
  console.log(JSON.stringify(await commands[cmd](), null, 2));
} catch (e) {
  console.log(JSON.stringify({ error: String(e.message || e) }));
  process.exit(1);
}
