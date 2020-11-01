# coding: utf-8
import os
import re
import time
import errno
import platform
import requests
import configparser
from tqdm import tqdm
if platform.system() == "Windows":
  import winsound
else:
  import os
#----------------------------------------(data-date=NGの板用)----------------------------------------
#from dateutil.parser import parse
#---------------------------------------------------------------------------------------------------

#初期化
#設定読み込み
config_ini = configparser.ConfigParser()
config_ini_path = 'config.ini'
if not os.path.exists(config_ini_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)
config_ini.read(config_ini_path, encoding='utf-8')
domain = 'hebi'
bbs = 'news4vip'
time_interval = int(config_ini['DEFAULT']['time_interval'])
target = config_ini['DEFAULT']['target']
name = config_ini['DEFAULT']['name']
message = config_ini['DEFAULT']['message']
mail = str(time_interval) + "秒"
print(
f'time_interval:\t{str(time_interval)}\n'
f'target:\t\t{target}\n'
f'name:\t\t{name}\n'
f'message:\t{message}')

#正規表現
pattern_find_thread = '<a href=\"([0-9]{10})/l50\">.+?' + target + '.+?</a>'
pattern_check_archived = '<div class=\"stoplight stopred stopdone\">'
pattern_find_date_latest = 'data-date=\"([0-9]+)\"'
#----------------------------------------(data-date=NGの板用)----------------------------------------
#pattern_find_date_latest = '<span class=\"date\">(.+?)</span>'
#---------------------------------------------------------------------------------------------------

#定義
#通知音を鳴らす
def beep():
  if platform.system() == "Windows":
    winsound.Beep(500, 50)
  else:
    os.system('play -n synth %s sin %s' % (50/1000, 500))

#待機
def wait(sec):
  for _ in tqdm(range(sec)):
    time.sleep(1)
  beep() #通知音を鳴らす

#投稿
def post_message(domain, bbs, key):
  url_thread = 'https://' + domain + '.5ch.net/test/read.cgi/' + bbs + '/' + key + '/l0'
  time_now = str(int(time.time()))
  submit = "書き込む"
  oekaki_thread1 =""

  data = {"FROM":name.encode("cp932"),"mail":mail.encode("cp932"),"MESSAGE":message.encode("cp932"),"bbs":bbs,"key":key,"time":time_now,"submit":submit.encode("cp932"),"oekaki_thread1":oekaki_thread1}  #POSTデータをセット
	
  headers = { #headerをセット
	'referer': url_thread, 
	'accept-encoding': 'zip, deflate, br', 
	'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36', 
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 
	'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 
	'accept-language': 'ja,en-US;q=0.9,en;q=0.8', 
	'connection': 'keep-alive',
	}
	
  cookies = {'yuki':'akari','READJS':''}  #cookieをセット

  url_bbscgi = 'https://' + domain + '.5ch.net/test/bbs.cgi'
  r = requests.post(url_bbscgi,data=data,headers=headers,cookies=cookies)
  response = re.sub('<.*?>', '', str(r.text))
  print(response) #結果画面を表示
  beep() #通知音を鳴らす

#保守
def hosh(domain, bbs, key):
  url_thread = 'https://' + domain + '.5ch.net/test/read.cgi/' + bbs + '/' + key + '/l0'
  print(f'url_thread:\t{url_thread}')
  response = requests.get(url_thread) #スレを読み込む

  while not re.search(pattern_check_archived, response.text):  #dat落ちまで繰り返す
    print('THREAD NOT ARCHIEVED')
    time_wait = time_interval
    date_latest = int(re.findall(pattern_find_date_latest, response.text)[-1]) #最終書込時刻、現在時刻、差分を取得
    #----------------------------------------(data-date=NGの板用)----------------------------------------
    #date_latest_raw = re.findall(pattern_find_date_latest, response.text)[-1] 
    #date_latest = int(parse(date_latest_raw[:10]+date_latest_raw[13:]).timestamp())
    #---------------------------------------------------------------------------------------------------
    date_now = int(time.time()) + 60 * 60 * 9
    time_diff = date_now - date_latest
    print(
    f'date_latest:\t{str(date_latest)}\n'
    f'date_now:\t{str(date_now)}\n'
    f'time_diff:\t{str(time_diff)}sec')

    if time_diff >= time_interval: #最終書き込み時刻からの経過時間が閾値を超えたら書き込む
      print('POST')
      post_message(domain, bbs, key) #投稿

    else: #超過予想時刻まで待機
      print('NOT POST')
      time_wait = time_interval - time_diff
    print('WAIT')
    wait(time_wait) #待機
    response = requests.get(url_thread)
  print('THREAD ARCHIEVED')

#実行部
#スレ検索
while 1:
  response = requests.get('https://' + domain + '.5ch.net/' + bbs + '/subback.html') #スレ一覧を開く
  response.encoding = response.apparent_encoding 
  key = re.search(pattern_find_thread, response.text) #スレを検索
  if key: #スレが見つからなければ保守間隔分だけ待機
    print('THREAD FOUND')
    hosh(domain, bbs, key.groups()[0]) #保守
  else:
    print('THREAD NOT FOUND')
    print('WAIT')
    wait(time_interval) #待機
