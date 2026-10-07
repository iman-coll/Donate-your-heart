"""Serve the Iman Donation Trust app on Streamlit.

ONE SOURCE OF TRUTH
-------------------
GitHub Pages publishes `docs/`, and this file serves the very same
`docs/index.html` inside an iframe. There is no second copy of the app, no second
copy of the site list, and nothing to keep in sync — a change to `docs/index.html`
appears on both hosts at once.

That is what makes the two deployments behave identically: same HTML, same CSS,
same JavaScript, same strict Content-Security-Policy.
"""

from __future__ import annotations

import pathlib

import streamlit as st
import streamlit.components.v1 as components

REPO_ROOT = pathlib.Path(__file__).resolve().parent
APP = REPO_ROOT / "docs" / "index.html"

st.set_page_config(
    page_title="Iman Donation Trust — donate your things in Pakistan",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Strip Streamlit's own chrome and let the iframe fill the window. `iframe[srcdoc]`
# targets only components.html (external components.iframe(url) uses src, so it is
# left alone), which is what keeps this from breaking if the app ever embeds one.
st.markdown(
    """
    <style>
      #MainMenu, header[data-testid="stHeader"], footer {visibility: hidden; height: 0;}
      .stApp {background: #fdeef2;}
      .block-container {padding: 0 !important; max-width: 100% !important;}
      iframe[srcdoc] {
        display: block;
        width: 100%;
        height: calc(100vh - 1rem);
        border: 0;
        border-radius: 0;
      }
      /* If the rule above is ever ignored by a future Streamlit, the height= argument
         below still gives a usable, scrollable frame. Nothing depends on the CSS. */
    </style>
    """,
    unsafe_allow_html=True,
)

if not APP.exists():
    st.error(
        "**docs/index.html is missing.**\n\n"
        "Keep the repository layout intact — `streamlit_app.py` serves the same file "
        "that GitHub Pages publishes, so the app lives in `docs/`."
    )
    st.stop()

html = APP.read_text(encoding="utf-8")

# Reading the file once and passing the string means no runtime file access from the
# browser, which is what lets the app keep its `connect-src 'none'` policy.
components.html(html, height=1600, scrolling=True)

st.caption(
    "This Streamlit page is only a shell around the same single-file app that runs at "
    "the GitHub Pages URL. All data stays in your browser — nothing is uploaded to "
    "Streamlit either."
)
