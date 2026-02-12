"""
Streamlit app for personal homepage (まるさん)

This Streamlit application showcases a personal homepage that reflects the
personality of its owner without mentioning YDK.  It demonstrates how
various third‑party services such as note, Shopify, Instagram, Threads and
a study‑session sign‑up form can be embedded seamlessly into one site while
also displaying up‑to‑date financial indices like the Nikkei 225, the
USD/JPY exchange rate and Japan's 10‑year government bond yield.  The
application uses Python to fetch market data and HTML iframes to embed
external content.  Feel free to customize the sections, colours and
layout to better match your brand.
"""

import json
import os
from datetime import datetime
from textwrap import dedent

import streamlit as st

try:
    import requests
except ImportError:
    # requests may not be available in the runtime; the user will need to
    # install it when deploying.  We catch ImportError so the file still
    # loads in environments where requests is absent.
    requests = None


def fetch_nikkei225(api_key: str | None = None) -> float | None:
    """
    Fetch the latest Nikkei 225 closing price from FRED.  This function
    requires a FRED API key if you exceed the anonymous request limit.  See
    https://fredhelp.stlouisfed.org for details on obtaining a free key.

    Parameters
    ----------
    api_key: str | None
        Your FRED API key.  If None, the function will attempt to call
        the endpoint without a key (useful for testing).

    Returns
    -------
    float | None
        The latest closing value of the Nikkei 225 index, or None if
        retrieval fails.
    """
    if requests is None:
        return None
    params = {
        "series_id": "NIKKEI225",
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    if api_key:
        params["api_key"] = api_key
    url = "https://api.stlouisfed.org/fred/series/observations"
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        obs = data.get("observations", [])
        if obs:
            return float(obs[0]["value"])
    except Exception:
        return None
    return None


def fetch_usd_jpy() -> float | None:
    """
    Fetch the current USD/JPY exchange rate using Alpha Vantage's
    free currency API.  You need to set the environment variable
    ALPHAVANTAGE_API_KEY with your API key.  You can obtain one for free
    from https://www.alphavantage.co/support/#api-key.  Alpha Vantage
    imposes rate limits on the free tier.

    Returns
    -------
    float | None
        The exchange rate, or None if unavailable.
    """
    if requests is None:
        return None
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        return None
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": "USD",
        "to_currency": "JPY",
        "apikey": api_key,
    }
    url = "https://www.alphavantage.co/query"
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        rate = data.get("Realtime Currency Exchange Rate", {}).get(
            "5. Exchange Rate"
        )
        if rate:
            return float(rate)
    except Exception:
        return None
    return None


def fetch_jgb_yield(api_key: str | None = None) -> float | None:
    """
    Fetch the most recent Japan 10‑year government bond yield from FRED.
    You may need an API key depending on the call volume.  See
    https://fredhelp.stlouisfed.org for details.

    Returns
    -------
    float | None
        The most recent yield (percentage), or None if retrieval fails.
    """
    if requests is None:
        return None
    params = {
        "series_id": "IRLTLT01JPM156N",
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    if api_key:
        params["api_key"] = api_key
    url = "https://api.stlouisfed.org/fred/series/observations"
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        obs = data.get("observations", [])
        if obs:
            return float(obs[0]["value"])
    except Exception:
        return None
    return None


def get_market_data() -> dict[str, float | None]:
    """
    Gather the latest market data.  Wraps each fetcher so that
    the page doesn't break if one value fails.  You can pass API keys
    via environment variables: FRED_API_KEY and ALPHAVANTAGE_API_KEY.
    """
    fred_key = os.getenv("FRED_API_KEY")
    return {
        "Nikkei 225": fetch_nikkei225(api_key=fred_key),
        "USD/JPY": fetch_usd_jpy(),
        "Japan 10Y Yield (%)": fetch_jgb_yield(api_key=fred_key),
    }


def show_market_section():
    """Render the market indices section."""
    st.markdown("## 市場指数 (Market Indices)")
    st.write("主要な日本の経済指数をリアルタイムで表示します。APIキーを設定すると最新データが取得できます。設定がない場合はNoneが表示されます。")
    data = get_market_data()
    for label, value in data.items():
        st.metric(label=label, value=value)


def show_intro_section():
    """Render the self‑introduction section."""
    st.markdown("## 自己紹介")
    st.write(
        dedent(
            """
            こんにちは、まるです！🧑‍💻  
            名古屋を拠点に活動する投資家・クリエイター。日本株を中心に、
            テクノロジーと金融の融合に魅力を感じながら日々学びを深めています。
            このサイトでは、ブログ記事や勉強会のご案内、
            おすすめ商品の紹介などを通じて皆さまと交流していきます。どうぞゆっくりご覧ください。
            """
        )
    )
    # Optionally include a hero image.  The image file should be placed in the
    # "images" directory.  Uncomment the following lines and replace
    # "hero.jpg" with your own file name.
    # from PIL import Image
    # image = Image.open("images/hero.jpg")
    # st.image(image, use_column_width=True)


def show_blog_section():
    """Render the blog (note) section."""
    st.markdown("## note ブログ")
    st.write(
        "noteで執筆した記事の一覧または特定の記事をこのページに埋め込みます。"
    )
    st.write(
        "以下に最新のnote記事を埋め込み表示しています。投稿内容は手動で更新できます。"
    )
    # まるさんのnote記事3件を直接埋め込み
    note_iframes = [
        "https://note.com/embed/notes/n33a01c8bc70c",
        "https://note.com/embed/notes/neda9e548c3e1",
        "https://note.com/embed/notes/nc3fa3211de10",
    ]
    cols = st.columns(len(note_iframes))
    for idx, url in enumerate(note_iframes):
        with cols[idx]:
            st.components.v1.iframe(url, height=400)
    # note embed script (the script is loaded automatically in the iframe)


def show_shopify_section():
    """Render the Shopify products section using Buy Buttons."""
    st.markdown("## オンラインショップ")
    st.write(
        "ShopifyのBuy Buttonを利用して商品をサイト内で販売しています。下記に既定の商品ボタンを表示します。"
    )
    # Shopify Buy Button embed code is hard-coded for the featured product
    shopify_html = """
    <div id='product-component-1770925614378'></div>
    <script type="text/javascript">
    (function () {
      var scriptURL = 'https://sdks.shopifycdn.com/buy-button/latest/buy-button-storefront.min.js';
      if (window.ShopifyBuy) {
        if (window.ShopifyBuy.UI) {
          ShopifyBuyInit();
        } else {
          loadScript();
        }
      } else {
        loadScript();
      }
      function loadScript() {
        var script = document.createElement('script');
        script.async = true;
        script.src = scriptURL;
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(script);
        script.onload = ShopifyBuyInit;
      }
      function ShopifyBuyInit() {
        var client = ShopifyBuy.buildClient({
          domain: '0shhwt-xp.myshopify.com',
          storefrontAccessToken: 'ae970d43dcae5a352d8bb24eda78403a',
        });
        ShopifyBuy.UI.onReady(client).then(function (ui) {
          ui.createComponent('product', {
            id: '15291114389664',
            node: document.getElementById('product-component-1770925614378'),
            moneyFormat: '%C2%A5%7B%7Bamount_no_decimals%7D%7D',
            options: {
          "product": {
            "styles": {
              "product": {
                "@media (min-width: 601px)": {
                  "max-width": "calc(25% - 20px)",
                  "margin-left": "20px",
                  "margin-bottom": "50px"
                }
              }
            },
            "text": {
              "button": "Add to cart"
            }
          },
          "productSet": {
            "styles": {
              "products": {
                "@media (min-width: 601px)": {
                  "margin-left": "-20px"
                }
              }
            }
          },
          "modalProduct": {
            "contents": {
              "img": false,
              "imgWithCarousel": true,
              "button": false,
              "buttonWithQuantity": true
            },
            "styles": {
              "product": {
                "@media (min-width: 601px)": {
                  "max-width": "100%",
                  "margin-left": "0px",
                  "margin-bottom": "0px"
                }
              }
            },
            "text": {
              "button": "Add to cart"
            }
          },
          "option": {},
          "cart": {
            "text": {
              "total": "Subtotal",
              "button": "Checkout"
            }
          },
          "toggle": {}
        },
          });
        });
      }
    })();
    </script>
    """
    st.components.v1.html(shopify_html, height=600)


def show_instagram_section():
    """Render the Instagram feed section."""
    st.markdown("## Instagram")
    st.write(
        "Instagramの最新投稿はInstagramのプロフィールページからご覧いただけます。以下のリンクをクリックしてください。"
    )
    instagram_link = "https://www.instagram.com/maru_update/"
    st.markdown(f"[Instagram @maru_update]({instagram_link})")


def show_threads_section():
    """Render the Threads feed section."""
    st.markdown("## Threads")
    st.write(
        "Threadsの最新投稿はThreadsのプロフィールページからご覧いただけます。以下のリンクをクリックしてください。"
    )
    threads_link = "https://www.threads.net/@maru_update"
    st.markdown(f"[Threads @maru_update]({threads_link})")


def show_signup_section():
    """Render the study session sign‑up form section."""
    st.markdown("## 勉強会申し込みフォーム")
    st.write(
        "ここでは勉強会の参加申込を受け付けます。フォームに入力されたデータはローカルファイルに保存されます。"
    )
    with st.form("study_form"):
        name = st.text_input("お名前")
        email = st.text_input("メールアドレス")
        message = st.text_area("参加目的・メッセージ")
        submitted = st.form_submit_button("送信")
        if submitted:
            record = {
                "name": name,
                "email": email,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
            # Append submission to local JSON file for demonstration.  In a real
            # deployment you should handle data storage securely (e.g., send to
            # Google Sheets or a database) and comply with privacy laws.
            file_path = "signup_data.json"
            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = []
                data.append(record)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                st.success("申し込みを受け付けました。ありがとうございます！")
            except Exception as e:
                st.error(f"データの保存に失敗しました: {e}")


def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="まるのホームページ", layout="wide")
    st.markdown(
        """
        <style>
        /* Custom CSS to give the site a stylish look */
        body {
            background-color: #f7f8fa;
            color: #333;
            font-family: 'Yu Gothic', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    menu = [
        "自己紹介",
        "note ブログ",
        "オンラインショップ",
        "Instagram",
        "Threads",
        "勉強会",
        "市場指数",
    ]
    choice = st.sidebar.selectbox("メニュー", menu)
    if choice == "自己紹介":
        show_intro_section()
    elif choice == "note ブログ":
        show_blog_section()
    elif choice == "オンラインショップ":
        show_shopify_section()
    elif choice == "Instagram":
        show_instagram_section()
    elif choice == "Threads":
        show_threads_section()
    elif choice == "勉強会":
        show_signup_section()
    elif choice == "市場指数":
        show_market_section()


if __name__ == "__main__":
    main()