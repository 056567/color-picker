#nama = adella safitri
#NPM = 140810240094
import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import io
import colorsys

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ColorLens · Palette Extractor",
    page_icon="🎨",
    layout="centered",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #0d0d0f;
    --surface: #161619;
    --surface2: #1f1f24;
    --border: rgba(255,255,255,0.07);
    --text: #f0ede8;
    --muted: #7a7888;
    --accent: #e8c97a;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text);
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

.block-container {
    padding: 2.5rem 2rem 4rem !important;
    max-width: 780px !important;
}

/* Hero */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    color: var(--text);
    line-height: 1.05;
    margin: 0 0 0.5rem;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* Upload zone */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1.5px dashed rgba(232,201,122,0.25) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(232,201,122,0.55) !important;
}
[data-testid="stFileUploader"] label {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--muted) !important;
}

/* Slider */
[data-testid="stSlider"] > div > div > div {
    background: var(--accent) !important;
}

/* Image display */
.img-wrap {
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    margin: 1.5rem 0;
}

/* Palette section */
.palette-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 2rem 0 1rem;
}

.palette-strip {
    display: flex;
    border-radius: 14px;
    overflow: hidden;
    height: 80px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 1.5rem;
}

.color-block {
    flex: 1;
    transition: flex 0.3s ease;
}

.color-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 12px;
    margin-top: 0.5rem;
}

.color-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    font-family: 'DM Sans', sans-serif;
}

.color-swatch {
    height: 72px;
    width: 100%;
}

.color-info {
    padding: 10px 12px;
}

.color-hex {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text);
    letter-spacing: 0.04em;
}

.color-rgb {
    font-size: 0.7rem;
    color: var(--muted);
    margin-top: 2px;
    letter-spacing: 0.02em;
}

.pct-badge {
    display: inline-block;
    font-size: 0.65rem;
    background: rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 2px 7px;
    color: var(--muted);
    margin-top: 4px;
    letter-spacing: 0.03em;
}

/* Section divider */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* Footer */
.footer {
    text-align: center;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    padding-top: 2rem;
}

/* Streamlit overrides */
.stMarkdown p {
    font-family: 'DM Sans', sans-serif;
    color: var(--muted);
}
button[data-testid="baseButton-secondary"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def hex_to_hsl(hex_color):
    r, g, b = int(hex_color[1:3], 16)/255, int(hex_color[3:5], 16)/255, int(hex_color[5:7], 16)/255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h*360, s*100, l*100

def text_color_for_bg(hex_color):
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    luminance = (0.299*r + 0.587*g + 0.114*b) / 255
    return "#000000" if luminance > 0.55 else "#ffffff"

def extract_palette(image: Image.Image, n_colors: int = 5):
    img = image.convert("RGB")
    img.thumbnail((300, 300), Image.LANCZOS)
    pixels = np.array(img).reshape(-1, 3).astype(float)

    kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    labels = kmeans.fit_predict(pixels)
    centers = kmeans.cluster_centers_

    counts = np.bincount(labels, minlength=n_colors)
    total = len(labels)
    percentages = (counts / total * 100).round(1)

    # Sort by count descending
    order = np.argsort(-counts)
    palette = []
    for i in order:
        rgb = centers[i]
        hex_val = rgb_to_hex(rgb)
        palette.append({
            "hex": hex_val,
            "rgb": (int(rgb[0]), int(rgb[1]), int(rgb[2])),
            "pct": percentages[i],
        })
    return palette


# ─── UI ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-title">Color<span>Lens</span></div>
    <div class="hero-sub">Dominant Palette Extractor</div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop your image here, or click to browse",
    type=["jpg", "jpeg", "png", "webp", "bmp"],
    label_visibility="visible",
)

n_colors = st.slider("Number of dominant colors", min_value=3, max_value=10, value=5)

if uploaded:
    image = Image.open(uploaded)
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown('<div class="img-wrap">', unsafe_allow_html=True)
        st.image(image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.spinner("Analyzing colors…"):
        palette = extract_palette(image, n_colors)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="palette-label">🎨 Dominant Palette</div>', unsafe_allow_html=True)

    # ── Palette strip ──
    strip_html = '<div class="palette-strip">'
    for c in palette:
        strip_html += f'<div class="color-block" style="background:{c["hex"]};"></div>'
    strip_html += '</div>'
    st.markdown(strip_html, unsafe_allow_html=True)

    # ── Color cards ──
    cards_html = '<div class="color-cards">'
    for c in palette:
        txt = text_color_for_bg(c["hex"])
        cards_html += f"""
        <div class="color-card">
            <div class="color-swatch" style="background:{c['hex']};"></div>
            <div class="color-info">
                <div class="color-hex">{c['hex']}</div>
                <div class="color-rgb">rgb({c['rgb'][0]}, {c['rgb'][1]}, {c['rgb'][2]})</div>
                <span class="pct-badge">{c['pct']}%</span>
            </div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── CSS snippet export ──
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="palette-label">📋 CSS Variables</div>', unsafe_allow_html=True)
    css_vars = ":root {\n"
    for i, c in enumerate(palette):
        css_vars += f"  --color-{i+1}: {c['hex']};\n"
    css_vars += "}"
    st.code(css_vars, language="css")

else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; font-family:'DM Sans',sans-serif; color: #4a4858;">
        ↑ Upload an image to begin
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">ColorLens · Built with Streamlit & scikit-learn</div>', unsafe_allow_html=True)
