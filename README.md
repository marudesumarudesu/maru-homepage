# まるのホームページ（日本株特化）

Streamlitで動く“おしゃれな個人サイト”テンプレです。左サイドバーは使わず、**上部タブ**でページ遷移します。

## できること

- **ホーム**で全体像が一目で分かる（自己紹介 / 指数 / 最新note / Shopify / Instagram / Threads / 勉強会）
- 画面上に**URL貼り付け入力欄は出さない**（埋め込みは設定ファイルで管理）
- 後から更新が簡単：`site_config.json` を編集するだけで反映
- 市場データは **yfinance** で取得（失敗時は `static/market.json` を表示）
- Java要素として、`java/market-fetcher/` に **Javaサンプル**を同梱

## ファイル構成

- `app.py`：Streamlitアプリ本体
- `site_config.json`：埋め込みコードやリンクの設定（ここだけ触ればOK）
- `requirements.txt`：デプロイ用
- `static/market.json`：取得失敗時のフォールバック表示（任意で更新）
- `java/market-fetcher/`：JavaでYahoo Financeを叩く最小サンプル（任意）

## ローカル実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## カスタマイズ（ここだけでOK）

`site_config.json` を編集します（UI上にURL入力欄はありません）。

### noteを増やす

`embeds.note` 配列に、noteの埋め込みiframe（+ script）を追加します。

### Shopifyを差し替える

`embeds.shopify` にShopify Buy Buttonの埋め込みコードを貼り替えます。

### 勉強会フォーム

どちらかでOK：

- **埋め込み表示**したい → `embeds.study_form` にGoogleフォームのiframeを貼る
- 外部ページに飛ばしたい → `links.study_form_url` にURLを入れる

## デプロイ（無料で簡単）

### Streamlit Community Cloud（おすすめ）

1. GitHubにこのフォルダをそのままPush
2. Streamlit Community Cloudで「New app」→ リポジトリ選択
3. Entry point を `app.py` にしてDeploy

### 静的サイトとして出したい場合

`static/` 配下のHTML/CSS版を、Netlify / Vercel / Cloudflare Pagesで公開できます。
（Shopifyやnoteの埋め込みは静的サイトと相性が良いです）
