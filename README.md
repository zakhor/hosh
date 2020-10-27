# hosh
## すること
5chの特定の掲示板においてスレッドタイトルに任意の文字列を含むスレを検索し保守する
## 設定できるもの（config.ini）
* 名前欄
* 本文欄
* 保守間隔時間（秒）
* 検索するスレッドタイトル
## 必要なもの
* Python 3.9
* GoogleChrome 87.0.4280.27 beta (通常版やChrome Canaryだとヘッドレスモード・プライベートモードにできない)
* chromedriver-binary 87.0.4280.20.0  
  
`python setup.py install`でまとめてインストールできる
## news4vip版、operatex版、liveanarachy版の違い
#### news4vip版
ソースからUNIX時間を取得
#### operatex版
書き込み時刻を解釈して取得
#### liveanarchy版
名前欄、メール欄の設定を削除しマルチポスト避けを本文に追加
