"""Serve the Iman Donation Trust app on Streamlit — 100% the same app.

WHY THERE IS NO PYTHON REWRITE
------------------------------
This file does not reimplement the app, and it should not. Streamlit's own HTML
renderer (`st.markdown(..., unsafe_allow_html=True)`) strips every `<script>` tag and
most attributes, so rebuilding the UI with Streamlit widgets would change the fonts,
the canvas-baked mascots, the cursor entourage, the modals, the Zakat calculator and
the ticket — i.e. it would be a different app that merely resembles this one.

Instead the real file is embedded whole. `docs/index.html` is the single source of
truth: GitHub Pages publishes it, and this page hands the identical bytes to the
browser inside an iframe. Nothing is translated, minified, templated or rewritten.

EMBED_MODE
----------
  srcdoc (default)  inline the file's bytes into the page. Independent of GitHub
                    Pages, works offline, byte-identical by construction.
  url               point an iframe at the live Pages URL instead. Even lighter, but
                    it needs the Pages site to be up.
  auto              try srcdoc, fall back to url if the local file is missing.

Everything below the docstring is presentation only: hide Streamlit's own chrome and
let the iframe fill the window, so what you see is the app and nothing else.
"""

from __future__ import annotations

import hashlib
import os
import pathlib

import streamlit as st
import streamlit.components.v1 as components

PAGES_URL = "https://iman-coll.github.io/Donate-your-heart/"
APP_PATH = pathlib.Path(__file__).resolve().parent / "docs" / "index.html"
MODE = os.environ.get("EMBED_MODE", "srcdoc").strip().lower()

st.set_page_config(
    page_title="Iman Donation Trust",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Presentation only. This is CSS, not app code, so it cannot affect the app's
# behaviour — it removes Streamlit's header, toolbar, menu and footer, and pads
# the iframe out to the full window.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      #MainMenu, footer {visibility: hidden; height: 0;}
      header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important; height: 0 !important;
      }
      .stApp {background: #fdeef2;}
      .block-container {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}
      [data-testid="stAppViewContainer"] > section {padding: 0 !important;}
      [data-testid="stVerticalBlock"] {gap: 0 !important;}
      [data-testid="stVerticalBlockBorderWrapper"] {padding: 0 !important;}

      /* The component iframe. Streamlit gives it a fixed pixel height; that is
         overridden here so the app fills the window and its own fixed bottom nav
         lands at the real bottom of the screen. `vh` first, `dvh` second: if a
         browser does not know dvh it simply drops that declaration and keeps vh. */
      iframe[srcdoc], iframe[title="streamlit_component"], [data-testid="stIFrame"] iframe {
        display: block;
        width: 100%;
        height: calc(100vh - 0.5rem);
        height: calc(100dvh - 0.5rem);
        min-height: 620px;
        border: 0;
        border-radius: 0;
      }
      @media (max-width: 640px) {
        iframe[srcdoc], iframe[title="streamlit_component"], [data-testid="stIFrame"] iframe {
          height: calc(100vh - 0.25rem);
          height: calc(100dvh - 0.25rem);
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

html = APP_PATH.read_text(encoding="utf-8") if APP_PATH.exists() else ""
mode = MODE
if mode == "auto":
    mode = "srcdoc" if html else "url"
if mode == "srcdoc" and not html:
    st.warning(
        "**docs/index.html is missing**, so the app cannot be inlined. "
        f"Falling back to the live page at {PAGES_URL}"
    )
    mode = "url"

if mode == "srcdoc":
    # height= is only a fallback for the CSS above; the iframe scrolls internally.
    components.html(html, height=1400, scrolling=True)
else:
    components.iframe(PAGES_URL, height=1400, scrolling=True)

# An opt-in check so you can PROVE the two hosts are serving identical bytes.
# Absent by default, because the whole point is that nothing but the app is visible.
if str(st.query_params.get("check", "")) == "1":
    if html:
        digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
        st.success(
            f"Embedding `docs/index.html` — {len(html):,} bytes, "
            f"sha256 `{digest[:16]}…`, mode `{mode}`. "
            f"This must match the file at {PAGES_URL} exactly."
        )
    else:
        st.info(f"Serving the live page directly from {PAGES_URL} (mode `{mode}`).")
    st.caption(
        "Remove `?check=1` from the URL for the clean, 100%-app view. "
        "The GitHub Pages copy is byte-identical because it is the same file."
    )
