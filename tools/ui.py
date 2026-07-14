import html

import streamlit as st


TOOL_LINKS = [
    ("pages/22 Research Radar.py", "Research Radar", "🛰️"),
    ("pages/23 Global Research Gap Radar.py", "Global Research Gap Radar", "🌐"),
    ("pages/1 Scattertext.py", "Scattertext", "🔀"),
    ("pages/2 Topic Modeling.py", "Topic Modeling", "🧩"),
    ("pages/3 Bidirected Network.py", "Bidirected Network", "🕸️"),
    ("pages/4 Sunburst.py", "Sunburst", "☀️"),
    ("pages/5 Burst Detection.py", "Burst Detection", "🚀"),
    ("pages/6 Keywords Stem.py", "Keywords Stem", "🌱"),
    ("pages/7 Sentiment Analysis.py", "Sentiment Analysis", "😊"),
    ("pages/8 Shifterator.py", "Shifterator", "⚖️"),
    ("pages/9 WordCloud.py", "WordCloud", "☁️"),
    ("pages/10 Histogram.py", "Histogram", "📊"),
    ("pages/11 Pie Chart.py", "Pie Chart", "🥧"),
    ("pages/12 Corpus Overview.py", "Corpus Overview", "🔎"),
    ("pages/13 Data Cleaner.py", "Data Cleaner", "🧹"),
    ("pages/14 Bibliometric Overview.py", "Bibliometric Overview", "📚"),
    ("pages/15 Named Entity Extraction.py", "Named Entity Extraction", "🏷️"),
    ("pages/16 Semantic Search.py", "Semantic Search", "🔍"),
    ("pages/17 Term Keyword Evolution.py", "Term/Keyword Evolution", "📈"),
    ("pages/18 Ask Your Dataset.py", "Ask Your Dataset", "💬"),
    ("pages/19 AI Report Builder.py", "AI Report Builder", "📝"),
    ("pages/20 AI Method Explainer.py", "AI Method Explainer", "🧠"),
    ("pages/21 Text Summarization.py", "Text Summarization", "✂️"),
]

TOOL_THEMES = {
    "Scattertext": ("#0a84ff", "#64d2ff"),
    "Topic Modeling": ("#7c3aed", "#ff7ab6"),
    "Bidirected Network": ("#00a887", "#ffd60a"),
    "Sunburst": ("#ff8a00", "#ff375f"),
    "Burst Detection": ("#ff453a", "#bf5af2"),
    "Keywords Stem": ("#30d158", "#0a84ff"),
    "Sentiment Analysis": ("#ff2d55", "#ffd60a"),
    "Shifterator": ("#5e5ce6", "#30d158"),
    "WordCloud": ("#00c7be", "#ff9f0a"),
    "Histogram Visualization": ("#0071e3", "#30d158"),
    "Histogram": ("#0071e3", "#30d158"),
    "Pie Chart Visualization": ("#ff9f0a", "#ff2d55"),
    "Pie Chart": ("#ff9f0a", "#ff2d55"),
    "Corpus Overview": ("#0a84ff", "#30d158"),
    "Data Cleaner": ("#1b8f5a", "#ffd60a"),
    "Bibliometric Overview": ("#5856d6", "#ff9f0a"),
    "Named Entity Extraction": ("#ff375f", "#64d2ff"),
    "Semantic Search": ("#0071e3", "#bf5af2"),
    "Term/Keyword Evolution": ("#30d158", "#ff9f0a"),
    "Ask Your Dataset": ("#00c7be", "#7c3aed"),
    "AI Report Builder": ("#ff2d55", "#0071e3"),
    "AI Method Explainer": ("#bf5af2", "#30d158"),
    "Text Summarization": ("#0a84ff", "#ff9f0a"),
    "Research Radar": ("#0071e3", "#ff375f"),
    "Global Research Gap Radar": ("#30d158", "#5856d6"),
    "File Checker": ("#1b8f5a", "#0071e3"),
    "Coconut Libtool": ("#0071e3", "#30d158"),
}


THEME_QUERY_KEY = "theme"
THEME_STATE_KEY = "coconut_dark_mode"


def init_theme_state():
    if THEME_STATE_KEY in st.session_state:
        return

    query_theme = st.query_params.get(THEME_QUERY_KEY)
    if isinstance(query_theme, list):
        query_theme = query_theme[0] if query_theme else None

    if query_theme in {"dark", "light"}:
        st.session_state[THEME_STATE_KEY] = query_theme == "dark"
    else:
        st.session_state.setdefault(THEME_STATE_KEY, False)


def _theme_palette():
    init_theme_state()
    if st.session_state[THEME_STATE_KEY]:
        return {
            "text": "#f5f5f7",
            "muted": "#a1a1a6",
            "soft": "#15171c",
            "panel": "rgba(28, 30, 36, 0.88)",
            "panel_strong": "rgba(38, 40, 48, 0.92)",
            "border": "rgba(255, 255, 255, 0.13)",
            "control": "#1c1e24",
            "control_hover": "#64d2ff",
            "primary": "#64d2ff",
            "surface_hover": "#272a32",
            "focus_ring": "rgba(100, 210, 255, 0.42)",
            "control_shine": "rgba(255, 255, 255, 0.24)",
            "mix_base": "#15171c",
            "highlight": "rgba(255, 255, 255, 0.16)",
            "line_soft": "rgba(255, 255, 255, 0.16)",
            "shadow": "0 16px 42px rgba(0, 0, 0, 0.34)",
            "soft_shadow": "0 8px 24px rgba(0, 0, 0, 0.24)",
            "hover_shadow": "0 18px 38px rgba(0, 0, 0, 0.34)",
            "app_background": "linear-gradient(180deg, #101114 0%, #171a20 42%, #0f1116 100%), linear-gradient(115deg, rgba(10, 132, 255, 0.20), rgba(48, 209, 88, 0.12), rgba(255, 159, 10, 0.11), rgba(191, 90, 242, 0.14))",
            "color_scheme": "dark",
        }
    return {
        "text": "#1d1d1f",
        "muted": "#6e6e73",
        "soft": "#f5f5f7",
        "panel": "rgba(255, 255, 255, 0.92)",
        "panel_strong": "rgba(255, 255, 255, 0.94)",
        "border": "rgba(0, 0, 0, 0.08)",
        "control": "#ffffff",
        "control_hover": "#005bb5",
        "primary": "#0071e3",
        "surface_hover": "#f0f6ff",
        "focus_ring": "rgba(0, 113, 227, 0.28)",
        "control_shine": "rgba(255, 255, 255, 0.62)",
        "mix_base": "white",
        "highlight": "rgba(255, 255, 255, 0.88)",
        "line_soft": "rgba(255, 255, 255, 0.72)",
        "shadow": "0 10px 30px rgba(0, 0, 0, 0.06)",
        "soft_shadow": "0 8px 24px rgba(0, 0, 0, 0.04)",
        "hover_shadow": "0 16px 34px rgba(0, 0, 0, 0.08)",
        "app_background": "linear-gradient(180deg, rgba(251, 251, 253, 0.96) 0%, #ffffff 36%, #f5f5f7 100%), linear-gradient(115deg, rgba(0, 113, 227, 0.12), rgba(48, 209, 88, 0.10), rgba(255, 159, 10, 0.10), rgba(255, 45, 85, 0.08))",
        "color_scheme": "light",
    }


def is_dark_mode():
    init_theme_state()
    return bool(st.session_state[THEME_STATE_KEY])


def theme_query_params():
    return {THEME_QUERY_KEY: "dark" if is_dark_mode() else "light"}


def _sync_theme_query_params():
    st.query_params[THEME_QUERY_KEY] = "dark" if st.session_state.get(THEME_STATE_KEY) else "light"


def _apply_plotly_theme():
    try:
        import plotly.io as pio
    except Exception:
        return

    pio.templates.default = "plotly_dark" if is_dark_mode() else "plotly_white"


def apply_app_style():
    _apply_plotly_theme()
    palette = _theme_palette()
    st.markdown(
        """
        <style>
        :root {
            --coconut-text: __COCONUT_TEXT__;
            --coconut-muted: __COCONUT_MUTED__;
            --coconut-soft: __COCONUT_SOFT__;
            --coconut-panel: __COCONUT_PANEL__;
            --coconut-panel-strong: __COCONUT_PANEL_STRONG__;
            --coconut-border: __COCONUT_BORDER__;
            --coconut-control: __COCONUT_CONTROL__;
            --coconut-control-hover: __COCONUT_CONTROL_HOVER__;
            --coconut-primary: __COCONUT_PRIMARY__;
            --coconut-surface-hover: __COCONUT_SURFACE_HOVER__;
            --coconut-focus-ring: __COCONUT_FOCUS_RING__;
            --coconut-control-shine: __COCONUT_CONTROL_SHINE__;
            --coconut-mix-base: __COCONUT_MIX_BASE__;
            --coconut-highlight: __COCONUT_HIGHLIGHT__;
            --coconut-line-soft: __COCONUT_LINE_SOFT__;
            --coconut-blue: #0071e3;
            --coconut-green: #1b8f5a;
            --coconut-pink: #ff2d55;
            --coconut-orange: #ff9f0a;
            --coconut-purple: #7c3aed;
            --coconut-shadow: __COCONUT_SHADOW__;
            --coconut-soft-shadow: __COCONUT_SOFT_SHADOW__;
            --coconut-hover-shadow: __COCONUT_HOVER_SHADOW__;
            --coconut-app-background: __COCONUT_APP_BACKGROUND__;
            color-scheme: __COCONUT_COLOR_SCHEME__;
        }

        @keyframes coconutEnter {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes coconutHeaderShift {
            0%, 100% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
        }

        @keyframes coconutSheen {
            from {
                transform: translateX(-135%) skewX(-16deg);
            }
            to {
                transform: translateX(135%) skewX(-16deg);
            }
        }

        @keyframes coconutSoftPulse {
            0%, 100% {
                box-shadow: var(--coconut-shadow);
            }
            50% {
                box-shadow: 0 16px 42px rgba(0, 113, 227, 0.11);
            }
        }

        @keyframes coconutTileFloat {
            0% {
                opacity: 0.68;
                transform: translateY(26px) scale(0.98) rotate(0.45deg);
            }
            42% {
                opacity: 1;
                transform: translateY(0) scale(1) rotate(0deg);
            }
            70% {
                opacity: 1;
                transform: translateY(-5px) scale(1.012) rotate(-0.22deg);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1) rotate(0deg);
            }
        }

        #MainMenu,
        footer,
        [data-testid="collapsedControl"] {
            visibility: hidden;
            display: none;
        }

        html,
        body,
        [data-testid="stAppViewContainer"],
        .stApp {
            background: var(--coconut-app-background);
            color: var(--coconut-text);
        }

        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            color: var(--coconut-text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
            animation: coconutEnter 420ms cubic-bezier(0.2, 0.8, 0.2, 1);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--coconut-text);
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
            letter-spacing: 0;
        }

        p, li, label, small,
        .stMarkdown,
        [data-testid="stText"],
        [data-testid="stCaptionContainer"],
        [data-testid="stMarkdownContainer"] {
            color: var(--coconut-text);
        }

        a:not([data-testid="stPageLink-NavLink"]) {
            color: var(--coconut-primary);
            text-underline-offset: 0.18em;
        }

        code:not([data-testid="stCodeBlock"] code) {
            border: 1px solid var(--coconut-border);
            border-radius: 5px;
            background: var(--coconut-soft);
            color: var(--coconut-text);
        }

        .coconut-page-header {
            --accent: var(--coconut-blue);
            --accent-2: var(--coconut-green);
            position: relative;
            overflow: hidden;
            margin: 0.15rem 0 1.4rem;
            padding: 1.25rem 1.35rem 1.35rem;
            border: 1px solid var(--coconut-border);
            border-radius: 8px;
            background: var(--coconut-panel);
            background:
                linear-gradient(120deg, var(--coconut-panel-strong), var(--coconut-panel)),
                linear-gradient(120deg, color-mix(in srgb, var(--accent) 18%, transparent), color-mix(in srgb, var(--accent-2) 18%, transparent));
            box-shadow: var(--coconut-shadow);
            animation: coconutEnter 520ms cubic-bezier(0.2, 0.8, 0.2, 1), coconutSoftPulse 6s ease-in-out infinite;
        }

        .coconut-page-header::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 6px;
            background: linear-gradient(180deg, var(--accent), var(--accent-2));
        }

        .coconut-page-header::after {
            content: "";
            position: absolute;
            left: 1.35rem;
            right: 1.35rem;
            bottom: 0;
            height: 3px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent), var(--accent-2), var(--coconut-orange), var(--coconut-pink));
            background-size: 260% 100%;
            animation: coconutHeaderShift 7s ease infinite;
        }

        .coconut-page-header .eyebrow {
            margin: 0 0 0.35rem;
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .coconut-page-header h1 {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.08;
        }

        .coconut-page-header .subtitle {
            max-width: 760px;
            margin: 0.55rem 0 0;
            color: var(--coconut-muted);
            font-size: 1.02rem;
            line-height: 1.55;
        }

        [data-testid="stPopover"] > div > button,
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {
            position: relative;
            overflow: hidden;
            min-height: 2.5rem;
            border: 1px solid rgba(0, 113, 227, 0.22);
            border-radius: 8px;
            background:
                linear-gradient(var(--coconut-control), var(--coconut-control)) padding-box,
                linear-gradient(120deg, rgba(0, 113, 227, 0.35), rgba(48, 209, 88, 0.22), rgba(255, 159, 10, 0.24)) border-box;
            color: var(--coconut-primary);
            font-weight: 650;
            box-shadow: var(--coconut-soft-shadow);
            transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease, color 140ms ease;
        }

        [data-testid="stPopover"] > div > button::after,
        div[data-testid="stButton"] > button::after,
        div[data-testid="stDownloadButton"] > button::after {
            content: "";
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            width: 42%;
            background: linear-gradient(90deg, transparent, var(--coconut-control-shine), transparent);
            transform: translateX(-135%) skewX(-16deg);
        }

        [data-testid="stPopover"] > div > button:hover,
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {
            border-color: rgba(0, 113, 227, 0.55);
            color: var(--coconut-control-hover);
            box-shadow: 0 8px 20px rgba(0, 113, 227, 0.12);
            transform: translateY(-1px);
        }

        [data-testid="stPopover"] > div > button:hover::after,
        div[data-testid="stButton"] > button:hover::after,
        div[data-testid="stDownloadButton"] > button:hover::after {
            animation: coconutSheen 900ms ease;
        }

        div[data-testid="stButton"] > button[kind="primary"] {
            background: var(--coconut-blue);
            color: #ffffff;
        }

        [data-testid="stPopover"] > div > button:focus-visible,
        div[data-testid="stButton"] > button:focus-visible,
        div[data-testid="stDownloadButton"] > button:focus-visible,
        button[data-baseweb="tab"]:focus-visible,
        [data-testid="stPageLink-NavLink"]:focus-visible {
            outline: 3px solid var(--coconut-focus-ring);
            outline-offset: 2px;
        }

        [data-testid="stFileUploader"] {
            padding: 1rem;
            border: 1px dashed rgba(0, 113, 227, 0.45);
            border-radius: 8px;
            background:
                linear-gradient(135deg, var(--coconut-panel), var(--coconut-panel-strong)),
                linear-gradient(135deg, rgba(0, 113, 227, 0.10), rgba(48, 209, 88, 0.09));
            transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: rgba(48, 209, 88, 0.65);
            box-shadow: 0 12px 28px rgba(0, 113, 227, 0.10);
            transform: translateY(-1px);
        }

        [data-testid="stExpander"],
        [data-testid="stForm"],
        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        [data-testid="stPlotlyChart"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--coconut-border);
            border-radius: 8px;
            box-shadow: var(--coconut-soft-shadow);
            transition: border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;
        }

        [data-testid="stExpander"],
        [data-testid="stForm"],
        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        [data-testid="stPlotlyChart"] {
            background: var(--coconut-panel);
        }

        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary p,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"],
        [data-testid="stTable"] th,
        [data-testid="stTable"] td {
            color: var(--coconut-text);
        }

        [data-testid="stExpander"] details {
            border-color: var(--coconut-border) !important;
        }

        [data-testid="stExpander"] summary {
            background: transparent !important;
        }

        [data-testid="stExpander"] summary:hover {
            background: var(--coconut-surface-hover) !important;
        }

        [data-testid="stExpander"] summary svg,
        [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
            color: var(--coconut-muted) !important;
            fill: currentColor !important;
        }

        [data-testid="stMetricLabel"] {
            color: var(--coconut-muted);
        }

        [data-testid="stTable"],
        [data-testid="stTable"] table,
        [data-testid="stCodeBlock"] {
            border-color: var(--coconut-border);
            background: var(--coconut-panel);
            color: var(--coconut-text);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(0, 113, 227, 0.22);
            box-shadow: var(--coconut-hover-shadow);
            transform: translateY(-2px);
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.coconut-home-card) {
            min-height: 354px;
            height: 100%;
            overflow: hidden;
            backdrop-filter: blur(14px);
            transform-origin: center bottom;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.coconut-home-card) > div {
            height: 100%;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.coconut-home-card) div[data-testid="stButton"] {
            margin-top: auto;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.coconut-home-card) div[data-testid="stButton"] > button {
            width: 100%;
        }

        [class*="st-key-workflow_card_"] {
            background: var(--coconut-panel);
        }

        [class*="st-key-workflow_card_"] h3 {
            min-height: 3.2rem;
            margin-top: 0;
            font-size: 1.15rem;
            line-height: 1.25;
        }

        [class*="st-key-workflow_card_"] [data-testid="stCaptionContainer"] {
            min-height: 4.25rem;
        }

        [class*="st-key-workflow_card_"] [data-testid="stPageLink"] {
            width: 100%;
            margin-top: auto;
        }

        [class*="st-key-workflow_card_"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) {
            width: 100%;
            margin-top: auto;
        }

        [class*="st-key-workflow_card_"] [data-testid="stPageLink-NavLink"] {
            display: flex !important;
            width: 100% !important;
            min-height: 2.5rem;
            justify-content: center;
            border: 1px solid rgba(0, 113, 227, 0.24);
            border-radius: 6px;
            background: var(--coconut-control);
            color: var(--coconut-primary);
            font-weight: 650;
            transition: background-color 140ms ease, border-color 140ms ease, transform 140ms ease;
        }

        [class*="st-key-workflow_card_"] [data-testid="stPageLink-NavLink"]:hover {
            border-color: var(--coconut-primary);
            background: var(--coconut-surface-hover);
            transform: translateY(-1px);
        }

        @supports (animation-timeline: view()) {
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.coconut-home-card) {
                animation: coconutTileFloat linear both;
                animation-timeline: view();
                animation-range: entry 0% cover 34%;
            }
        }

        @supports not (animation-timeline: view()) {
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.coconut-home-card) {
                animation: coconutEnter 520ms cubic-bezier(0.2, 0.8, 0.2, 1) both;
            }
        }

        div[data-baseweb="tab-list"],
        [role="tablist"],
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            display: flex !important;
            width: 100% !important;
            gap: 0.35rem !important;
            border-bottom: 1px solid var(--coconut-border);
        }

        div[data-baseweb="tab-list"] > *,
        [role="tablist"] > *,
        [data-testid="stTabs"] [data-baseweb="tab-list"] > * {
            flex: 1 1 0 !important;
            min-width: 0 !important;
        }

        button[data-baseweb="tab"],
        [role="tab"] {
            flex: 1 1 0 !important;
            max-width: none !important;
            min-width: 0 !important;
            min-height: 3.1rem !important;
            padding: 0.65rem 0.75rem !important;
            border-radius: 8px 8px 0 0;
            color: var(--coconut-muted);
            font-weight: 650;
            justify-content: center !important;
            text-align: center !important;
        }

        button[data-baseweb="tab"] p,
        [role="tab"] p {
            width: 100%;
            overflow-wrap: anywhere;
            color: inherit;
            line-height: 1.25;
            text-align: center;
            white-space: normal;
        }

        button[data-baseweb="tab"][aria-selected="true"],
        [role="tab"][aria-selected="true"] {
            color: var(--coconut-primary);
            background:
                linear-gradient(180deg, rgba(0, 113, 227, 0.10), rgba(0, 113, 227, 0.04));
        }

        button[data-baseweb="tab"]:hover:not([aria-selected="true"]),
        [role="tab"]:hover:not([aria-selected="true"]) {
            background: var(--coconut-surface-hover);
            color: var(--coconut-text);
        }

        [data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid var(--coconut-border);
        }

        .stSelectbox, .stTextInput, .stNumberInput, .stSlider {
            margin-bottom: 0.25rem;
        }

        [data-testid="stPopoverBody"] {
            width: clamp(12.5rem, 18vw, 14.5rem) !important;
            min-width: 0 !important;
            max-width: calc(100vw - 2rem) !important;
            max-height: min(72vh, 42rem) !important;
            overflow-y: auto !important;
            padding: 0.7rem !important;
            border: 1px solid var(--coconut-border) !important;
            border-radius: 8px !important;
            background: var(--coconut-control) !important;
            color: var(--coconut-text) !important;
            box-shadow: var(--coconut-shadow) !important;
            scrollbar-color: var(--coconut-muted) transparent;
        }

        [data-testid="stPopoverBody"] > div {
            border-radius: inherit !important;
            background: transparent !important;
            color: var(--coconut-text) !important;
        }

        [data-testid="stPopoverBody"] [data-testid="stPageLink-NavLink"] {
            width: 100%;
            min-height: 2.65rem;
            padding: 0.48rem 0.62rem;
            border-radius: 6px;
            color: var(--coconut-text) !important;
            transition: background-color 140ms ease, color 140ms ease, transform 140ms ease;
        }

        [data-testid="stPopoverBody"] [data-testid="stPageLink-NavLink"]:hover {
            background: var(--coconut-surface-hover);
            color: var(--coconut-primary) !important;
            transform: translateX(2px);
        }

        [data-testid="stPopoverBody"] [data-testid="stPageLink-NavLink"] p,
        [data-testid="stPopoverBody"] [data-testid="stIconEmoji"] {
            color: inherit !important;
        }

        [data-baseweb="input"],
        [data-baseweb="select"] > div,
        [data-baseweb="textarea"],
        [data-baseweb="menu"],
        [data-baseweb="menu"] li,
        [role="listbox"],
        [role="option"],
        textarea {
            border-color: var(--coconut-border) !important;
            background-color: var(--coconut-control) !important;
            color: var(--coconut-text) !important;
        }

        [data-baseweb="menu"],
        [role="listbox"] {
            border: 1px solid var(--coconut-border) !important;
            box-shadow: var(--coconut-shadow) !important;
        }

        [role="option"]:hover,
        [role="option"][aria-selected="true"],
        [data-baseweb="menu"] li:hover {
            background-color: var(--coconut-surface-hover) !important;
        }

        [data-baseweb="select"] svg,
        [data-baseweb="input"] svg {
            color: var(--coconut-muted);
        }

        input,
        textarea,
        [contenteditable="true"] {
            color: var(--coconut-text) !important;
            caret-color: var(--coconut-primary);
        }

        input::placeholder,
        textarea::placeholder {
            color: var(--coconut-muted) !important;
            opacity: 1;
        }

        button:disabled,
        input:disabled,
        textarea:disabled,
        [aria-disabled="true"] {
            color: var(--coconut-muted) !important;
            opacity: 0.72;
        }

        .coconut-theme-label {
            margin: 0 0 0.12rem;
            color: var(--coconut-muted);
            font-size: 0.76rem;
            font-weight: 750;
            letter-spacing: 0.04em;
            text-align: right;
            text-transform: uppercase;
        }

        div[data-testid="stHorizontalBlock"]:has(.coconut-theme-label) {
            align-items: center;
            margin: -0.45rem 0 0.25rem;
        }

        div[data-testid="stHorizontalBlock"]:has(.coconut-theme-label) [data-testid="stToggle"],
        div[data-testid="stHorizontalBlock"]:has(.coconut-theme-label) [data-testid="stCheckbox"] {
            display: flex;
            justify-content: flex-end;
        }

        div[data-testid="stHorizontalBlock"]:has(.coconut-theme-label) [data-testid="stCheckbox"] label {
            margin-left: auto;
        }

        div[data-testid="stHorizontalBlock"]:has(.coconut-theme-label) [data-testid="stWidgetLabel"] p {
            color: var(--coconut-text);
            font-weight: 650;
        }

        .coconut-tool-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            margin-bottom: 0.55rem;
            padding: 0.18rem 0.58rem;
            border-radius: 999px;
            background: rgba(0, 113, 227, 0.08);
            background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 14%, var(--coconut-mix-base)), color-mix(in srgb, var(--accent-2) 14%, var(--coconut-mix-base)));
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.02em;
        }

        .coconut-home-card {
            --accent: var(--coconut-blue);
            --accent-2: var(--coconut-green);
            min-height: 252px;
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }

        .coconut-home-card .coconut-tool-badge {
            width: fit-content;
        }

        .coconut-home-card-media {
            height: 116px;
            display: grid;
            place-items: center;
            overflow: hidden;
            border: 1px solid var(--coconut-line-soft);
            border-radius: 8px;
            background:
                radial-gradient(circle at 24% 18%, var(--coconut-highlight), transparent 26%),
                linear-gradient(135deg, color-mix(in srgb, var(--accent) 22%, var(--coconut-mix-base)), color-mix(in srgb, var(--accent-2) 24%, var(--coconut-mix-base)));
            box-shadow: inset 0 1px 0 var(--coconut-line-soft), 0 10px 22px rgba(0, 0, 0, 0.055);
            color: var(--accent);
            font-size: 2.75rem;
            line-height: 1;
        }

        .coconut-home-card h3 {
            min-height: 2.35rem;
            margin: 0.15rem 0 0;
            color: var(--coconut-text);
            font-size: 1.1rem;
            line-height: 1.18;
            font-weight: 740;
        }

        .coconut-home-card p {
            min-height: 3.35rem;
            margin: 0;
            color: var(--coconut-muted);
            font-size: 0.92rem;
            line-height: 1.42;
        }

        .coconut-icon-tile {
            min-height: 112px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: rgba(0, 113, 227, 0.08);
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--accent) 18%, var(--coconut-mix-base)), color-mix(in srgb, var(--accent-2) 18%, var(--coconut-mix-base)));
            font-size: 3rem;
            animation: coconutHeaderShift 8s ease infinite;
        }

        .coconut-ai-note {
            margin: 0 0 1rem;
            padding: 0.85rem 1rem;
            border: 1px solid rgba(0, 113, 227, 0.16);
            border-radius: 8px;
            background:
                linear-gradient(135deg, var(--coconut-panel), var(--coconut-panel-strong)),
                linear-gradient(135deg, rgba(0, 113, 227, 0.10), rgba(48, 209, 88, 0.08), rgba(255, 159, 10, 0.08));
            color: var(--coconut-muted);
            font-size: 0.95rem;
            line-height: 1.5;
        }

        ::selection {
            background: rgba(0, 113, 227, 0.20);
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.001ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
                transition-duration: 0.001ms !important;
            }
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.25rem;
            }

            .coconut-page-header h1 {
                font-size: 1.7rem;
            }

            div[data-baseweb="tab-list"],
            [role="tablist"],
            [data-testid="stTabs"] [data-baseweb="tab-list"] {
                gap: 0.2rem !important;
            }

            button[data-baseweb="tab"],
            [role="tab"] {
                min-height: 3.25rem !important;
                padding: 0.55rem 0.35rem !important;
                font-size: 0.86rem;
            }

            [data-testid="stPopoverBody"] {
                width: min(18rem, calc(100vw - 2rem)) !important;
                max-height: 68vh !important;
            }
        }
        </style>
        """
        .replace("__COCONUT_TEXT__", palette["text"])
        .replace("__COCONUT_MUTED__", palette["muted"])
        .replace("__COCONUT_SOFT__", palette["soft"])
        .replace("__COCONUT_PANEL__", palette["panel"])
        .replace("__COCONUT_PANEL_STRONG__", palette["panel_strong"])
        .replace("__COCONUT_BORDER__", palette["border"])
        .replace("__COCONUT_CONTROL__", palette["control"])
        .replace("__COCONUT_CONTROL_HOVER__", palette["control_hover"])
        .replace("__COCONUT_PRIMARY__", palette["primary"])
        .replace("__COCONUT_SURFACE_HOVER__", palette["surface_hover"])
        .replace("__COCONUT_FOCUS_RING__", palette["focus_ring"])
        .replace("__COCONUT_CONTROL_SHINE__", palette["control_shine"])
        .replace("__COCONUT_MIX_BASE__", palette["mix_base"])
        .replace("__COCONUT_HIGHLIGHT__", palette["highlight"])
        .replace("__COCONUT_LINE_SOFT__", palette["line_soft"])
        .replace("__COCONUT_SHADOW__", palette["shadow"])
        .replace("__COCONUT_SOFT_SHADOW__", palette["soft_shadow"])
        .replace("__COCONUT_HOVER_SHADOW__", palette["hover_shadow"])
        .replace("__COCONUT_APP_BACKGROUND__", palette["app_background"])
        .replace("__COCONUT_COLOR_SCHEME__", palette["color_scheme"]),
        unsafe_allow_html=True,
    )


def _render_theme_toggle_control():
    init_theme_state()
    st.markdown('<div class="coconut-theme-label">Appearance</div>', unsafe_allow_html=True)
    st.toggle(
        "Dark mode",
        key=THEME_STATE_KEY,
        help="Switch between white and dark mode.",
        on_change=_sync_theme_query_params,
    )


def render_theme_toggle():
    _, toggle_col = st.columns([0.76, 0.24])
    with toggle_col:
        _render_theme_toggle_control()


def render_tool_menu():
    menu_col, toggle_col = st.columns([0.72, 0.28])
    with menu_col:
        with st.popover("Menu"):
            st.page_link("Home.py", label="Home", icon="🏠", query_params=theme_query_params())
            for page, label, icon in TOOL_LINKS:
                st.page_link(page, label=label, icon=icon, query_params=theme_query_params())
    with toggle_col:
        _render_theme_toggle_control()


def render_app_link():
    link_col, toggle_col = st.columns([0.72, 0.28])
    with link_col:
        st.page_link("https://www.coconut-libtool.com/the-app", label="Go to app", icon="🥥")
    with toggle_col:
        _render_theme_toggle_control()


def render_page_header(title, subtitle=None, eyebrow="Coconut Libtool"):
    safe_title = html.escape(title)
    safe_eyebrow = html.escape(eyebrow)
    safe_subtitle = html.escape(subtitle) if subtitle else ""
    subtitle_html = f'<p class="subtitle">{safe_subtitle}</p>' if safe_subtitle else ""
    accent, accent_2 = TOOL_THEMES.get(title, ("#0071e3", "#30d158"))
    st.markdown(
        f"""
        <section class="coconut-page-header" style="--accent: {accent}; --accent-2: {accent_2};">
            <p class="eyebrow">{safe_eyebrow}</p>
            <h1>{safe_title}</h1>
            {subtitle_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def themed_embedded_html(document):
    """Apply Coconut's dark palette to HTML rendered inside an iframe."""
    if not is_dark_mode() or not document:
        return document

    dark_style = """
    <style id="coconut-embedded-theme">
        html, body {
            background: #15171c !important;
            color: #f5f5f7 !important;
            color-scheme: dark;
        }
        text, .label, .axis text, .tick text {
            fill: #f5f5f7 !important;
            color: #f5f5f7 !important;
        }
        .axis path, .axis line, path.domain {
            stroke: #8e8e93 !important;
        }
        a { color: #64d2ff !important; }
    </style>
    """
    if "</head>" in document:
        return document.replace("</head>", f"{dark_style}</head>", 1)
    return f"{dark_style}{document}"


def render_home_tool_card(title, description, target_page, image_path=None, icon=None, button_label=None):
    accent, accent_2 = TOOL_THEMES.get(title, ("#0071e3", "#30d158"))
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="coconut-home-card" style="--accent: {accent}; --accent-2: {accent_2};">
                <div class="coconut-tool-badge" style="--accent: {accent}; --accent-2: {accent_2};">
                    <span>●</span><span>{html.escape(title)}</span>
                </div>
                <div class="coconut-home-card-media">
                    {html.escape(icon or "🥥")}
                </div>
                <h3>{html.escape(title)}</h3>
                <p>{html.escape(description)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(button_label or f"Go to {title}", key=f"home_{target_page}"):
            st.switch_page(target_page, query_params=theme_query_params())
