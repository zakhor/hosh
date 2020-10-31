# hosh
## すること
5chにおいてスレタイに任意の文字列を含むスレを検索し保守する
## キャプチャ
![image](https://user-images.githubusercontent.com/49256667/97784682-9ec26c00-1be3-11eb-97fa-aa248248933b.png)
## 設定できるもの（config.ini）
* スレタイ検索ワード
* 保守間隔時間（秒）
* 名前
* 本文
## 必要なもの
* Python 3.9    
* 各種モジュール（requirement.txtに記載）    
`python setup.py install`でまとめてインストールできる
## news4vip版とoperatex版の違い
#### news4vip版
data-dateから書込時刻を取得
#### operatex版
レスを解釈して書込時刻を取得
