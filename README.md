# 💗 Donate your heart — Iman Donation Trust

A donation-directory app for Pakistan: find a drop-off point for clothes, books, toys
and food across 34 partner sites in 17 cities, build a basket, and walk away with a
printable donation ticket. Plus a Zakat calculator, a donation guide, an emergency
appeals page with scam warnings, and an about/trust page.

Everything is one HTML file. There is no build step, no framework, no dependency, no
backend, no account and no tracking.

| | |
|---|---|
| **Live (GitHub Pages)** | https://iman-coll.github.io/Donate-your-heart/ |
| **Live (Streamlit)** | deploy once — see [Run it on Streamlit](#3-run-it-on-streamlit) |
| **The app** | [`docs/index.html`](docs/index.html) — one file, ~161 KB, everything inlined |
| **Licence** | MIT, with additional notices in [`LICENSE`](LICENSE) |

---

## One app, two hosts — and why the layout is like this

```
Donate-your-heart/
├── docs/                 ← GitHub Pages publishes THIS folder, and only this folder
│   ├── index.html        ← THE app. The single source of truth.
│   ├── manifest.json     ← installable-app manifest
│   ├── icon-*.png        ← app icons, generated from code
│   ├── og-cover.png      ← the card WhatsApp/Facebook show when the link is shared
│   ├── 404.html          ← sends lost visitors back to the app
│   └── .nojekyll         ← stop GitHub running Jekyll over the output
├── streamlit_app.py      ← reads docs/index.html and serves that exact file
├── requirements.txt
├── .streamlit/config.toml
└── index.html            ← safety-net redirect, only used if Pages is misconfigured
```

`streamlit_app.py` does not reimplement anything. It reads `docs/index.html` and hands
it to Streamlit inside an iframe, so **the Pages build and the Streamlit build can
never drift apart** — same HTML, same CSS, same JavaScript, same strict CSP. Edit one
file and both hosts change.

Keeping the app in `docs/` rather than at the repo root matters: GitHub Pages
publishes only that folder, so `streamlit_app.py`, `.streamlit/` and this README are
never exposed as public files. (A Streamlit app at the repo root of a Pages site gets
served as plain text, and `secrets.toml` becomes downloadable if `.nojekyll` is added.)

### What "works in all conditions" means here

| Condition | What happens |
|---|---|
| Opened from a server (Pages, Streamlit, any host) | Full app, `localStorage` persists your history |
| Opened as a local `file://` | Works — navigation failures and storage errors are caught, so nothing goes blank |
| Inside Streamlit's iframe | Works; the file-save button tells you to use **Copy** instead of pretending it saved |
| First visit, no JavaScript | A `<noscript>` card with the three national helplines as tappable links |
| `prefers-reduced-motion` | All animation, cursor-following and smooth scrolling are dropped |
| Storage full, disabled, or corrupt | Repaired field by field, with a corrupt blob backed up, and a one-time warning |
| No network after load | Everything is inline; the app makes **zero** requests (`connect-src 'none'`) |
| Narrow phone (360 px) | Five-tab bar, real layout sizes for the mascots, no clipped header |
| Old phone / low bandwidth | No images to download except 3 small icons; all art is inline SVG or canvas |

---

## 1. Get the code

```bash
git clone https://github.com/iman-coll/Donate-your-heart.git
cd Donate-your-heart
```

## 2. Run it as a plain web page

Any static server works. From the repo root:

```bash
python -m http.server 8000 --directory docs
# then open http://127.0.0.1:8000/
```

Opening `docs/index.html` directly in a browser also works — the app is built to
survive `file://` — but a real server is closer to how it will behave live.

> **Why the app is served from `docs/` and not the repo root:** see the section above.
> If you set GitHub Pages to `/ (root)` by mistake, the root `index.html` redirects
> visitors to `./docs/`, so the site still works.

## 3. Run it on Streamlit

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then **Streamlit Community Cloud**: share.streamlit.io → *New app* → pick this repo →
main file `streamlit_app.py` → Deploy. `requirements.txt` is picked up automatically.

Two notes about Streamlit, because they are the two things that can look broken:

* **The app renders inside an iframe.** Its own Content-Security-Policy still applies,
  and every asset it needs is a `data:` URI or inline, so nothing is blocked. The one
  thing an iframe *can* block is saving files, which is why the ticket button says
  "use 📋 Copy" when it cannot be sure the save worked.
* **`localStorage` may be shared with the Streamlit origin** rather than isolated to
  the app. The app already assumes its stored data might be corrupt or foreign and
  repairs it on load, so this is safe — but if you want true isolation, use the Pages
  URL instead.

## 4. Deploy to GitHub Pages

Already done for this repo: **Settings → Pages → Source: `Deploy from a branch` →
Branch: `main` → Folder: `/docs`**.

If you fork this repo, that single setting is the whole deployment. There is
deliberately **no GitHub Actions workflow**, so there is no CI to fail and no second
source of truth fighting the branch setting.

---

## What's in the app

| Tab | What it does |
|---|---|
| **Home** | Illustrated companion that follows your cursor, 12 donation categories, live search over sites and categories, and quick links |
| **Sites** | 34 partner sites, searchable and filterable by province and city, with call and directions buttons |
| **Donate** | Basket, request form with real validation, and a printable donation ticket (copy or save) |
| **Zakat** | Calculator: five asset lines minus debts, compared against the nisaab you enter, at 2.5%. Nothing is stored or sent |
| **Profile** | Kindness badges, donation history, export and clear |
| **Guide** *(from Home)* | What to give, what charities usually cannot take, and how to hand it over |
| **Emergency** *(from Home)* | A dated relief snapshot and how to spot a fake appeal |
| **About** *(from Home)* | How the directory is built, its limits, and how to verify an organisation |

Mascots (bear, bunny, castle, chick) and the cursor entourage (6 butterflies, 5 boys,
5 girls) are generated from code — there are no image files for any of them.

---

## Editing it

Almost everything you want to change lives in **one place**: the `CONFIG`, `HELPLINES`,
`SITES` and `CATEGORIES` constants near the top of the `<script>` in
`docs/index.html`.

```js
const CONFIG = {
  org: 'Iman Donation Trust',
  storageKey: 'iman-trust-v3',
  homeBase: { lat: 32.161, lng: 74.188, label: 'Iman Trust HQ, Gujranwala' },
  helplinesChecked: '2026-10-07',   // shown on the helplines card
  child: { mode: 'vector', videoSrc: '', poster: '' },
  zakat: { nisaab: 0, goldGrams: 87.48, silverGrams: 612.36, nisaabCheckedOn: '' }
};
```

* **Add a site** — add one object to `SITES` with a unique `id`, `city`, `pro` (province),
  `address`, `hours`, `phone`, `lat`, `lng` and `accepts` (an array of category ids, or
  `['*']`). The site appears in the directory on both hosts immediately.
* **Fix a helpline** — edit `HELPLINES` and bump `helplinesChecked`. Each entry's `src`
  URL is rendered as a "source ↗" link, and the checked date is shown to the donor.
* **Use your own mascot art** — set `CONFIG.art.bear` (etc.) to a data URI or
  same-origin image path; the canvas-baked sprite is skipped.
* **Use your own companion clip** — drop an `.mp4` in `docs/`, then set
  `child.mode: 'video'` and `child.videoSrc`. Same-origin media is already permitted by
  the CSP (`media-src 'self'`).
* **Prefill the Zakat nisaab** — set `zakat.nisaab` (rupees) and `zakat.nisaabCheckedOn`.
  Left at `0`, the donor is asked for it, which is the honest default because it moves
  with metal prices.

---

## Checking your changes

The repo ships the test harness used to build it. All of it runs offline.

```bash
# 128 assertions against the app's real extracted source (node required)
python tools/run_logic_tests.py

# markup, ids, routes, CSP, SVG geometry, mascot wiring
python tools/check.py

# render the mascots and the cursor entourage to PNG so you can look at them
python tools/preview_sprites.py
python tools/preview_friends.py
python tools/preview_companion.py

# regenerate the icons and the social card from code
python tools/make_assets.py

# 61 assertions that need a real browser
python tools/make_selftest.py
python -m http.server 8123 --directory tools/site
# open http://127.0.0.1:8123/ and read the <pre id="RESULTS"> block at the bottom
```

---

## More reading

* [`REVIEW-AND-ROADMAP.md`](REVIEW-AND-ROADMAP.md) — the full review: ~20 defects that were
  found and fixed, what was verified and how, what is still open, and a six-tier roadmap for
  turning this into a production-grade Pakistan donation platform. Includes the rendered
  mascot sheets and the cursor entourage.
* [`research/pakistan-donation-briefing.md`](research/pakistan-donation-briefing.md) — the
  evidence base for the directory: what each major trust actually accepts, how zakat and
  qurbani are organised, the payments and registration rules that apply in Pakistan, and what
  a prototype may and may not do. Every claim is labelled `[fetched]`, `[snippet]`,
  **UNVERIFIED** or **CONFLICT**.

---

## Honest limits

* **The directory is not verified.** Addresses, hours and accepted categories were
  compiled from public sources. Always ring a site before travelling. Each helpline
  carries a source link and a checked date; branch details do not.
* **No organisation was confirmed to collect used goods from a donor's home.** Drop-off
  is the assumption throughout; the app says "call ahead to confirm what they can
  accept" rather than promising a pickup.
* **This app does not collect money** and holds no funds. Donation account collection
  by personal accounts is not permitted by the State Bank of Pakistan, and this app
  never asks for one.
* **Not affiliated** with any organisation it lists, and not endorsed by one.
* **The Zakat calculator is arithmetic, not a fatwa.** It does not know about the hawl,
  the eight categories of recipients, or differences between schools of thought.
* **The UI has not been run in a browser by the author of the tests** — the logic,
  markup, geometry and rendered artwork were verified offline, but the in-motion feel
  is reasoned about rather than observed. Please open it on a phone.

## Credits

Built by [iman-coll](https://github.com/iman-coll). All artwork is generated from code
in this repository. Organisation names, addresses and helpline numbers remain the
property of their respective owners and are reproduced only so donors can reach them.
