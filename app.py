"""maru_homepage (Streamlit)

まるの個人サイト（日本株特化）。

要件
 - 画面上に「URLを貼る」入力欄は出さない（埋め込みは site_config.json を編集）
 - 上部タブでナビ（左サイドバーは使わない）
 - ホームで全体像（自己紹介/指数/note/Shopify/Instagram/Threads/勉強会）が分かる
 - 指数は yfinance を利用（失敗時は static/market.json にフォールバック）
 - 後から追加しやすい（site_config.json に追記するだけ）
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import streamlit as st
import streamlit.components.v1 as components

try:
    import yfinance as yf  # type: ignore
except Exception:  # pragma: no cover
    yf = None


# =========================
# Config
# =========================


@dataclass
class SiteConfig:
    name: str
    tagline: str
    focus_badge: str
    bio: str
    note_embeds: list[str]
    shopify_embed: str
    instagram_url: str
    instagram_label: str
    threads_url: str
    threads_label: str
    study_form_embed: str
    study_form_fallback_url: str


DEFAULT_CONFIG = SiteConfig(
    name="まる",
    tagline="日本株 × テクノロジー × クリエイティブ",
    focus_badge="日本株特化",
    bio=(
        "名古屋を拠点に活動する投資家・クリエイター。日本株を中心に、\n"
        "テクノロジーと金融の融合に魅力を感じながら日々学びを深めています。\n"
        "noteや勉強会、プロダクトを通じて“学びを続けられる場所”を作っています。"
    ),
    note_embeds=[],
    shopify_embed="",
    instagram_url="https://www.instagram.com/maru_update/",
    instagram_label="@maru_update",
    threads_url="https://www.threads.net/@maru_update",
    threads_label="@maru_update",
    study_form_embed="",
    study_form_fallback_url="",
)


def load_config() -> SiteConfig:
    cfg_path = Path(__file__).with_name("site_config.json")
    if not cfg_path.exists():
        return DEFAULT_CONFIG

    try:
        raw = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_CONFIG

    def g(path: list[str], default: Any) -> Any:
        cur: Any = raw
        for k in path:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    return SiteConfig(
        name=str(g(["profile", "name"], DEFAULT_CONFIG.name)),
        tagline=str(g(["profile", "tagline"], DEFAULT_CONFIG.tagline)),
        focus_badge=str(g(["profile", "focus_badge"], DEFAULT_CONFIG.focus_badge)),
        bio=str(g(["profile", "bio"], DEFAULT_CONFIG.bio)),
        note_embeds=list(g(["embeds", "note"], DEFAULT_CONFIG.note_embeds) or []),
        shopify_embed=str(g(["embeds", "shopify"], DEFAULT_CONFIG.shopify_embed) or ""),
        instagram_url=str(g(["links", "instagram_url"], DEFAULT_CONFIG.instagram_url)),
        instagram_label=str(g(["links", "instagram_label"], DEFAULT_CONFIG.instagram_label)),
        threads_url=str(g(["links", "threads_url"], DEFAULT_CONFIG.threads_url)),
        threads_label=str(g(["links", "threads_label"], DEFAULT_CONFIG.threads_label)),
        study_form_embed=str(g(["embeds", "study_form"], DEFAULT_CONFIG.study_form_embed) or ""),
        study_form_fallback_url=str(
            g(["links", "study_form_url"], DEFAULT_CONFIG.study_form_fallback_url) or ""
        ),
    )


# =========================
# Styling
# =========================


def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+JP:wght@400;600;700;800&display=swap');

:root{
  --bgA:#0b1020;
  --bgB:#101a33;
  --glass:rgba(255,255,255,.08);
  --glass2:rgba(255,255,255,.12);
  --border:rgba(255,255,255,.14);
  --text:#eef2ff;
  --muted:rgba(238,242,255,.72);
  --accent:#7c3aed; /* violet */
  --accent2:#22d3ee; /* cyan */
  --shadow:0 22px 80px rgba(0,0,0,.45);
  --shadow2:0 14px 40px rgba(0,0,0,.35);
  --r:22px;
}

html, body, [class*="css"]{
  font-family:'Inter','Noto Sans JP',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
}

.stApp{
  background:
    radial-gradient(1200px 700px at 10% 10%, rgba(124,58,237,.35), transparent 60%),
    radial-gradient(1100px 700px at 90% 15%, rgba(34,211,238,.25), transparent 60%),
    linear-gradient(180deg, var(--bgA) 0%, var(--bgB) 70%, #0a0f1e 100%);
  color:var(--text);
}

/* Remove default Streamlit chrome */
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{visibility:hidden;}

/* Hide sidebar completely */
[data-testid="stSidebar"]{display:none;}

/* Content width */
.block-container{
  max-width:1320px;
  padding-top:0.9rem;
  padding-bottom:3.2rem;
}

/* Tabs as top nav */
.stTabs [data-baseweb="tab-list"]{
  gap:.35rem;
  background:linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.04));
  border:1px solid var(--border);
  border-radius:999px;
  padding:.35rem;
  box-shadow:var(--shadow2);
  backdrop-filter: blur(14px);
}
.stTabs [data-baseweb="tab"]{
  color:var(--muted);
  font-weight:800;
  border-radius:999px;
  padding:.55rem .9rem;
}
.stTabs [data-baseweb="tab"][aria-selected="true"]{
  color:var(--text);
  background:linear-gradient(135deg, rgba(124,58,237,.95), rgba(34,211,238,.55));
  box-shadow:0 10px 26px rgba(124,58,237,.25);
}

/* Cards */
.card{
  background:var(--glass);
  border:1px solid var(--border);
  border-radius:var(--r);
  box-shadow:var(--shadow2);
  padding:1.1rem 1.1rem;
  backdrop-filter: blur(14px);
}
.card h3{margin:0 0 .4rem 0; font-size:1.05rem; letter-spacing:.01em;}
.muted{color:var(--muted);}

.hero{
  border-radius:28px;
  border:1px solid rgba(255,255,255,.16);
  background:linear-gradient(135deg, rgba(124,58,237,.28), rgba(34,211,238,.12));
  box-shadow:var(--shadow);
  padding:1.4rem 1.4rem;
  margin-bottom:1.1rem;
  position:relative;
  overflow:hidden;
}
.hero:before{
  content:"";
  position:absolute;
  inset:-70px;
  background:
    radial-gradient(circle at 20% 20%, rgba(124,58,237,.55), transparent 55%),
    radial-gradient(circle at 80% 15%, rgba(34,211,238,.35), transparent 55%);
  filter: blur(18px);
}
.hero > div{position:relative;}
.badge{
  display:inline-flex;
  align-items:center;
  gap:.45rem;
  padding:.35rem .7rem;
  border-radius:999px;
  background:rgba(255,255,255,.10);
  border:1px solid rgba(255,255,255,.16);
  font-weight:800;
  color:var(--text);
  font-size:.85rem;
}
.title{margin:.6rem 0 .2rem 0; font-size:2.35rem; font-weight:900;}
.sub{margin:0 0 .85rem 0; color:var(--muted); font-size:1.05rem;}

.pillrow{display:flex; gap:.6rem; flex-wrap:wrap;}
.pill{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding:.55rem .95rem;
  border-radius:999px;
  font-weight:900;
  color:var(--text);
  text-decoration:none;
  background:linear-gradient(135deg, rgba(124,58,237,.95), rgba(34,211,238,.6));
  box-shadow:0 10px 26px rgba(0,0,0,.28);
}
.pill.ghost{background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18);}

.kpis{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; margin-top:.5rem;}
.kpi{
  background:rgba(255,255,255,.09);
  border:1px solid rgba(255,255,255,.14);
  border-radius:18px;
  padding:.85rem .85rem;
}
.kpi .l{font-weight:800; color:var(--muted); font-size:.84rem;}
.kpi .v{font-weight:950; font-size:1.25rem; margin-top:.2rem;}

@media (max-width: 900px){
  .kpis{grid-template-columns:1fr;}
  .title{font-size:2.05rem;}
}

/* Sticky market ticker (top) */
.tickerbar{
  position: sticky;
  top: 0;
  z-index: 999;
  margin: 0 0 .65rem 0;
  padding: .55rem .85rem;
  border-radius: 999px;
  background: rgba(12,16,30,.55);
  border: 1px solid rgba(255,255,255,.14);
  box-shadow: 0 18px 55px rgba(0,0,0,.35);
  backdrop-filter: blur(16px);
}
.tickergrid{
  display:flex;
  align-items:center;
  gap:.9rem;
  flex-wrap:wrap;
}
.tickeritem{
  display:flex;
  align-items:baseline;
  gap:.45rem;
  padding:.18rem .55rem;
  border-radius: 999px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.10);
}
.tickeritem .k{font-weight:900; color: rgba(238,242,255,.78); font-size:.82rem;}
.tickeritem .v{font-weight:950; color: var(--text); font-size:.95rem;}
.tickersep{flex:1 1 auto; min-width: 180px;}
.marquee{
  overflow:hidden;
  white-space:nowrap;
  position:relative;
  mask-image: linear-gradient(90deg, transparent 0%, black 12%, black 88%, transparent 100%);
}
.marquee span{
  display:inline-block;
  padding-left: 100%;
  animation: marquee 18s linear infinite;
  color: rgba(238,242,255,.68);
  font-weight:800;
  font-size:.82rem;
}
@keyframes marquee{ 0%{transform:translateX(0);} 100%{transform:translateX(-100%);} }

/* Animated aura background (subtle motion) */
.stApp:before{
  content:"";
  position:fixed;
  inset:-200px;
  z-index:-1;
  background:
    radial-gradient(circle at 20% 20%, rgba(124,58,237,.35), transparent 55%),
    radial-gradient(circle at 80% 10%, rgba(34,211,238,.25), transparent 55%),
    radial-gradient(circle at 60% 90%, rgba(16,185,129,.18), transparent 60%);
  filter: blur(18px);
  animation: drift 14s ease-in-out infinite alternate;
}
@keyframes drift{
  0%{transform:translate3d(-18px,-10px,0) scale(1.02);}
  100%{transform:translate3d(18px,12px,0) scale(1.06);}
}

/* Embed cards: remove extra padding and tighten layout */
.card.embed{padding:0; overflow:hidden;}
.tight{margin-top:.2rem;}

/* Hover polish */
.card{transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;}
.card:hover{transform: translateY(-3px); border-color: rgba(255,255,255,.22); box-shadow: var(--shadow);}
.pill{transition: transform .18s ease, filter .18s ease;}
.pill:hover{transform: translateY(-2px); filter: brightness(1.06);}

/* Sticky tabs below ticker */
.stTabs [data-baseweb="tab-list"]{
  position: sticky;
  top: 66px; /* below ticker */
  z-index: 998;
}

/* Pulse dot */
.pdot{
  width:8px;height:8px;border-radius:999px;
  background: rgba(34,211,238,.95);
  box-shadow:0 0 0 0 rgba(34,211,238,.55);
  animation:pulse 1.8s ease-out infinite;
}
@keyframes pulse{
  0%{box-shadow:0 0 0 0 rgba(34,211,238,.55);}
  70%{box-shadow:0 0 0 10px rgba(34,211,238,0);}
  100%{box-shadow:0 0 0 0 rgba(34,211,238,0);}
}


</style>
        """,
        unsafe_allow_html=True,
    )


def hero(cfg: SiteConfig) -> None:
    st.markdown(
        f"""
<div class="hero">
  <div>
    <div class="badge">📈 {cfg.focus_badge}</div>
    <div class="title">{cfg.name}</div>
    <div class="sub">{cfg.tagline}</div>
    <div class="pillrow">
      <a class="pill" href="{cfg.instagram_url}" target="_blank" rel="noopener">Instagram</a>
      <a class="pill" href="{cfg.threads_url}" target="_blank" rel="noopener">Threads</a>
      <a class="pill ghost" href="#" onclick="window.scrollTo(0,0)">Home</a>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Market data (yfinance)
# =========================


def _safe_last_close(df: Any) -> float | None:
    try:
        if df is None or len(df) == 0:
            return None
        # yfinance may return multi-index columns depending on version
        if hasattr(df, "columns") and "Close" in df.columns:
            s = df["Close"].dropna()
            return float(s.iloc[-1]) if len(s) else None
        # MultiIndex: ('Close', ticker)
        if hasattr(df, "columns") and isinstance(df.columns, type(getattr(df.columns, "__class__", object))):
            # try common patterns
            for col in df.columns:
                if isinstance(col, tuple) and len(col) >= 1 and col[0] == "Close":
                    s = df[col].dropna()
                    return float(s.iloc[-1]) if len(s) else None
        return None
    except Exception:
        return None


@st.cache_data(ttl=60 * 10, show_spinner=False)
def _fetch_close_yf(ticker: str) -> float | None:
    if yf is None:
        return None
    try:
        df = yf.download(ticker, period="7d", interval="1d", progress=False)
        return _safe_last_close(df)
    except Exception:
        return None


def _fallback_market_json() -> dict[str, float | None]:
    try:
        p = Path(__file__).parent / "static" / "market.json"
        if not p.exists():
            return {"nikkei": None, "usdjpy": None, "jgb10y": None}
        d = json.loads(p.read_text(encoding="utf-8"))
        return {
            "nikkei": float(d.get("nikkei")) if d.get("nikkei") is not None else None,
            "usdjpy": float(d.get("usdjpy")) if d.get("usdjpy") is not None else None,
            "jgb10y": float(d.get("jgb_yield")) if d.get("jgb_yield") is not None else None,
        }
    except Exception:
        return {"nikkei": None, "usdjpy": None, "jgb10y": None}


def fetch_market_snapshot() -> dict[str, Any]:
    """Return market snapshot using yfinance.

    - Nikkei225: ^N225
    - USDJPY  : JPY=X (or USDJPY=X)
    - JGB10Y  : try JP10YT=XX/JP10YT=RR (not always available), otherwise ^JGBL (JGB futures)
    """
    nikkei = _fetch_close_yf("^N225")
    usdjpy = _fetch_close_yf("JPY=X") or _fetch_close_yf("USDJPY=X")

    jgb_val: float | None = None
    jgb_label = "日本10年債"
    jgb_suffix = "%"
    for tkr, label, suffix in [
        ("JP10YT=XX", "日本10年債利回り", "%"),
        ("JP10YT=RR", "日本10年債利回り", "%"),
        ("^JGBL", "日本国債先物（参考）", ""),
    ]:
        v = _fetch_close_yf(tkr)
        if v is not None:
            jgb_val, jgb_label, jgb_suffix = v, label, suffix
            break

    # fallback
    fb = _fallback_market_json()
    if nikkei is None:
        nikkei = fb["nikkei"]
    if usdjpy is None:
        usdjpy = fb["usdjpy"]
    if jgb_val is None:
        jgb_val = fb["jgb10y"]
        jgb_label = "日本10年債利回り（fallback）"
        jgb_suffix = "%"

    return {
        "nikkei": nikkei,
        "usdjpy": usdjpy,
        "jgb": jgb_val,
        "jgb_label": jgb_label,
        "jgb_suffix": jgb_suffix,
    }


def fmt_num(x: float | None, suffix: str = "") -> str:
    if x is None:
        return "--"
    try:
        return f"{x:,.2f}{suffix}"
    except Exception:
        return "--"


# =========================
# Embeds
# =========================


def wrap_embed(embed_html: str) -> str:
    """Embed HTML safely into components.html with consistent sizing."""
    return f"""<!doctype html>
<html lang='ja'>
<head>
  <meta charset='utf-8'/>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'/>
  <style>
    html,body{{margin:0;padding:0;background:transparent;}}
    iframe{{width:100% !important; max-width:100% !important; border:0;}}
  </style>
</head>
<body>
{embed_html}
</body>
</html>"""




def extract_iframe_src(embed_html: str) -> str | None:
    """Extract iframe src from an embed snippet (noteなど).

    We intentionally ignore <script> tags to avoid extra placeholder UI.
    """
    if not embed_html:
        return None
    m = re.search(r"src=['\"]([^'\"]+)['\"]", embed_html)
    return m.group(1) if m else None


def render_tickerbar(snap: dict[str, Any]) -> None:
    """Render a sticky top market ticker bar (CSS animated)."""
    nik = fmt_num(snap.get("nikkei"))
    fx = fmt_num(snap.get("usdjpy"))
    jgb = fmt_num(snap.get("jgb"), snap.get("jgb_suffix", ""))
    jgb_label = str(snap.get("jgb_label", "日本10年債"))

    message = f"Nikkei {nik}  •  USDJPY {fx}  •  {jgb_label} {jgb}  •  日本株に特化した学びと発信  •  "
    st.markdown(
        f"""
<div class="tickerbar">
  <div class="tickergrid">
    <div class="tickeritem"><span class="pdot"></span><span class="k">LIVE</span></div><div class="tickeritem"><span class="k">日経平均</span><span class="v">{nik}</span></div>
    <div class="tickeritem"><span class="k">ドル円</span><span class="v">{fx}</span></div>
    <div class="tickeritem"><span class="k">{jgb_label}</span><span class="v">{jgb}</span></div>
    <div class="tickersep"></div>
    <div class="marquee"><span>{message}{message}</span></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )



# =========================
# Pages
# =========================


def page_home(cfg: SiteConfig) -> None:
    # NOTE: top of page already renders a sticky tickerbar in main().
    snap = fetch_market_snapshot()

    # --- Top: profile + market (tighter layout, less blank space) ---
    left, right = st.columns([1.2, 0.8], gap="medium")
    with left:
        st.markdown(
            f"""
<div class="card">
  <h3>まるについて</h3>
  <div class="muted">{cfg.bio.replace(chr(10), '<br/>')}</div>
  <div style="height:.75rem"></div>
  <div class="pillrow">
    <a class="pill" href="{cfg.instagram_url}" target="_blank" rel="noopener">Instagram</a>
    <a class="pill" href="{cfg.threads_url}" target="_blank" rel="noopener">Threads</a>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
<div class="card">
  <h3>市場（yfinance）</h3>
  <div class="kpis">
    <div class="kpi"><div class="l">日経平均</div><div class="v">{fmt_num(snap['nikkei'])}</div></div>
    <div class="kpi"><div class="l">ドル円</div><div class="v">{fmt_num(snap['usdjpy'])}</div></div>
    <div class="kpi"><div class="l">{snap['jgb_label']}</div><div class="v">{fmt_num(snap['jgb'], snap['jgb_suffix'])}</div></div>
  </div>
  <div class="muted" style="margin-top:.55rem; font-size:.85rem;">更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:.45rem'></div>", unsafe_allow_html=True)

    # --- Latest note (remove scripts -> iframe only) ---
    st.markdown("### 最新note")
    if cfg.note_embeds:
        cols = st.columns(3, gap="medium")
        for i, emb in enumerate(cfg.note_embeds[:3]):
            src = extract_iframe_src(emb) or "about:blank"
            with cols[i % 3]:
                st.markdown("<div class='card embed'>", unsafe_allow_html=True)
                components.iframe(src, height=420, scrolling=False)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='card muted'>noteが未設定です。site_config.json の embeds.note に iframe を追加するとここに表示されます。</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:.45rem'></div>", unsafe_allow_html=True)

    # --- Shop: full-width (avoid column height gaps) ---
    st.markdown("### ショップ")
    st.markdown("<div class='card embed'>", unsafe_allow_html=True)
    if cfg.shopify_embed.strip():
        components.html(wrap_embed(cfg.shopify_embed), height=620, scrolling=False)
    else:
        st.markdown(
            "<div class='muted' style='padding:1rem'>Shopifyが未設定です。site_config.json の embeds.shopify にBuy Buttonコードを貼ると表示されます。</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:.45rem'></div>", unsafe_allow_html=True)

    # --- Study + Social (balanced two-column) ---
    c1, c2 = st.columns([1.0, 1.0], gap="medium")
    with c1:
        st.markdown("### 勉強会")
        st.markdown("<div class='card embed'>", unsafe_allow_html=True)
        if cfg.study_form_embed.strip():
            components.html(wrap_embed(cfg.study_form_embed), height=520, scrolling=True)
        elif cfg.study_form_fallback_url.strip():
            st.markdown(
                f"<div class='muted' style='padding:1rem'>外部フォームで受付中です。</div>"
                f"<div style='padding:0 1rem 1rem 1rem'><a class='pill' href='{cfg.study_form_fallback_url}' target='_blank' rel='noopener'>申し込みへ</a></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='muted' style='padding:1rem'>準備中。Googleフォームのiframeを site_config.json に貼るだけでここに表示されます。</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("### Instagram / Threads")
        st.markdown(
            f"""
<div class="card">
  <div class="muted">SNSは <b>{cfg.instagram_label}</b> で統一。</div>
  <div style="height:.75rem"></div>
  <div class="pillrow">
    <a class="pill" href="{cfg.instagram_url}" target="_blank" rel="noopener">Instagramへ</a>
    <a class="pill" href="{cfg.threads_url}" target="_blank" rel="noopener">Threadsへ</a>
  </div>
  <div style="height:.85rem"></div>
  <div class="muted" style="font-size:.9rem">上のティッカーはスクロールしても追従します。</div>
</div>
            """,
            unsafe_allow_html=True,
        )


def page_intro(cfg: SiteConfig) -> None:
    st.markdown(
        f"""
<div class="card">
  <h3>プロフィール</h3>
  <div class="muted">{cfg.bio.replace(chr(10), '<br/>')}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def page_note(cfg: SiteConfig) -> None:
    if not cfg.note_embeds:
        st.markdown(
            "<div class='card muted'>noteが未設定です。site_config.json の embeds.note に iframe を追加してね。</div>",
            unsafe_allow_html=True,
        )
        return
    cols = st.columns(3)
    for i, emb in enumerate(cfg.note_embeds):
        with cols[i % 3]:
            st.markdown("<div class='card embed'>", unsafe_allow_html=True)
            components.iframe(extract_iframe_src(emb) or "about:blank", height=430, scrolling=False)
            st.markdown("</div>", unsafe_allow_html=True)


def page_shop(cfg: SiteConfig) -> None:
    st.markdown(
        "<div class='card muted'>Shopify Buy Button をそのまま表示しています。</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("<div class='card embed'>", unsafe_allow_html=True)
    if cfg.shopify_embed.strip():
        components.html(wrap_embed(cfg.shopify_embed), height=780, scrolling=False)
    else:
        st.markdown(
            "<div class='muted'>未設定です。site_config.json の embeds.shopify に貼り付けてね。</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def page_social(cfg: SiteConfig) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
<div class="card">
  <h3>Instagram</h3>
  <div class="muted">最新の告知・まとめはこちら。</div>
  <div style="height:.8rem"></div>
  <a class="pill" href="{cfg.instagram_url}" target="_blank" rel="noopener">{cfg.instagram_label}</a>
</div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
<div class="card">
  <h3>Threads</h3>
  <div class="muted">日々のメモ・気づきはThreadsへ。</div>
  <div style="height:.8rem"></div>
  <a class="pill" href="{cfg.threads_url}" target="_blank" rel="noopener">{cfg.threads_label}</a>
</div>
            """,
            unsafe_allow_html=True,
        )


def page_study(cfg: SiteConfig) -> None:
    st.markdown(
        "<div class='card muted'>申し込みフォームをここに表示します。Googleフォームのiframeを貼るだけでOK。</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("<div class='card embed'>", unsafe_allow_html=True)
    if cfg.study_form_embed.strip():
        components.html(wrap_embed(cfg.study_form_embed), height=780, scrolling=True)
    elif cfg.study_form_fallback_url.strip():
        st.markdown(
            f"<div class='muted'>外部フォームで受付中です。</div><div style='height:.7rem'></div>"
            f"<a class='pill' href='{cfg.study_form_fallback_url}' target='_blank' rel='noopener'>申し込みへ</a>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='muted'>準備中。site_config.json に iframe を貼るとここに表示されます。</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def page_market(_: SiteConfig) -> None:
    snap = fetch_market_snapshot()
    st.markdown(
        f"""
<div class="card">
  <h3>市場指数</h3>
  <div class="kpis">
    <div class="kpi"><div class="l">日経平均（^N225）</div><div class="v">{fmt_num(snap['nikkei'])}</div></div>
    <div class="kpi"><div class="l">ドル円（JPY=X）</div><div class="v">{fmt_num(snap['usdjpy'])}</div></div>
    <div class="kpi"><div class="l">{snap['jgb_label']}</div><div class="v">{fmt_num(snap['jgb'], snap['jgb_suffix'])}</div></div>
  </div>
  <div class="muted" style="margin-top:.6rem; font-size:.9rem;">
    ※ 日本10年債はデータソースの都合で取得できない場合があり、その際は同梱の market.json を表示します。
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def page_tech(_: SiteConfig) -> None:
    st.markdown(
        "<div class='card muted'>Webの動きは JavaScript（Javaとは別物）で作ります。<br/>"
        "このサイトでは <b>Python（Streamlit）</b> で表示しつつ、<b>Java</b> の取得サンプルも同梱しています。</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:.45rem'></div>", unsafe_allow_html=True)

    st.markdown("### 動くデモ（JavaScript）")
    components.html(
        """<!doctype html>
<html><head>
<meta charset="utf-8">
<style>
  body{margin:0;background:transparent;}
  .wrap{
    border-radius:18px;
    border:1px solid rgba(255,255,255,.14);
    background:rgba(255,255,255,.06);
    padding:14px;
  }
  canvas{width:100%; height:180px; display:block; border-radius:14px;}
</style>
</head>
<body>
  <div class="wrap">
    <canvas id="c" width="900" height="180"></canvas>
  </div>
<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
let t = 0;
function draw(){
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0,0,w,h);
  // gradient line
  const g = ctx.createLinearGradient(0,0,w,0);
  g.addColorStop(0, 'rgba(124,58,237,0.95)');
  g.addColorStop(1, 'rgba(34,211,238,0.85)');
  ctx.strokeStyle = g;
  ctx.lineWidth = 3;
  ctx.beginPath();
  for(let x=0; x<w; x++){
    const y = h/2 + Math.sin((x/70) + t)*26 + Math.sin((x/22) - t*0.6)*8;
    if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  }
  ctx.stroke();
  // moving dot
  const px = (t*110) % w;
  const py = h/2 + Math.sin((px/70) + t)*26 + Math.sin((px/22) - t*0.6)*8;
  ctx.fillStyle = 'rgba(255,255,255,0.95)';
  ctx.beginPath(); ctx.arc(px, py, 5.5, 0, Math.PI*2); ctx.fill();
  t += 0.02;
  requestAnimationFrame(draw);
}
draw();
</script>
</body></html>""",
        height=220,
        scrolling=False,
    )

    st.markdown("<div style='height:.45rem'></div>", unsafe_allow_html=True)

    st.markdown("### Javaサンプル（抜粋）")
    st.code(
        """// java/market-fetcher/src/main/java/com/maru/MarketFetcher.java
import yahoofinance.Stock;
import yahoofinance.YahooFinance;

public class MarketFetcher {
  public static void main(String[] args) throws Exception {
    Stock nikkei = YahooFinance.get("^N225");
    System.out.println("Nikkei: " + nikkei.getQuote().getPrice());
  }
}
""",
        language="java",
    )

    st.markdown(
        "<div class='card muted'>Javaサンプルは「同梱してるだけ」で、Streamlit Cloud上でJavaを実行するわけではないよ。<br/>"
        "動き（アニメーション）はブラウザ側なので JavaScript が担当、ここは役割分担って覚えてね。</div>",
        unsafe_allow_html=True,
    )


# =========================
# Main
# =========================


def main() -> None:
    cfg = load_config()
    st.set_page_config(
        page_title=f"{cfg.name} | 日本株",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_css()

    snap = fetch_market_snapshot()
    render_tickerbar(snap)
    hero(cfg)

    tabs = st.tabs(
        [
            "ホーム",
            "自己紹介",
            "note",
            "ショップ",
            "SNS",
            "勉強会",
            "市場指数",
            "Tech",
        ]
    )

    with tabs[0]:
        page_home(cfg)
    with tabs[1]:
        page_intro(cfg)
    with tabs[2]:
        page_note(cfg)
    with tabs[3]:
        page_shop(cfg)
    with tabs[4]:
        page_social(cfg)
    with tabs[5]:
        page_study(cfg)
    with tabs[6]:
        page_market(cfg)
    with tabs[7]:
        page_tech(cfg)


if __name__ == "__main__":
    main()