/* Functional smoke test, injected after the app's own script.
   Top-level const/let of a classic script live in the shared global lexical scope,
   so GAZE / state / route / pickSite / sanitise are all reachable from here.

   ⚠️ NOT EXECUTED during this review: Chrome and Edge cannot start under the review
   sandbox (they need named-pipe IPC for their multi-process architecture). Everything
   here is written against the real code but has never actually run — treat it as a
   suite to run yourself, and expect to adjust a selector or two on the first pass.

   Run it with:
     python tools/make_selftest.py
     python -m http.server 8123 --directory tools/site
     # open http://127.0.0.1:8123/ and read the <pre id="RESULTS"> block
*/
(function () {
  const out = [];
  const ok = (n, c, extra) => out.push((c ? 'PASS' : 'FAIL') + ' :: ' + n + (extra ? ' :: ' + extra : ''));
  const t = (n, fn) => { try { fn(); ok(n, true); } catch (e) { ok(n, false, e.message); } };
  const eq = (n, a, b) => ok(n, a === b, 'got ' + JSON.stringify(a) + ' want ' + JSON.stringify(b));
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const fire = (el, type) => el.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true }));

  /* ---------- 1. init rendered everything ---------- */
  t('12 category cards built', () => { if ($$('#cat-grid .cat').length !== 12) throw new Error('got ' + $$('#cat-grid .cat').length); });
  t('12 quick-add chips built', () => { if ($$('#quick-add .chipbtn').length !== 12) throw new Error('got ' + $$('#quick-add .chipbtn').length); });
  t('4 avatar options built', () => { if ($$('#avatar-picker .av-opt').length !== 4) throw new Error('got ' + $$('#avatar-picker .av-opt').length); });
  t('6 badges rendered', () => { if ($$('#badge-row .badge').length !== 6) throw new Error('got ' + $$('#badge-row .badge').length); });
  t('city select populated', () => { if ($$('#f-city option').length < 10) throw new Error('got ' + $$('#f-city option').length); });
  t('copyright year set', () => { if (!/^\d{4}$/.test($('#yr').textContent)) throw new Error('yr=' + $('#yr').textContent); });
  t('date min == LOCAL today', () => {
    const d = new Date();
    const want = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    if ($('#f-date').min !== want) throw new Error('min=' + $('#f-date').min + ' want=' + want);
  });
  t('empty history message shown', () => { if ($('#empty-history').hidden) throw new Error('hidden'); });

  /* ---------- 2. the gaze engine actually ran ---------- */
  t('GAZE engine exposed and always running', () => {
    if (!GAZE || typeof GAZE.start !== 'function') throw new Error('GAZE missing');
    if ($('#gaze-toggle')) throw new Error('the pause button was supposed to be removed');
  });
  t('rAF loop wrote the 3D transform', () => {
    const tr = $('#child-3d').style.transform;
    if (!tr || tr.indexOf('perspective') !== 0) throw new Error('transform=' + JSON.stringify(tr));
  });
  t('rAF loop wrote blink heights', () => {
    const lids = $$('#child-stage .lid');
    if (lids.length !== 2) throw new Error('lids=' + lids.length);
    for (const l of lids) if (l.getAttribute('height') === null) throw new Error('height attr never set');
  });
  t('rAF loop moved pupils', () => {
    for (const p of $$('#child-stage .pupil-g')) if (p.getAttribute('transform') === null) throw new Error('pupil transform never set');
  });
  t('the companion caption is gone and nothing replaced it', () => {
    if ($('#child-hero .child-caption')) throw new Error('caption element still present');
    const hero = $('#child-hero').textContent.trim();
    if (hero.length) throw new Error('visible text inside the hero: ' + hero.slice(0, 60));
  });
  t('the cursor entourage exists and is wired up', () => {
    const host = $('#friends');
    if (!host) throw new Error('#friends overlay missing');
    if (host.getAttribute('aria-hidden') !== 'true') throw new Error('entourage is not aria-hidden');
    const els = $$('#friends .fr');
    if (els.length !== 16) throw new Error('expected 16 friends, found ' + els.length);
    if ($$('#friends .fr svg').length !== 16) throw new Error('a friend has no artwork');
    if ($$('#friends .bwl').length !== 6 || $$('#friends .bwr').length !== 6)
      throw new Error('butterfly wing groups are missing');
    if (!FRIENDS || FRIENDS.folk.length !== 16) throw new Error('initFriends() did not report 16 friends');
    if (typeof FRIENDS.start !== 'function' || typeof FRIENDS.stop !== 'function')
      throw new Error('the entourage loop cannot be started or stopped');
    for (const f of FRIENDS.folk)
      if (typeof f.x !== 'number' || typeof f.y !== 'number' || typeof f.a !== 'number')
        throw new Error('a friend was created without a position');
    /* Motion itself is deliberately not asserted here: it happens on rAF, and this
       suite runs synchronously at parse time. The logic suite covers the specs. */
  });

  /* ---------- 3. basket ---------- */
  t('badge hidden while basket empty', () => { if (!$('#basket-count').hidden) throw new Error('badge visible'); });
  t('category modal adds 3 books', () => {
    openCatModal(CATEGORIES[0]);
    if (!$('#m-cat').classList.contains('open')) throw new Error('modal did not open');
    fire($('#cat-plus'), 'click'); fire($('#cat-plus'), 'click');
    if ($('#cat-q').textContent !== '3') throw new Error('stepper=' + $('#cat-q').textContent);
    fire($('#cat-add'), 'click');
    if (state.basket.length !== 1) throw new Error('basket len=' + state.basket.length);
    if (state.basket[0].qty !== 3) throw new Error('qty=' + state.basket[0].qty);
    if ($('#basket-count').textContent !== '3') throw new Error('badge=' + $('#basket-count').textContent);
    if ($('#basket-count').hidden) throw new Error('badge still hidden');
  });
  t('same cat+condition merges instead of duplicating', () => {
    addToBasket('books', 2, 'Like New');
    if (state.basket.length !== 1) throw new Error('len=' + state.basket.length);
    if (state.basket[0].qty !== 5) throw new Error('qty=' + state.basket[0].qty);
    addToBasket('books', 1, 'Good');
    if (state.basket.length !== 2) throw new Error('new condition did not create a row');
  });
  t('minus never drops below 1', () => {
    route('donate');
    const rows = $$('#basket-list .b-row');
    if (rows.length !== 2) throw new Error('rows=' + rows.length);
    for (let i = 0; i < 5; i++) fire(rows[0].querySelectorAll('.qty button')[0], 'click');
    if (state.basket[0].qty !== 1) throw new Error('qty=' + state.basket[0].qty);
  });
  t('delete removes the right row', () => {
    route('donate');
    const before = state.basket.map(i => i.cond).join(',');
    const rows = $$('#basket-list .b-row');
    fire(rows[0].querySelector('.del'), 'click');
    if (state.basket.length !== 1) throw new Error('len=' + state.basket.length);
    if (state.basket.map(i => i.cond).join(',') === before) throw new Error('wrong row removed: ' + state.basket[0].cond);
  });

  /* ---------- 4. site selection uses ids ---------- */
  t('city change refills sites with id values', () => {
    const sel = $('#f-city');
    sel.value = 'Lahore';
    sel.dispatchEvent(new Event('change', { bubbles: true }));
    const opts = $$('#f-site option');
    if (opts.length < 2) throw new Error('opts=' + opts.length);
    const lah = SITES.filter(s => s.city === 'Lahore');
    if (opts.length !== lah.length + 1) throw new Error('opts=' + opts.length + ' want ' + (lah.length + 1));
    for (const o of opts.slice(1)) if (!SITES.some(s => s.id === o.value)) throw new Error('option value is not a site id: ' + o.value);
  });
  t('pickSite selects the right site and route', () => {
    const target = SITES.filter(s => s.city === 'Lahore')[2];
    pickSite(target);
    if ($('#f-city').value !== target.city) throw new Error('city=' + $('#f-city').value);
    if ($('#f-site').value !== target.id) throw new Error('site=' + $('#f-site').value + ' want ' + target.id);
    if (!$('#view-donate').classList.contains('active')) throw new Error('did not route to donate');
    if (state.ui.city !== target.city) throw new Error('city not remembered');
  });
  t('city choice survives leaving and re-entering Donate', () => {
    route('home'); route('donate');
    const target = SITES.filter(s => s.city === 'Lahore')[2];
    if ($('#f-city').value !== target.city) throw new Error('city reset to ' + $('#f-city').value);
  });
  t('legacy tickets without siteId still resolve', () => {
    const legacy = { id: 'Dold', ts: Date.now(), name: 'Old', phone: '03001234567', city: 'Lahore', site: 'Rizq Food Bank', items: [{ cat: 'food', qty: 1, cond: 'Good' }] };
    if (ticketText(legacy).indexOf('Rizq Food Bank') < 0) throw new Error('legacy name lookup broke');
  });

  /* ---------- 5. form validation + submit ---------- */
  function fill(name, phone, date) {
    $('#f-name').value = name; $('#f-phone').value = phone; $('#f-date').value = date || '';
    $('#f-notes').value = 'Books for the school library';
  }
  const submit = () => $('#donate-form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));

  t('empty basket is refused', () => {
    const keep = state.basket; state.basket = [];
    fill('Ayesha Khan', '0300 1234567');
    submit();
    state.basket = keep;
    if (state.history.length !== 0) throw new Error('created a ticket from an empty basket');
  });
  t('junk phone is rejected', () => {
    addToBasket('toys', 1, 'Good');
    fill('Ayesha Khan', '0000000');
    submit();
    if (state.history.length !== 0) throw new Error('accepted a junk phone number');
    if ($$('#donate-form .field.err').length === 0) throw new Error('no field was marked invalid');
  });
  t('past date is rejected', () => {
    fill('Ayesha Khan', '03001234567', '2020-01-01');
    submit();
    if (state.history.length !== 0) throw new Error('accepted a past date');
  });
  t('valid submit creates the ticket', () => {
    fill('Ayesha Khan', '+92 300 1234567', '');
    submit();
    if (state.history.length !== 1) throw new Error('history=' + state.history.length);
    if (state.basket.length !== 0) throw new Error('basket not cleared');
    if ($('#donate-success').hidden) throw new Error('success card hidden');
    if ($('#basket-count').hidden !== true) throw new Error('badge still visible');
  });
  t('ticket text carries site, items and a warning-free line', () => {
    const txt = $('#sum-pre').textContent;
    if (txt.indexOf('DONATION TICKET') < 0) throw new Error('no header');
    if (txt.indexOf('Toys') < 0) throw new Error('items missing');
    if (txt.indexOf('Ayesha Khan') < 0) throw new Error('donor missing');
    if (txt.indexOf('Site phone') < 0) throw new Error('site details missing');
  });
  t('notes and date are cleared after submit', () => {
    if ($('#f-notes').value !== '') throw new Error('notes kept: ' + $('#f-notes').value);
    if ($('#f-date').value !== '') throw new Error('date kept');
    if ($$('#donate-form .field.err').length !== 0) throw new Error('stale error styling');
  });
  t('name prefilled into profile', () => { if (state.profile.name !== 'Ayesha Khan') throw new Error(state.profile.name); });
  t('saved siteId resolves back to the same site', () => {
    const rec = state.history[0];
    if (!rec.siteId) throw new Error('no siteId stored');
    if (ticketText(rec).indexOf(rec.site) < 0) throw new Error('site name not in ticket');
  });

  /* ---------- 6. persistence shape ---------- */
  t('localStorage holds the repaired shape', () => {
    const raw = JSON.parse(localStorage.getItem('iman-trust-v3'));
    if (!raw || !Array.isArray(raw.basket) || !Array.isArray(raw.history)) throw new Error('bad shape');
    if (raw.history.length !== 1) throw new Error('history=' + raw.history.length);
  });
  t('corrupt state is repaired, not trusted', () => {
    const bad = sanitise({ profile: null, basket: 'nope', history: [{ items: null }, { items: [{ cat: 'ZZZ' }] }], ui: 7 });
    if (!bad.profile || bad.profile.avatar !== 'bear') throw new Error('profile not repaired');
    if (!Array.isArray(bad.basket) || bad.basket.length !== 0) throw new Error('basket not repaired');
    if (bad.history.length !== 0) throw new Error('history not repaired');
    if (!bad.ui || bad.ui.city !== '' || 'gaze' in bad.ui) throw new Error('ui not repaired');
  });
  t('unknown category and condition are filtered', () => {
    const bad = sanitise({ basket: [{ cat: 'books', qty: 999, cond: 'Нет' }, { cat: 'nope', qty: 1, cond: 'Good' }] });
    if (bad.basket.length !== 1) throw new Error('len=' + bad.basket.length);
    if (bad.basket[0].qty !== 99) throw new Error('qty not clamped: ' + bad.basket[0].qty);
    if (bad.basket[0].cond !== 'Good') throw new Error('cond not defaulted');
  });

  /* ---------- 7. search consistency ---------- */
  t('multi-word category search matches', () => {
    $('#search').value = 'kids items';
    $('#search').dispatchEvent(new Event('input', { bubbles: true }));
    const vis = $$('#cat-grid .cat').filter(c => !c.hidden);
    if (vis.length < 1) throw new Error('nothing matched "kids items"');
  });
  t('multi-word site search needs every word', () => {
    const hits = searchSites('edhi lahore');
    if (!hits.length) throw new Error('no hits for "edhi lahore"');
    for (const h of hits) if (!/edhi/i.test(h.name) || !/lahore/i.test(h.city)) throw new Error('loose match: ' + h.name);
    if (searchSites('edhi quetta').some(s => s.city !== 'Quetta')) throw new Error('AND semantics broken');
  });
  t('clearing search restores all cards', () => {
    $('#search').value = '';
    $('#search').dispatchEvent(new Event('input', { bubbles: true }));
    if ($$('#cat-grid .cat').filter(c => !c.hidden).length !== 12) throw new Error('not restored');
  });

  /* ---------- 8. search → Enter opens the Sites page ---------- */
  t('Enter in search opens the Sites page with the query', () => {
    $('#search').value = 'Lahore';
    $('#search').dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    if (!$('#view-sites').classList.contains('active')) throw new Error('did not route to Sites');
    if ($('#sites-q').value !== 'Lahore') throw new Error('query not carried over: ' + $('#sites-q').value);
    if ($$('#sites-list .s-card').length < 1) throw new Error('no .s-card');
  });
  t('province filter narrows the city list', () => {
    $('#sites-prov').value = 'Sindh';
    $('#sites-prov').dispatchEvent(new Event('change', { bubbles: true }));
    const cities = $$('#sites-city option').map(o => o.value);
    if (cities.some(c => c !== 'All cities' && !SITES.some(s => s.city === c && s.pro === 'Sindh'))) throw new Error('foreign city leaked: ' + cities.join('|'));
    if ($$('#sites-list .s-card').length < 1) throw new Error('filter emptied the list');
  });
  t('a city filter with no matches says so instead of going blank', () => {
    $('#sites-q').value = 'zzzqqq';
    $('#sites-q').dispatchEvent(new Event('input', { bubbles: true }));
    if ($$('#sites-list .s-card').length !== 0) throw new Error('matches found for nonsense');
    if ($('#sites-none').hidden) throw new Error('empty-state message stayed hidden');
    if ($('#sites-echo').textContent.indexOf('0 of') < 0) throw new Error('count not updated: ' + $('#sites-echo').textContent);
    $('#sites-q').value = '';
    $('#sites-q').dispatchEvent(new Event('input', { bubbles: true }));
  });

  /* ---------- 9. modal a11y ---------- */
  t('#app is hidden from AT while a modal is open', () => {
    openCatModal(CATEGORIES[0]);
    if (!$('#m-cat').classList.contains('open')) throw new Error('modal did not open');
    if ($('#app').getAttribute('aria-hidden') !== 'true') throw new Error('not hidden');
  });
  t('Escape closes the top modal and restores AT', () => {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    if ($('#m-cat').classList.contains('open')) throw new Error('still open');
    if ($('#app').hasAttribute('aria-hidden')) throw new Error('aria-hidden not removed');
  });
  t('helplines render with a source and the checked date', () => {
    $('#helpline-open').click();
    const cards = $$('#hp-list .hp-card');
    if (cards.length !== HELPLINES.length) throw new Error('cards=' + cards.length);
    if ($('#hp-checked').textContent !== CONFIG.helplinesChecked) throw new Error('date not filled');
    if (!cards[0].querySelector('.src-link')) throw new Error('no source link');
    const body = cards.map(c => c.textContent).join(' ');
    if (body.indexOf('1020') < 0) throw new Error('Chhipa 1020 missing');
    if (body.indexOf('1121') >= 0) throw new Error('wrong Chhipa number still present');
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  });

  /* ---------- 10. routing ---------- */
  t('route sets aria-current on exactly one nav button', () => {
    route('profile');
    const cur = $$('.navbtn[aria-current="true"]');
    if (cur.length !== 1) throw new Error('count=' + cur.length);
    if (cur[0].dataset.view !== 'profile') throw new Error('wrong button');
    if ($('#stat-don').textContent !== '1') throw new Error('stat-don=' + $('#stat-don').textContent);
  });
  t('unknown hash falls back to home', () => {
    route('nonsense');
    if (!$('#view-home').classList.contains('active')) throw new Error('not home');
  });
  t('history card renders and its delete is wired', () => {
    route('profile');
    const cards = $$('#history-list .h-card');
    if (cards.length !== 1) throw new Error('cards=' + cards.length);
    if (!cards[0].querySelector('.tk') || !cards[0].querySelector('.dl')) throw new Error('buttons missing');
  });
  t('switching avatars retires the previous sprite', () => {
    const live = () => sprites.filter(s => !s.dead).length;
    const before = live();
    setAvatar('duck');
    if (live() > before + 1) throw new Error('live sprites grew ' + before + ' -> ' + live());
    if (!sprites.some(s => s.dead)) throw new Error('the previous avatar sprite was not retired');
    setAvatar('bear'); setAvatar('castle');
    if (live() > 1) throw new Error('more than one live avatar sprite: ' + live());
    if (typeof step !== 'function') throw new Error('the pruner step() is missing');
  });
  t('export payload is the whole state', () => {
    const json = JSON.stringify(state);
    if (json.indexOf('Ayesha Khan') < 0) throw new Error('export missing donor');
  });

  /* ---------- 11. the added pages ---------- */
  t('all five tabs exist and each maps to a view', () => {
    const tabs = $$('.navbtn').map(b => b.dataset.view);
    if (tabs.length !== 5) throw new Error('tabs=' + tabs.join(','));
    for (const v of tabs) if (!$('#view-' + v)) throw new Error('no view for ' + v);
  });
  t('secondary pages keep their parent tab lit', () => {
    route('guide');
    const cur = $$('.navbtn[aria-current="true"]');
    if (cur.length !== 1) throw new Error('lit tabs=' + cur.length);
    if (cur[0].dataset.view !== 'home') throw new Error('guide lit ' + cur[0].dataset.view);
    if (!$('#view-guide').classList.contains('active')) throw new Error('guide not shown');
  });
  t('every in-app link routes somewhere real', () => {
    for (const b of $$('[data-goto]')) if (!$('#view-' + b.dataset.goto)) throw new Error('bad target ' + b.dataset.goto);
    $('[data-goto="zakat"]').click();
    if (!$('#view-zakat').classList.contains('active')) throw new Error('zakat did not open');
  });
  t('zakat calculator recomputes live', () => {
    $('#zk-cash').value = '100000';
    $('#zk-cash').dispatchEvent(new Event('input', { bubbles: true }));
    $('#zk-nisaab').value = '50000';
    $('#zk-nisaab').dispatchEvent(new Event('input', { bubbles: true }));
    if ($('#zk-due').textContent.replace(/[^0-9]/g, '') !== '2500') throw new Error('due=' + $('#zk-due').textContent);
    if ($('#zk-verdict').className.indexOf('due') < 0) throw new Error('verdict=' + $('#zk-verdict').className);
  });
  t('zakat goes quiet below the nisaab', () => {
    $('#zk-cash').value = '10000';
    $('#zk-cash').dispatchEvent(new Event('input', { bubbles: true }));
    if ($('#zk-due').textContent.replace(/[^0-9]/g, '') !== '0') throw new Error('due=' + $('#zk-due').textContent);
    if ($('#zk-verdict').className.indexOf('below') < 0) throw new Error('verdict=' + $('#zk-verdict').className);
  });
  t('zakat nisaab helper multiplies grams by the rate', () => {
    $('#zk-metal').value = '612.36';
    $('#zk-rate').value = '100';
    $('#zk-usenisaab').click();
    if ($('#zk-nisaab').value !== '61236') throw new Error('nisaab=' + $('#zk-nisaab').value);
  });
  t('zakat figures are never persisted', () => {
    $('#zk-cash').value = '777777';
    $('#zk-cash').dispatchEvent(new Event('input', { bubbles: true }));
    persist();
    if (localStorage.getItem(CONFIG.storageKey).indexOf('777777') >= 0) throw new Error('zakat figures were stored');
  });
  t('zakat clear empties the form', () => {
    $('#zk-clear').click();
    if ($('#zk-cash').value !== '' || $('#zk-nisaab').value !== '') throw new Error('not cleared');
  });
  t('all four mascots are baked animations, with no emoji fallback', () => {
    if (AVATARS.length !== 4) throw new Error('avatars=' + AVATARS.length);
    for (const a of AVATARS) if (!a.sheet || !sheets[a.sheet]) throw new Error('no sheet for ' + a.id);
    setAvatar('duck');
    if ($('#av-stage').hidden) throw new Error('chick stage hidden — it fell back to the emoji');
    if (!$('#av-emoji').hidden) throw new Error('emoji fallback is still showing');
    if ($('#av-stage').style.backgroundImage.indexOf('data:image/png') < 0) throw new Error('chick sheet was not baked');
  });
  t('the emergency page lists the same verified helplines', () => {
    route('emergency');
    const cards = $$('#em-orgs .hp-card');
    if (cards.length !== HELPLINES.length) throw new Error('cards=' + cards.length);
    if (cards.map(c => c.textContent).join(' ').indexOf('1020') < 0) throw new Error('Chhipa number missing');
  });
  t('the guide and about pages have real content', () => {
    if ($$('#view-guide .gd-item').length < 10) throw new Error('guide is thin: ' + $$('#view-guide .gd-item').length);
    if ($$('#view-about .gd-item').length < 5) throw new Error('about is thin');
    if ($$('#view-emergency .gd-item').length < 8) throw new Error('emergency page is thin');
  });
  t('the directory disclaimer survives on the Sites page', () => {
    route('sites');
    const txt = $('#view-sites').textContent;
    if (txt.indexOf('not') < 0 || txt.indexOf('verified') < 0) throw new Error('disclaimer missing');
  });
  t('a site picked from the directory preselects the ticket', () => {
    const target = SITES.filter(s => s.city === 'Lahore')[0];
    pickSite(target);
    if (!$('#view-donate').classList.contains('active')) throw new Error('did not route to Donate');
    if ($('#f-site').value !== target.id) throw new Error('site=' + $('#f-site').value);
    if (state.ui.siteId !== target.id) throw new Error('choice not remembered');
  });

  /* ---------- report ---------- */
  const fails = out.filter(l => l.indexOf('FAIL') === 0);
  const pre = document.createElement('pre');
  pre.id = 'RESULTS';
  pre.textContent = '\n@@@BEGIN@@@\n' + out.join('\n') +
    '\n-----\n' + (out.length - fails.length) + '/' + out.length + ' passed\n@@@END@@@\n';
  document.body.appendChild(pre);
  document.title = fails.length ? 'SELFTEST FAIL ' + fails.length : 'SELFTEST PASS';
})();
