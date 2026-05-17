"""
styles.py — High-End Command Center Dashboard CSS.

FIXES:
  1. Removed `header { visibility: hidden; }` — this was hiding the sidebar
     toggle button, making it impossible to open the sidebar.
  2. Fixed `[data-testid="stSidebar"] * { color: ... }` — this was overriding
     file uploader and widget colors making them invisible/unclickable.
  3. Added explicit sidebar toggle button visibility fix.
"""

def get_custom_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

/* COMMAND CENTER VARIABLES */
:root {
    --bg-main: #141416;
    --bg-card: #1D1E24;
    --bg-card-hover: #262831;
    --border-color: #2F313E;

    --text-main: #FFFFFF;
    --text-muted: #8F95B2;
    --text-accent: #00FFCC;

    --neon-green: #00FF9D;
    --neon-blue: #00E5FF;
    --neon-pink: #FF3366;
    --neon-orange: #FF8800;
    --neon-yellow: #FFCC00;

    --font-sans: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

/* GLOBAL STREAMLIT OVERRIDES */
.stApp {
    background-color: var(--bg-main);
    color: var(--text-main);
    font-family: var(--font-sans);
}

.main .block-container {
    max-width: 1300px;
    padding-top: 2rem;
}

/* FIX: Only hide footer and main menu — NOT header.
   Hiding header also hides the sidebar collapse/expand toggle button. */
#MainMenu, footer { visibility: hidden; }

/* FIX: Force sidebar toggle button to always be visible */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    color: #00FFCC !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #0F0F11 !important;
    border-right: 1px solid var(--border-color);
}

/* FIX: Don't override ALL sidebar child colors — only text nodes.
   The old rule broke file uploader, buttons, and widgets inside sidebar. */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption {
    color: var(--text-muted) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-main) !important;
    font-family: var(--font-mono) !important;
    letter-spacing: 1px;
}

/* File uploader in sidebar — keep it visible and styled */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1px dashed #00FFCC !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] * {
    color: #FFFFFF !important;
}
[data-testid="stFileUploader"] button {
    background: var(--bg-card) !important;
    border: 1px solid #00FFCC !important;
    color: #00FFCC !important;
    border-radius: 8px !important;
}

/* File chip for file list in sidebar */
.file-chip {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
    font-family: var(--font-mono);
    color: var(--text-muted) !important;
    margin-bottom: 4px;
}

/* Status bars in sidebar */
.status-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 1px;
}
.status-bar.ready {
    background: rgba(0, 255, 157, 0.08);
    border: 1px solid rgba(0, 255, 157, 0.3);
    color: var(--neon-green) !important;
}
.status-bar.idle {
    background: rgba(143, 149, 178, 0.08);
    border: 1px solid var(--border-color);
    color: var(--text-muted) !important;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
}

/* TOP STATUS BAR */
.status-dashboard {
    background: rgba(0, 255, 157, 0.05);
    border: 1px solid rgba(0, 255, 157, 0.2);
    border-radius: 8px;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    margin-bottom: 30px;
}
.status-pulse {
    width: 10px; height: 10px;
    background-color: var(--neon-green);
    border-radius: 50%;
    box-shadow: 0 0 10px var(--neon-green);
    animation: pulse-neon 1.5s infinite;
}
.status-text {
    font-family: var(--font-mono);
    color: var(--neon-green);
    font-size: 14px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* NEON BUTTONS */
.stButton > button {
    background: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
}
.stButton > button:hover {
    border-color: var(--neon-blue) !important;
    color: var(--neon-blue) !important;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.2) !important;
    transform: translateY(-2px) !important;
}

/* INPUT FIELDS */
.stChatInputContainer, .stChatInputContainer > div {
    border-color: var(--border-color) !important;
}
.stChatInput textarea,
.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"] > div:first-child {
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    font-family: var(--font-sans) !important;
}
.stChatInput textarea:focus,
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--neon-blue) !important;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.1) !important;
}

/* DASHBOARD CARDS */
.dash-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    transition: all 0.3s ease;
}
.dash-card:hover {
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.card-pink   { border-top: 3px solid var(--neon-pink);   background: linear-gradient(180deg, rgba(255,51,102,0.05)  0%, var(--bg-card) 40%); }
.card-blue   { border-top: 3px solid var(--neon-blue);   background: linear-gradient(180deg, rgba(0,229,255,0.05)   0%, var(--bg-card) 40%); }
.card-green  { border-top: 3px solid var(--neon-green);  background: linear-gradient(180deg, rgba(0,255,157,0.05)   0%, var(--bg-card) 40%); }
.card-orange { border-top: 3px solid var(--neon-orange); background: linear-gradient(180deg, rgba(255,136,0,0.05)   0%, var(--bg-card) 40%); }
.card-icon  { font-size: 24px; margin-bottom: 10px; }
.card-title {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 5px;
}
.card-value { font-size: 24px; font-weight: 700; color: var(--text-main); }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: 8px;
    padding: 5px;
    border: 1px solid var(--border-color);
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-size: 12px !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--neon-blue) !important;
    background: rgba(0, 229, 255, 0.1) !important;
    border-radius: 4px !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* CHAT BUBBLES */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
}

/* ALERTS */
.stAlert > div {
    background-color: #2b2b00 !important;
    color: #FFFFFF !important;
    border-color: #cccc00 !important;
}
.stAlert [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
}

/* AVATARS */
[data-testid="stChatMessageAvatarUser"]      { background-color: var(--neon-blue)  !important; }
[data-testid="stChatMessageAvatarAssistant"] { background-color: var(--neon-green) !important; }

@keyframes pulse-neon {
    0%   { box-shadow: 0 0 0 0   rgba(0, 255, 157, 0.4); }
    70%  { box-shadow: 0 0 0 10px rgba(0, 255, 157, 0);   }
    100% { box-shadow: 0 0 0 0   rgba(0, 255, 157, 0);    }
}
</style>
"""