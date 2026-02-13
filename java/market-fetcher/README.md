# market-fetcher (Java sample)

「Javaの要素が欲しい」という要望に対して、**YahooFinanceAPI** を使って
Yahoo Finance の価格を取得する最小サンプルを同梱しています。

- 本番サイト（Streamlit）は **Python + HTML/CSS** で動作
- このフォルダは **学習/デモ用のJavaサンプル**（デプロイ必須ではありません）

## 使い方

```bash
cd java/market-fetcher
mvn -q package
java -jar target/market-fetcher-0.1.0.jar
```

## 依存

- Maven
- Java 17+

依存ライブラリ:
- com.yahoofinance-api:YahooFinanceAPI:3.17.0
