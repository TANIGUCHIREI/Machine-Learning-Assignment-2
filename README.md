# Machine-Learning-Assignment-2

## Studies on International Integrated Sciences Wed2Thu2 Assignment 2.

What factors affect the number of views on YouTube?

## Scraper.ipynbの仕様
ほぼDataCollector.py, Utils.py と一緒
### 変更点
- 最初にライブラリのインストール
- YOUTUBE_API_KEY は Colab の Secret 変数で実装
- ```item['statistics']['dislikeCount']```がエラーを吐いたので、if文分岐に変更
