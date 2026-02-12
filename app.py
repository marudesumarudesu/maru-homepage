"""maru_homepage Streamlit app

要件
 - 画面上に「URLを貼る/埋め込みコードを貼る」入力欄を出さない
 - ホームで全体像（プロフィール/最新note/Shopify/Instagram/Threads/勉強会/市場指数）が分かる
 - 日本株に特化していることが一目で伝わる
 - 後から更新しやすい：site_config.json を編集するだけで差し替え可能

デプロイ
 - Streamlit Community Cloud（GitHub連携）推奨
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

try:
    import requests  # type: ignore
except Exception:
    requests = None


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
    """Load site_config.json if present; fallback to DEFAULT_CONFIG."""
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
# Market data
# =========================


def _fetch_fred_series(series_id: str, api_key: str | None) -> float | None:
    if requests is None:
        return None
    params: dict[str, Any] = {
        "series_id": series_id,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    if api_key:
        params["api_key"] = api_key
    url = "https://api.stlouisfed.org/fred/series/observations"
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        obs = data.get("observations", [])
        if obs:
            return float(obs[0]["value"])
    except Exception:
        return None
    return None


def fetch_market_snapshot() -> dict[str, float | None]:
    """Try API -> fallback to static/market.json."""
    fred_key = os.getenv("FRED_API_KEY")
    nikkei = _fetch_fred_series("NIKKEI225", fred_key)
    jgb10y = _fetch_fred_series("IRLTLT01JPM156N", fred_key)

    # USDJPY: keep it optional (API key needed). fallback to static.
    usdjpy: float | None = None
    if requests is not None:
        av_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if av_key:
            try:
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": "USD",
                    "to_currency": "JPY",
                    "apikey": av_key,
                }
                resp = requests.get(url, params=params, timeout=10)
                data = resp.json()
                rate = data.get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate")
                if rate:
                    usdjpy = float(rate)
            except Exception:
                usdjpy = None

    # fallback
    if nikkei is None or usdjpy is None or jgb10y is None:
        try:
            p = Path(__file__).parent / "static" / "market.json"
            if p.exists():
                d = json.loads(p.read_text(encoding="utf-8"))
                nikkei = nikkei if nikkei is not None else float(d.get("nikkei"))
                usdjpy = usdjpy if usdjpy is not None else float(d.get("usdjpy"))
                jgb10y = jgb10y if jgb10y is not None else float(d.get("jgb_yield"))
        except Exception:
            pass

    return {"nikkei": nikkei, "usdjpy": usdjpy, "jgb10y": jgb10y}


# =========================
# Styling
# =========================


def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+JP:wght@400;600;700&display=swap');

:root {
  --bg1: #f6f2ff;
  --bg2: #eef6ff;
  --bg3: #ffffff;
  --card: rgba(255,255,255,0.78);
  --border: rgba(30,35,45,0.08);
  --text: #101524;
  --muted: rgba(16,21,36,0.62);
  --accent1: #6f6bff;
  --accent2: #2bd2ff;
  --shadow: 0 18px 50px rgba(16,21,36,0.10);
  --shadow2: 0 10px 30px rgba(16,21,36,0.08);
  --radius: 22px;
}

html, body, [class*="css"]  {
  font-family: 'Inter','Noto Sans JP', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

.stApp {
  background:
    radial-gradient(1200px 600px at 15% 10%, rgba(111,107,255,0.20) 0%, rgba(111,107,255,0.0) 60%),
    radial-gradient(1200px 600px at 85% 15%, rgba(43,210,255,0.18) 0%, rgba(43,210,255,0.0) 60%),
    linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 40%, var(--bg3) 100%);
  color: var(--text);
}

/* Hide Streamlit default chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
  padding-top: 1.2rem;
  padding-bottom: 4rem;
  max-width: 1200px;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: rgba(255,255,255,0.65);
  backdrop-filter: blur(12px);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stSelectbox label {
  color: var(--muted);
  font-weight: 600;
}

/* Sidebar selectbox look */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  border-radius: 16px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.78);
}
[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
  box-shadow: 0 0 0 4px rgba(111,107,255,0.18);
  border-color: rgba(111,107,255,0.35);
}

/* Hero */
.maru-hero {
  background: linear-gradient(135deg, rgba(111,107,255,0.14), rgba(43,210,255,0.10));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.6rem 1.6rem;
  margin-bottom: 1.2rem;
  position: relative;
  overflow: hidden;
}
.maru-hero:before {
  content: "";
  position: absolute;
  inset: -60px;
  background: radial-gradient(circle at 30% 30%, rgba(111,107,255,0.22), transparent 60%),
              radial-gradient(circle at 70% 20%, rgba(43,210,255,0.18), transparent 55%);
  filter: blur(8px);
}
.maru-hero > div { position: relative; }
.maru-badge {
  display: inline-flex;
  align-items: center;
  gap: .5rem;
  padding: .35rem .7rem;
  border-radius: 999px;
  background: rgba(16,21,36,0.06);
  border: 1px solid var(--border);
  color: var(--text);
  font-weight: 700;
  font-size: 0.85rem;
}
.maru-title {
  margin-top: .6rem;
  margin-bottom: .2rem;
  font-size: 2.2rem;
  letter-spacing: 0.02em;
}
.maru-sub {
  color: var(--muted);
  font-size: 1.05rem;
  margin-bottom: .9rem;
}
.maru-pills {
  display: flex;
  flex-wrap: wrap;
  gap: .6rem;
}
.maru-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: .55rem .9rem;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(111,107,255,0.85), rgba(43,210,255,0.85));
  color: white;
  text-decoration: none;
  font-weight: 700;
  font-size: .95rem;
  box-shadow: var(--shadow2);
}
.maru-pill.secondary {
  background: rgba(255,255,255,0.85);
  color: var(--text);
  border: 1px solid var(--border);
}

/* Cards */
.maru-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow2);
  padding: 1.2rem 1.2rem;
}
.maru-card h3 {
  margin: 0 0 .4rem 0;
  font-size: 1.1rem;
}
.maru-muted { color: var(--muted); }
.maru-kpi {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: .9rem;
}
.maru-kpi .k {
  background: rgba(255,255,255,0.75);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: .9rem .9rem;
}
.maru-kpi .k .lbl { color: var(--muted); font-weight: 700; font-size: .85rem; }
.maru-kpi .k .val { font-weight: 800; font-size: 1.25rem; margin-top: .25rem; }

/* Buttons inside markdown */
a.maru-link {
  color: var(--accent1);
  font-weight: 700;
  text-decoration: none;
}
a.maru-link:hover { text-decoration: underline; }

/* Better spacing for Streamlit elements */
div[data-testid="stVerticalBlock"] > div:has(> .maru-card) {
  margin-bottom: 1.1rem;
}

@media (max-width: 900px) {
  .maru-kpi { grid-template-columns: 1fr; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def hero(cfg: SiteConfig) -> None:
    st.markdown(
        f"""
<div class="maru-hero">
  <div>
    <div class="maru-badge">📈 {cfg.focus_badge}</div>
    <div class="maru-title">{cfg.name}</div>
    <div class="maru-sub">{cfg.tagline}</div>
    <div class="maru-pills">
      <a class="maru-pill" href="{cfg.instagram_url}" target="_blank" rel="noopener">Instagram</a>
      <a class="maru-pill" href="{cfg.threads_url}" target="_blank" rel="noopener">Threads</a>
      <a class="maru-pill secondary" href="#" onclick="window.scrollTo(0,0)">Home</a>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def fmt_num(x: float | None, suffix: str = "") -> str:
    if x is None:
        return "--"
    try:
        return f"{x:,.2f}{suffix}"
    except Exception:
        return "--"


# =========================
# Pages
# =========================


def page_home(cfg: SiteConfig) -> None:
    bio_html = cfg.bio.replace("\n", "<br/>")
    snap = fetch_market_snapshot()
    col1, col2 = st.columns([1.1, 1])
    with col1:
        st.markdown(
            f"""
<div class="maru-card">
  <h3>自己紹介</h3>
  <div class="maru-muted">{bio_html}</div>
  <div style="height:.8rem"></div>
  <div>
    <a class="maru-link" href="{cfg.instagram_url}" target="_blank" rel="noopener">▶ SNSを見る</a>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
<div class="maru-card">
  <h3>市場スナップショット</h3>
  <div class="maru-kpi">
    <div class="k"><div class="lbl">日経平均</div><div class="val">{fmt_num(snap['nikkei'])}</div></div>
    <div class="k"><div class="lbl">ドル円</div><div class="val">{fmt_num(snap['usdjpy'])}</div></div>
    <div class="k"><div class="lbl">日本10年債利回り</div><div class="val">{fmt_num(snap['jgb10y'], '%')}</div></div>
  </div>
  <div style="height:.6rem"></div>
  <div class="maru-muted" style="font-size:.9rem;">APIキー未設定の場合は同梱の market.json を表示します。</div>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Note previews
    st.markdown("### 最新note")
    if cfg.note_embeds:
        cols = st.columns(3)
        for i, emb in enumerate(cfg.note_embeds[:3]):
            with cols[i % 3]:
                st.markdown("<div class='maru-card'>", unsafe_allow_html=True)
                components.html(_wrap_embed(emb), height=460, scrolling=False)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='maru-card maru-muted'>note埋め込みが未設定です。site_config.json の embeds.note に追加してね。</div>",
            unsafe_allow_html=True,
        )

    st.write("")

    # Shop + Community + Study
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### ショップ")
        st.markdown("<div class='maru-card'>", unsafe_allow_html=True)
        if cfg.shopify_embed.strip():
            components.html(_wrap_embed(cfg.shopify_embed), height=720, scrolling=False)
        else:
            st.markdown(
                "<div class='maru-muted'>Shopify埋め込みが未設定です。site_config.json の embeds.shopify に貼り付けてね。</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("### コミュニティ")
        st.markdown(
            f"""
<div class="maru-card">
  <h3>Instagram</h3>
  <div class="maru-muted">最新の投稿・告知はこちら。</div>
  <div style="height:.6rem"></div>
  <a class="maru-pill" href="{cfg.instagram_url}" target="_blank" rel="noopener">{cfg.instagram_label}</a>
  <div style="height:1.0rem"></div>
  <h3>Threads</h3>
  <div class="maru-muted">日々の気づき・メモはThreadsへ。</div>
  <div style="height:.6rem"></div>
  <a class="maru-pill" href="{cfg.threads_url}" target="_blank" rel="noopener">{cfg.threads_label}</a>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 勉強会")
        st.markdown("<div class='maru-card'>", unsafe_allow_html=True)
        if cfg.study_form_embed.strip():
            components.html(_wrap_embed(cfg.study_form_embed), height=720, scrolling=True)
        elif cfg.study_form_fallback_url.strip():
            st.markdown(
                f"<div class='maru-muted'>フォームは外部ページで受付中です。</div><div style='height:.7rem'></div>"
                f"<a class='maru-pill' href='{cfg.study_form_fallback_url}' target='_blank' rel='noopener'>申し込みへ</a>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='maru-muted'>フォーム準備中。site_config.json にGoogleフォームのiframeを貼るだけで即反映されます。</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def page_intro(cfg: SiteConfig) -> None:
    st.markdown("## 自己紹介")
    bio_html = cfg.bio.replace("\n", "<br/>")
    st.markdown(
        f"""
<div class="maru-card">
  <h3>まるについて</h3>
  <div class="maru-muted">{bio_html}</div>
  <div style="height:1rem"></div>
  <div class="maru-muted" style="font-size:.95rem;">このサイトは日本株に特化した情報発信の拠点です。</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def page_note(cfg: SiteConfig) -> None:
    st.markdown("## note ブログ")
    if not cfg.note_embeds:
        st.markdown(
            "<div class='maru-card maru-muted'>note埋め込みが未設定です。site_config.json の embeds.note に iframe を追加してね。</div>",
            unsafe_allow_html=True,
        )
        return
    cols = st.columns(3)
    for i, emb in enumerate(cfg.note_embeds):
        with cols[i % 3]:
            st.markdown("<div class='maru-card'>", unsafe_allow_html=True)
            components.html(_wrap_embed(emb), height=460, scrolling=False)
            st.markdown("</div>", unsafe_allow_html=True)


def page_shop(cfg: SiteConfig) -> None:
    st.markdown("## オンラインショップ")
    st.markdown(
        "<div class='maru-card maru-muted'>ShopifyのBuy Buttonをそのまま表示しています。</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("<div class='maru-card'>", unsafe_allow_html=True)
    if cfg.shopify_embed.strip():
        components.html(_wrap_embed(cfg.shopify_embed), height=800, scrolling=False)
    else:
        st.markdown(
            "<div class='maru-muted'>未設定です。site_config.json の embeds.shopify に貼り付けてね。</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def page_instagram(cfg: SiteConfig) -> None:
    st.markdown("## Instagram")
    st.markdown(
        f"""
<div class="maru-card">
  <h3>Instagramで最新情報をチェック</h3>
  <div class="maru-muted">更新は @maru_update で発信中。</div>
  <div style="height:.8rem"></div>
  <a class="maru-pill" href="{cfg.instagram_url}" target="_blank" rel="noopener">{cfg.instagram_label}</a>
</div>
        """,
        unsafe_allow_html=True,
    )


def page_threads(cfg: SiteConfig) -> None:
    st.markdown("## Threads")
    st.markdown(
        f"""
<div class="maru-card">
  <h3>Threadsでラフに発信</h3>
  <div class="maru-muted">日々のメモや気づきはこちらに置いてます。</div>
  <div style="height:.8rem"></div>
  <a class="maru-pill" href="{cfg.threads_url}" target="_blank" rel="noopener">{cfg.threads_label}</a>
</div>
        """,
        unsafe_allow_html=True,
    )


def page_study(cfg: SiteConfig) -> None:
    st.markdown("## 勉強会")
    st.markdown(
        "<div class='maru-card maru-muted'>勉強会の申し込みフォームをここに表示します。Googleフォームのiframeを貼るだけでOK。</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("<div class='maru-card'>", unsafe_allow_html=True)
    if cfg.study_form_embed.strip():
        components.html(_wrap_embed(cfg.study_form_embed), height=800, scrolling=True)
    elif cfg.study_form_fallback_url.strip():
        st.markdown(
            f"<div class='maru-muted'>フォームは外部ページで受付中です。</div><div style='height:.7rem'></div>"
            f"<a class='maru-pill' href='{cfg.study_form_fallback_url}' target='_blank' rel='noopener'>申し込みへ</a>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='maru-muted'>フォーム準備中。site_config.json に iframe を貼るとここに表示されます。</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def page_market(cfg: SiteConfig) -> None:
    _ = cfg
    st.markdown("## 市場指数")
    snap = fetch_market_snapshot()
    st.markdown(
        f"""
<div class="maru-card">
  <h3>主要指数</h3>
  <div class="maru-kpi">
    <div class="k"><div class="lbl">日経平均</div><div class="val">{fmt_num(snap['nikkei'])}</div></div>
    <div class="k"><div class="lbl">ドル円</div><div class="val">{fmt_num(snap['usdjpy'])}</div></div>
    <div class="k"><div class="lbl">日本10年債利回り</div><div class="val">{fmt_num(snap['jgb10y'], '%')}</div></div>
  </div>
  <div style="height:.6rem"></div>
  <div class="maru-muted" style="font-size:.9rem;">更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _wrap_embed(embed_html: str) -> str:
    """Wrap embed HTML with minimal CSS so it fits nicely in Streamlit iframe."""
    return f"""<!doctype html>
<html lang='ja'>
<head>
  <meta charset='utf-8'/>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'/>
  <style>
    html, body {{ margin:0; padding:0; background:transparent; }}
    .wrap {{ width:100%; }}
    iframe {{ width:100% !important; max-width:100% !important; }}
  </style>
</head>
<body>
  <div class='wrap'>
    {embed_html}
  </div>
</body>
</html>"""


def main() -> None:
    cfg = load_config()
    st.set_page_config(page_title=f"{cfg.name} | 日本株", page_icon="📈", layout="wide")
    inject_css()
    hero(cfg)

    pages = [
        "ホーム",
        "自己紹介",
        "note ブログ",
        "オンラインショップ",
        "Instagram",
        "Threads",
        "勉強会",
        "市場指数",
    ]

    # Sidebar profile
    with st.sidebar:
        st.markdown(
            f"""
<div style="padding: .3rem .2rem 1rem .2rem;">
  <div style="font-weight:800; font-size:1.05rem;">{cfg.name}</div>
  <div style="color:rgba(16,21,36,0.62); font-weight:600; font-size:.9rem;">{cfg.focus_badge}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        choice = st.selectbox("メニュー", pages, index=0, label_visibility="collapsed")

    if choice == "ホーム":
        page_home(cfg)
    elif choice == "自己紹介":
        page_intro(cfg)
    elif choice == "note ブログ":
        page_note(cfg)
    elif choice == "オンラインショップ":
        page_shop(cfg)
    elif choice == "Instagram":
        page_instagram(cfg)
    elif choice == "Threads":
        page_threads(cfg)
    elif choice == "勉強会":
        page_study(cfg)
    elif choice == "市場指数":
        page_market(cfg)


if __name__ == "__main__":
    main()
