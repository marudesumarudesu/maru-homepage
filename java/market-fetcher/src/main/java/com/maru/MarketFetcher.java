package com.maru;

import java.math.BigDecimal;

import yahoofinance.Stock;
import yahoofinance.YahooFinance;

/**
 * Javaの要素（参考実装）
 *
 * 実行例:
 *   cd java/market-fetcher
 *   mvn -q package
 *   java -jar target/market-fetcher-0.1.0.jar
 */
public class MarketFetcher {

  private static void printQuote(String label, String ticker) throws Exception {
    Stock s = YahooFinance.get(ticker);
    if (s == null || s.getQuote() == null) {
      System.out.println(label + " (" + ticker + "): --");
      return;
    }
    BigDecimal price = s.getQuote().getPrice();
    System.out.println(label + " (" + ticker + "): " + (price == null ? "--" : price.toPlainString()));
  }

  public static void main(String[] args) throws Exception {
    System.out.println("=== market-fetcher (Java sample) ===");
    printQuote("Nikkei 225", "^N225");
    printQuote("USDJPY", "JPY=X");
    // 日本10年債はYahoo側で取得できないことがあるため、先物を参考表示
    printQuote("JGB Future (ref)", "^JGBL");
  }
}
