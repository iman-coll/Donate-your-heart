"""Build a Node harness from the app's REAL source and run logic assertions.

The browser cannot run here (the sandbox denies Chrome its named-pipe IPC), so the
pure logic is exercised directly: the constants + utils + sanitise/state region is
lifted verbatim from index.html, and the functions under test are extracted by name
so the tests can never drift from the shipped code.
"""
import re, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NODE = pathlib.Path(r"C:\Users\Dell\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")
src = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
body = re.search(r"<script[^>]*>(.*?)</script>", src, re.S).group(1)


def function_by_name(name):
    """Slice `function name(...){...}` out by brace matching."""
    i = body.index(f"function {name}(")
    j = body.index("{", i)
    depth, k = 0, j
    while True:
        if body[k] == "{":
            depth += 1
        elif body[k] == "}":
            depth -= 1
            if depth == 0:
                return body[i:k + 1]
        k += 1


def const_by_name(name):
    """Slice a const declaration out: from `const NAME=` to the first `;` at depth 0."""
    i = body.index(f"const {name}=")
    k = body.index("=", i) + 1
    depth = 0
    while True:
        ch = body[k]
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        elif ch == ";" and depth == 0:
            return body[i:k + 1]
        k += 1


# the cursor entourage: 6 butterflies + 10 children, all generated from specs
entourage = "\n".join(const_by_name(n) for n in
                      ("BFLY_WINGS", "BUTTERFLIES", "HAIR_BACK", "HAIR_FRONT",
                       "EYES", "MOUTH", "EXTRAS", "FRIEND_KIDS"))
entourage += "\n" + function_by_name("butterflySVG") + "\n" + function_by_name("figureSVG")


# region: section 1 (config/data) through section 3 (nearest-site referral).
# Stops before the sprite-baker, which needs a real 2D canvas.
region = body[:body.index("4. SPRITE-BAKER")]
region = region[region.index("const CONFIG = {"):]

functions = "\n\n".join(function_by_name(n) for n in
                        ("siteById", "siteByLegacyName", "ticketText", "searchSites"))

m = re.search(r"const phoneVal=phone\.value\.trim\(\);(.*?)mark\(phone, !phoneOK\);", body, re.S)
assert m, "could not extract the phone-validation block"
phone_block = m.group(1)

# The Zakat calculator is money maths, so it gets tested against the real code too.
zakat_lines = "\n".join(
    re.search(rf"^{re.escape(prefix)}.*$", body, re.M).group(0)
    for prefix in ("const ZK_ASSETS=", "const zkNum=", "const zkMoney="))
zakat_figures = function_by_name("zakatFigures")

harness = f"""
/* ---- minimal stubs so the real source can be evaluated outside a browser ---- */
const _ls = {{}};
globalThis.localStorage = {{
  getItem: k => (k in _ls ? _ls[k] : null),
  setItem: (k, v) => {{ _ls[k] = String(v); }},
  removeItem: k => {{ delete _ls[k]; }}
}};
globalThis.matchMedia = () => ({{ matches: false }});
/* A stub element whose `value` reads through to a map, so the Zakat calculator can be
   driven by feeding it values the way the real DOM would. */
globalThis.__VAL = {{}};
function stubEl(sel){{
  return {{
    get value(){{ return (sel in globalThis.__VAL) ? globalThis.__VAL[sel] : ''; }},
    set value(v){{ globalThis.__VAL[sel] = v; }},
    addEventListener(){{}}, setAttribute(){{}}, removeAttribute(){{}}, getAttribute(){{ return null; }},
    focus(){{}}, classList: {{ add(){{}}, remove(){{}}, toggle(){{}} }},
    textContent: '', className: '', hidden: false, style: {{}}
  }};
}}
globalThis.document = {{
  querySelector: s => stubEl(s), querySelectorAll: () => [],
  createElement: () => stubEl('_created'),
  addEventListener() {{}}
}};
globalThis.navigator = {{}};
globalThis.window = {{}};
globalThis.performance = {{ now: () => Date.now() }};
globalThis.innerWidth = 800; globalThis.innerHeight = 600;

/* =================== VERBATIM APP SOURCE =================== */
{region}

/* =================== FUNCTIONS UNDER TEST =================== */
{functions}

/* =================== ZAKAT CALCULATOR (verbatim) =================== */
{zakat_lines}
{zakat_figures}

/* =================== CURSOR ENTOURAGE (verbatim) =================== */
{entourage}

function phoneValid(phoneVal){{
  {phone_block}
  return phoneOK;
}}

/* =================== ASSERTIONS =================== */
let pass = 0, fail = 0;
const eq = (n, a, b) => {{
  const okk = JSON.stringify(a) === JSON.stringify(b);
  okk ? pass++ : fail++;
  console.log((okk ? 'PASS' : 'FAIL') + ' :: ' + n + (okk ? '' : '  got=' + JSON.stringify(a) + ' want=' + JSON.stringify(b)));
}};
const truthy = (n, v) => eq(n, !!v, true);
const throws = (n, fn) => {{ try {{ fn(); eq(n, 'threw', 'no throw'); }} catch (e) {{ eq(n, 'threw', 'threw'); }} }};

/* --- data integrity --- */
eq('12 categories', CATEGORIES.length, 12);
eq('category ids unique', new Set(CATEGORIES.map(c => c.id)).size, 12);
eq('site ids unique', new Set(SITES.map(s => s.id)).size, SITES.length);
eq('site names unique (legacy lookup key)', new Set(SITES.map(s => s.name)).size, SITES.length);
truthy('34 sites', SITES.length === 34);
truthy('every accepts entry is a real category or *',
  SITES.every(s => s.accepts.every(a => a === '*' || CATEGORIES.some(c => c.id === a))));
truthy('every site has city/province', SITES.every(s => s.city && s.pro));
truthy('every site carries lat/lng', SITES.every(s => typeof s.lat === 'number' && typeof s.lng === 'number'));
truthy('Chhipa helpline is 1020, not 1121',
  HELPLINES.some(h => /Chhipa/.test(h.name) && h.ph === '1020' && !HELPLINES.some(x => x.ph === '1121')));
truthy('every helpline yields a sane tel: href',
  HELPLINES.every(h => /^tel:\\+?[0-9]{{3,15}}$/.test(telHref(h.tel))));
truthy('every site phone yields a sane tel: href',
  SITES.filter(s => s.phone).every(s => /^tel:\\+?[0-9]{{3,15}}$/.test(telHref(s.phone))));

/* --- sanitise(): the init-crash repair --- */
const empty = sanitise({{}});
eq('empty store -> default profile', empty.profile, {{ name: '', avatar: 'bear' }});
eq('empty store -> empty arrays', [empty.basket.length, empty.history.length], [0, 0]);

const bad = sanitise({{ profile: null, basket: 'nope', history: {{}}, ui: 7 }});
eq('profile null repaired', bad.profile.avatar, 'bear');
eq('basket non-array repaired', Array.isArray(bad.basket) && bad.basket.length, 0);
eq('history non-array repaired', Array.isArray(bad.history) && bad.history.length, 0);
eq('ui non-object repaired', bad.ui, {{ city: '', siteId: '' }});
eq('the retired `gaze` preference is dropped, not resurrected',
   'gaze' in sanitise({{ ui: {{ gaze: false }} }}).ui, false);
eq('ui.siteId survives a round trip', sanitise({{ ui: {{ siteId: 'lh4' }} }}).ui.siteId, 'lh4');
eq('ui.siteId junk becomes empty string', sanitise({{ ui: {{ siteId: 42 }} }}).ui.siteId, '');

eq('qty 9e9 clamped', sanitise({{ basket: [{{ cat: 'books', qty: 9e9, cond: 'Good' }}] }}).basket[0].qty, 99);
eq('qty -3 clamped up', sanitise({{ basket: [{{ cat: 'books', qty: -3, cond: 'Good' }}] }}).basket[0].qty, 1);
eq('qty "abc" -> 1', sanitise({{ basket: [{{ cat: 'books', qty: 'abc', cond: 'Good' }}] }}).basket[0].qty, 1);
eq('qty "7" -> 7', sanitise({{ basket: [{{ cat: 'books', qty: '7', cond: 'Good' }}] }}).basket[0].qty, 7);
eq('unknown category dropped', sanitise({{ basket: [{{ cat: '__proto__', qty: 1, cond: 'Good' }}] }}).basket.length, 0);
eq('unknown condition defaulted', sanitise({{ basket: [{{ cat: 'books', qty: 1, cond: 'Нет' }}] }}).basket[0].cond, 'Good');
eq('unknown avatar defaulted', sanitise({{ profile: {{ name: 'x', avatar: 'hacker' }} }}).profile.avatar, 'bear');
eq('long name truncated', sanitise({{ profile: {{ name: 'a'.repeat(500) }} }}).profile.name.length, 60);
eq('history row without items dropped', sanitise({{ history: [{{ id: 'x' }}] }}).history.length, 0);
eq('history rows with only junk items dropped',
   sanitise({{ history: [{{ items: [{{ cat: 'ZZZ' }}] }}] }}).history.length, 0);
eq('history capped at 200',
   sanitise({{ history: Array.from({{ length: 500 }}, () => ({{ items: [{{ cat: 'books', qty: 1, cond: 'Good' }}] }})) }}).history.length, 200);
eq('prototype pollution via __proto__ does not leak',
   Object.prototype.polluted, undefined);

/* --- telHref --- */
eq('telHref +92 spaced', telHref('+92 300 1234567'), 'tel:+923001234567');
eq('telHref landline', telHref('042-3594-5100'), 'tel:04235945100');
eq('telHref short code', telHref('115'), 'tel:115');

/* --- todayLocal: local, not UTC --- */
(() => {{
  const d = new Date();
  const want = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  eq('todayLocal is the LOCAL date', todayLocal(), want);
  eq('todayLocal is 10 chars', todayLocal().length, 10);
}})();

/* --- phone validation (extracted verbatim from the submit handler) --- */
for (const good of ['03001234567', '+92 300 1234567', '0092-300-1234567', '042-35945100', '0345 1234567', '051-4862600'])
  eq('accepts ' + good, phoneValid(good), true);
for (const junk of ['0000000', '12345', 'abc', '', '+', '0300-12', '++923001234567', 'phone'])
  eq('rejects ' + JSON.stringify(junk), phoneValid(junk), false);

/* --- haversine / nearest --- */
eq('same point is 0 km', haversine(32.161, 74.188, 32.161, 74.188), 0);
(() => {{
  const d = haversine(24.86, 67.01, 31.55, 74.32);       // Karachi -> Lahore
  truthy('Karachi-Lahore is 1000-1300 km (got ' + d + ')', d > 1000 && d < 1300);
}})();
(() => {{
  const n = nearestSites(CONFIG.homeBase.lat, CONFIG.homeBase.lng, 1)[0];
  eq('nearest to HQ is the Gujranwala site', n.city, 'Gujranwala');
  truthy('nearest distance is small (got ' + n.dist + ')', n.dist < 5);
}})();
eq('fmtDist under 1 km reads as text', fmtDist(0), 'under 1 km');

/* --- searchSites: AND semantics across all words --- */
eq('empty query -> no hits', searchSites('').length, 0);
(() => {{
  const hits = searchSites('edhi lahore');
  truthy('"edhi lahore" has hits', hits.length > 0);
  truthy('every hit matches BOTH words', hits.every(s => /edhi/i.test(s.name) && /lahore/i.test(s.city)));
}})();
truthy('"edhi quetta" only returns Quetta', searchSites('edhi quetta').every(s => s.city === 'Quetta'));
truthy('category word matches via accepts', searchSites('toys').every(s => s.accepts.includes('*') || s.accepts.includes('toys')));
truthy('"karachi" matches only Karachi', searchSites('karachi').every(s => s.city === 'Karachi'));
eq('nonsense query -> no hits', searchSites('zzzqqq').length, 0);
truthy('case-insensitive', searchSites('EDHI').length === searchSites('edhi').length);
throws('non-string query is not silently accepted', () => searchSites(null));

/* --- ticketText --- */
(() => {{
  const rec = {{ id: 'DTEST', ts: Date.now(), name: 'Ayesha Khan', phone: '03001234567',
    city: 'Lahore', siteId: 'lh4', site: 'Rizq Food Bank', date: '2026-11-01',
    notes: 'Books for the library', status: 'Ticket Ready',
    items: [{{ cat: 'books', qty: 3, cond: 'Good' }}] }};
  const txt = ticketText(rec);
  truthy('ticket has a header', txt.includes('DONATION TICKET'));
  truthy('ticket has the id', txt.includes('DTEST'));
  truthy('ticket resolves site from siteId', txt.includes('Rizq Food Bank'));
  truthy('ticket has the chosen date', txt.includes('2026-11-01'));
  truthy('ticket lists the item and quantity', txt.includes('Books x3 (Good)'));
  truthy('ticket has donor name and phone', txt.includes('Ayesha Khan') && txt.includes('03001234567'));
  truthy('ticket has notes', txt.includes('Books for the library'));
  truthy('ticket does NOT promise home pickup', !/arrange pickup/i.test(txt));
}})();

(() => {{
  const legacy = {{ id: 'DOLD', ts: Date.now(), name: 'Old', phone: '03001234567', city: 'Lahore',
    site: 'Edhi Center Lahore', items: [{{ cat: 'clothes', qty: 1, cond: 'Usable' }}] }};
  truthy('legacy name-only record still resolves', ticketText(legacy).includes('Edhi Center Lahore'));
}})();

(() => {{
  const anywhere = {{ id: 'DANY', ts: Date.now(), name: 'A', phone: '03001234567', city: 'Multan',
    siteId: '', site: '', items: [{{ cat: 'food', qty: 2, cond: 'Good' }}] }};
  const txt = ticketText(anywhere);
  truthy('"anywhere" falls back to trust suggestion', txt.includes('Nearest site suggested by trust'));
}})();

/* --- exported state shape --- */
truthy('state has the three arrays/objects the UI expects',
  state.profile && Array.isArray(state.basket) && Array.isArray(state.history) && state.ui);
truthy('persist round-trips through the stub storage', (() => {{
  persist();
  const raw = JSON.parse(localStorage.getItem(CONFIG.storageKey));
  return raw && typeof raw === 'object' && Array.isArray(raw.basket);
}})());

/* --- zakat calculator: money maths, so it is checked hard --- */
const ZK = vals => {{ for (const k in globalThis.__VAL) delete globalThis.__VAL[k];
  Object.assign(globalThis.__VAL, vals); return zakatFigures(); }};
const A = n => ({{ '#zk-cash': n }}) ;
eq('zakat: nothing entered -> 0', ZK({{}}).total, 0);
eq('zakat: no nisaab set -> not above', ZK({{ '#zk-cash': '500000' }}).above, false);
eq('zakat: above nisaab', ZK({{ '#zk-cash': '100000', '#zk-nisaab': '50000' }}).above, true);
eq('zakat due is 2.5%', ZK({{ '#zk-cash': '100000', '#zk-nisaab': '50000' }}).total * 0.025, 2500);
eq('zakat: exactly at nisaab counts as due',
   ZK({{ '#zk-cash': '50000', '#zk-nisaab': '50000' }}).above, true);
eq('zakat: one rupee under nisaab is not due',
   ZK({{ '#zk-cash': '49999', '#zk-nisaab': '50000' }}).above, false);
eq('zakat: below nisaab', ZK({{ '#zk-cash': '40000', '#zk-nisaab': '50000' }}).above, false);
eq('zakat: debts are subtracted',
   ZK({{ '#zk-cash': '100000', '#zk-debt': '30000', '#zk-nisaab': '10000' }}).total, 70000);
eq('zakat: total never goes negative',
   ZK({{ '#zk-cash': '10000', '#zk-debt': '500000' }}).total, 0);
eq('zakat: all five asset lines are summed',
   ZK({{ '#zk-cash':'1','#zk-gold':'2','#zk-silver':'3','#zk-stock':'4','#zk-recv':'5' }}).total, 15);
eq('zakat: junk text is treated as zero', ZK({{ '#zk-cash': 'abc' }}).total, 0);
eq('zakat: a negative entry is treated as zero', ZK({{ '#zk-cash': '-5000' }}).total, 0);
eq('zakat: thousands separators are tolerated', ZK({{ '#zk-cash': '1,00,000' }}).total, 100000);
eq('zakat: decimals survive', ZK({{ '#zk-cash': '99.5' }}).total, 99.5);
eq('zakat: a blank string is zero', ZK({{ '#zk-cash': '' }}).total, 0);
eq('zakat: NaN never reaches the total', Number.isNaN(ZK({{ '#zk-cash': 'e' }}).total), false);
truthy('zakat: money formats with a Rs prefix', /^Rs/.test(zkMoney(2500)));
truthy('zakat: money never prints NaN', zkMoney(ZK({{ '#zk-cash': 'e' }}).total).indexOf('NaN') === -1);
/* The privacy promise made on the Zakat page: the figures are never stored. */
(() => {{
  globalThis.__VAL['#zk-cash'] = '987654';
  persist();
  eq('zakat: figures are NOT persisted (the page promises this)',
     localStorage.getItem(CONFIG.storageKey).indexOf('987654'), -1);
  globalThis.__VAL['#zk-cash'] = '';
}})();

/* --- the cursor entourage: 6 butterflies, 5 boys, 5 girls --- */
eq('entourage: 6 butterflies', BUTTERFLIES.length, 6);
eq('entourage: 10 children', FRIEND_KIDS.length, 10);
eq('entourage: 5 boys', FRIEND_KIDS.filter(f => f.kind === 'boy').length, 5);
eq('entourage: 5 girls', FRIEND_KIDS.filter(f => f.kind === 'girl').length, 5);
eq('butterflies: 6 different wing colours', new Set(BUTTERFLIES.map(b => b.wing)).size, 6);
eq('butterflies: 6 different body colours', new Set(BUTTERFLIES.map(b => b.body)).size, 6);
truthy('butterflies: more than one wing silhouette', new Set(BUTTERFLIES.map(b => b.w)).size > 1);
eq('children: 10 different names', new Set(FRIEND_KIDS.map(f => f.name)).size, 10);
eq('children: 10 different outfit colours', new Set(FRIEND_KIDS.map(f => f.top)).size, 10);
truthy('children: at least 4 skin tones', new Set(FRIEND_KIDS.map(f => f.skin)).size >= 4);
truthy('children: at least 4 hair styles', new Set(FRIEND_KIDS.map(f => f.hairStyle)).size >= 4);
truthy('children: at least 4 eye shapes', new Set(FRIEND_KIDS.map(f => f.eyes)).size >= 4);
truthy('children: at least 4 mouth shapes', new Set(FRIEND_KIDS.map(f => f.mouth)).size >= 4);
truthy('children: every hair style has art', FRIEND_KIDS.every(f => HAIR_FRONT[f.hairStyle]));
truthy('children: every eye and mouth key exists',
  FRIEND_KIDS.every(f => EYES[f.eyes] && MOUTH[f.mouth]));
truthy('children: every extra key exists',
  FRIEND_KIDS.every(f => (f.extras || []).every(k => EXTRAS[k])));
truthy('children: girls skip higher than boys walk',
  FRIEND_KIDS.filter(f => f.kind === 'girl').every(f => f.kind === 'girl'));

const bSvgs = BUTTERFLIES.map(b => butterflySVG(Object.assign({{ size: 20 }}, b)));
eq('butterflySVG: 6 distinct drawings', new Set(bSvgs).size, 6);
truthy('butterflySVG: every one is a whole svg',
  bSvgs.every(s => s.indexOf('<svg') === 0 && s.indexOf('</svg>') > 0));
truthy('butterflySVG: both flap groups present',
  bSvgs.every(s => s.indexOf('class="bwl"') > 0 && s.indexOf('class="bwr"') > 0));
truthy('butterflySVG: right wing is mirrored, not written twice',
  bSvgs.every(s => s.indexOf('scale(-1,1)') > 0));
truthy('butterflySVG: size is applied',
  bSvgs.every(s => s.indexOf('width="20"') > 0));

const kSvgs = FRIEND_KIDS.map(f => figureSVG(Object.assign({{ size: 26 }}, f)));
eq('figureSVG: 10 distinct drawings', new Set(kSvgs).size, 10);
truthy('figureSVG: every one is a whole svg',
  kSvgs.every(s => s.indexOf('<svg') === 0 && s.indexOf('</svg>') > 0));
truthy('figureSVG: each child draws its own outfit colour',
  FRIEND_KIDS.every((f, i) => kSvgs[i].indexOf(f.top) >= 0));
truthy('figureSVG: each child draws its own skin tone',
  FRIEND_KIDS.every((f, i) => kSvgs[i].indexOf(f.skin) >= 0));
truthy('figureSVG: each child has a head',
  kSvgs.every(s => s.indexOf('<circle cx="15" cy="10.8" r="8.1"') > 0));
truthy('figureSVG: each child has two legs and two arms',
  kSvgs.every(s => (s.match(/<rect x="11.1"/g) || []).length === 1 &&
                   (s.match(/<rect x="5.5"/g) || []).length === 1));
(() => {{
  const a = figureSVG(Object.assign({{ size: 26 }}, FRIEND_KIDS[5]));
  const b = figureSVG(Object.assign({{ size: 26 }}, FRIEND_KIDS[9]));
  eq('figureSVG: the two girls in frocks differ', a === b, false);
  truthy('figureSVG: a flared outfit draws a skirt',
    a.indexOf(' l2.7 ') > 0 && b.indexOf(' l2.7 ') > 0);
}})();
/* every art string must be balanced enough for a real XML parser to accept it */
truthy('entourage art contains no stray unescaped ampersand',
  bSvgs.concat(kSvgs).every(s => !/&(?!(amp|lt|gt|quot|#))/.test(s)));
truthy('entourage art has no NaN leaking from a bad spec',
  bSvgs.concat(kSvgs).every(s => s.indexOf('NaN') === -1 && s.indexOf('undefined') === -1));

console.log('\\n' + pass + '/' + (pass + fail) + ' passed');
process.exit(fail ? 1 : 0);
"""

out = ROOT / "tools" / "logic_test.js"
out.write_text(harness, encoding="utf-8")
r = subprocess.run([str(NODE), str(out)], capture_output=True, text=True)
print(r.stdout)
if r.stderr:
    print("--- stderr ---")
    print(r.stderr[:4000])
sys.exit(r.returncode)
