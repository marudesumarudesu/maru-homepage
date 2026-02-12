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


def show_home_section():
    """Render a home page that provides an overview of all sections."""
    st.markdown("## ホーム")
    st.write(
        "まるの世界へようこそ！ここでは日本株やクリエイティブに関する活動をまとめています。"
    )
    # Create a grid layout using Streamlit columns
    # First row: Intro, Blog, Shop
    cols1 = st.columns(3)
    with cols1[0]:
        st.subheader("自己紹介")
        st.write(
            "投資家・クリエイターとして活動するまるのプロフィールを簡潔にご紹介します。左のメニューから詳細をご覧ください。"
        )
    with cols1[1]:
        st.subheader("ブログ")
        st.write("noteで公開している最新の記事をお届けします。")
        # Show first note article as a preview
        st.components.v1.iframe(
            "https://note.com/embed/notes/n33a01c8bc70c", height=300
        )
    with cols1[2]:
        st.subheader("ショップ")
        st.write("まる厳選の商品を販売中です。")
        # Embed Shopify product but at a smaller height
        shop_html = """
        <div id='product-component-home'></div>
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
                node: document.getElementById('product-component-home'),
                moneyFormat: '%C2%A5%7B%7Bamount_no_decimals%7D%7D',
                options: {
                "product": {
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
                    "button": "カートに入れる"
                  }
                },
                "option": {},
                "cart": {
                  "text": {
                    "total": "小計",
                    "button": "購入手続き"
                  }
                },
                "toggle": {}
              });
            });
          }
        })();
        </script>
        """
        st.components.v1.html(shop_html, height=300)
    # Second row: SNS, Market, Events
    cols2 = st.columns(3)
    with cols2[0]:
        st.subheader("コミュニティ")
        st.write("InstagramとThreadsで最新情報を発信しています。")
        instagram_svg = (
            """
            <a href='https://www.instagram.com/maru_update/' target='_blank' style='text-decoration:none;'>
            <svg width='24' height='24' viewBox='0 0 448 512' fill='#6a4c93' xmlns='http://www.w3.org/2000/svg'>
            <path d='M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z'/>
            </svg>
            </a>
            &nbsp;
            <a href='https://www.threads.net/@maru_update' target='_blank' style='text-decoration:none;'>
            <svg width='24' height='24' viewBox='0 0 448 512' fill='#6a4c93' xmlns='http://www.w3.org/2000/svg'>
            <path d='M331.5 235.7c2.2 .9 4.2 1.9 6.3 2.8c29.2 14.1 50.6 35.2 61.8 61.4c15.7 36.5 17.2 95.8-30.3 143.2c-36.2 36.2-80.3 52.5-142.6 53h-.3c-70.2-.5-124.1-24.1-160.4-70.2c-32.3-41-48.9-98.1-49.5-169.6V256v-.2C17 184.3 33.6 127.2 65.9 86.2C102.2 40.1 156.2 16.5 226.4 16h.3c70.3 .5 124.9 24 162.3 69.9c18.4 22.7 32 50 40.6 81.7l-40.4 10.8c-7.1-25.8-17.8-47.8-32.2-65.4c-29.2-35.8-73-54.2-130.5-54.6c-57 .5-100.1 18.8-128.2 54.4C72.1 146.1 58.5 194.3 58 256c.5 61.7 14.1 109.9 40.3 143.3c28 35.6 71.2 53.9 128.2 54.4c51.4-.4 85.4-12.6 113.7-40.9c32.3-32.2 31.7-71.8 21.4-95.9c-6.1-14.2-17.1-26-31.9-34.9c-3.7 26.9-11.8 48.3-24.7 64.8c-17.1 21.8-41.4 33.6-72.7 35.3c-23.6 1.3-46.3-4.4-63.9-16c-20.8-13.8-33-34.8-34.3-59.3c-2.5-48.3 35.7-83 95.2-86.4c21.1-1.2 40.9-.3 59.2 2.8c-2.4-14.8-7.3-26.6-14.6-35.2c-10-11.7-25.6-17.7-46.2-17.8H227c-16.6 0-39 4.6-53.3 26.3l-34.4-23.6c19.2-29.1 50.3-45.1 87.8-45.1h.8c62.6 .4 99.9 39.5 103.7 107.7l-.2 .2zm-156 68.8c1.3 25.1 28.4 36.8 54.6 35.3c25.6-1.4 54.6-11.4 59.5-73.2c-13.2-2.9-27.8-4.4-43.4-4.4c-4.8 0-9.6 .1-14.4 .4c-42.9 2.4-57.2 23.2-56.2 41.8l-.1 .1z'/>
            </svg>
            </a>
            """
        )
        st.markdown(instagram_svg, unsafe_allow_html=True)
    with cols2[1]:
        st.subheader("市場指数")
        data = get_market_data()
        for label, value in data.items():
            st.metric(label, value)
    with cols2[2]:
        st.subheader("勉強会・イベント")
        st.write("勉強会の開催予定と申し込みフォームを準備中です。左のメニューから詳細をご確認ください。")


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
        "ホーム",
        "自己紹介",
        "note ブログ",
        "オンラインショップ",
        "Instagram",
        "Threads",
        "勉強会",
        "市場指数",
    ]
    choice = st.sidebar.selectbox("メニュー", menu)
    if choice == "ホーム":
        show_home_section()
    elif choice == "自己紹介":
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