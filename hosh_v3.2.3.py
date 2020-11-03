# coding: utf-8
import os
import re
import time
import tqdm
import errno
import platform
import requests
import threading
import configparser
if platform.system() == "Windows":
  import winsound
else:
  import os
#----------------------------------------(data-date=NGの板用)----------------------------------------
#from dateutil.parser import parse
#---------------------------------------------------------------------------------------------------

#Configクラス作成
class Config():
  def __init__(self):
    self.time_interval = 0
    self.target = ''
    self.key = ''
    self.url_thread = ''

#初期化部
domain = 'hebi' #板設定
bbs = 'news4vip'

lock = threading.Lock() #ロック

pattern_check_archived = '<div class=\"stoplight stopred stopdone\">' #正規表現
pattern_find_date_latest = 'data-date=\"([0-9]+)\"'
#----------------------------------------(data-date=NGの板用)----------------------------------------
#pattern_find_date_latest = '<span class=\"date\">(.+?)</span>'
#---------------------------------------------------------------------------------------------------

#定義部
#printをロックする
def print_lock(str, lock):
  with lock:
    print(str)

#通知音を鳴らす
def beep():
  if platform.system() == "Windows":
    winsound.Beep(2500, 50)
  else:
    os.system('play -n synth %s sin %s' % (50/1000, 500))

#待機
def wait(sec):
  for _ in tqdm.tqdm(range(sec)):
    time.sleep(1)
  beep() #通知音を鳴らす

#投稿
def post_message(config):
  time_now = str(int(time.time()))
  name = ''
  message = '保守'
  mail = str(config.time_interval) + '秒'
  submit = "書き込む"
  oekaki_thread1 =""
  data = {"FROM":name.encode("cp932"),"mail":mail.encode("cp932"),"MESSAGE":message.encode("cp932"),"bbs":bbs,"key":config.key,"time":time_now,"submit":submit.encode("cp932"),"oekaki_thread1":oekaki_thread1}  #POSTデータをセット
  
  headers = { #headerをセット
    'authority': domain + '.5ch.net',
    'method': 'POST',
    'path': '/test/bbs.cgi',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
    'cache-control': 'max-age=0',
    'connection': 'keep-alive',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://' + domain + '.5ch.net',
    'referer': config.url_thread,
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'
  }
  
  cookies = {'yuki':'akari', 'READJS':''}  #cookieをセット
  url_bbscgi = 'https://' + domain + '.5ch.net/test/bbs.cgi'
  r = requests.post(url_bbscgi,data=data,headers=headers,cookies=cookies)
  response = re.sub('<.*?>', '', str(r.text))
  print_lock(response, lock) #結果画面を表示
  beep() #通知音を鳴らす

#保守
def hosh(config):
  response = requests.get(config.url_thread) #スレを読み込む
  time_interval = int(config.time_interval)
  while not re.search(pattern_check_archived, response.text):  #dat落ちまで繰り返す
    time_wait = time_interval
    date_latest = int(re.findall(pattern_find_date_latest, response.text)[-1]) #最終書込時刻、現在時刻、差分を取得
    #----------------------------------------(data-date=NGの板用)----------------------------------------
    #date_latest_raw = re.findall(pattern_find_date_latest, response.text)[-1] 
    #date_latest = int(parse(date_latest_raw[:10]+date_latest_raw[13:]).timestamp())
    #---------------------------------------------------------------------------------------------------
    date_now = int(time.time()) + 60 * 60 * 9
    time_diff = date_now - date_latest
    print_lock(f'url_thread:\t{config.url_thread}\n'
    'THREAD NOT ARCHIEVED\n'
    f'date_latest:\t{str(date_latest)}\n'
    f'date_now:\t{str(date_now)}\n'
    f'time_diff:\t{str(time_diff)}sec', lock)
    if time_diff >= config.time_interval: #最終書き込み時刻からの経過時間が閾値を超えたら書き込む
      print_lock('POST\n'
      'WAIT\n', lock)
      post_message(config) #投稿
    else: #超過予想時刻まで待機
      time_wait = config.time_interval - time_diff
      print_lock('NOT POST\n'
      'WAIT\n', lock) 
    wait(time_wait) #待機
    response = requests.get(config.url_thread)
  print_lock('THREAD ARCHIEVED\n', lock)

#スレ検索
def search_thread(section, config):
  while 1:
    response = requests.get('https://' + domain + '.5ch.net/' + bbs + '/subback.html') #スレ一覧を開く
    response.encoding = 'Shift_JIS'
    pattern_find_thread = '<a href=\"([0-9]{10})/l50\">.+?' + config.target + '.+?</a>'
    key = re.search(pattern_find_thread, response.text) #スレを検索
    if key: #スレが見つかったら保守
      config.key = key.groups()[0]
      config.url_thread = 'https://' + domain + '.5ch.net/test/read.cgi/' + bbs + '/' + config.key + '/'
      print_lock('THREAD FOUND\n'
      f'target:\t\t{config.target}\n'
      f'url_thread:\t{config.url_thread}\n', lock) 
      hosh(config) #保守
    else: #スレが見つからなければ保守間隔分待機
      print_lock('THREAD NOT FOUND\n'
      f'target:\t\t{config.target}\n'
      'WAIT\n', lock)
      wait(config.time_interval) #待機

#実行部
if __name__ == '__main__':
  config_ini = configparser.ConfigParser()  #config.ini読み込み
  config_ini_path = './config.ini'
  if not os.path.exists(config_ini_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)
  config_ini.read(config_ini_path, encoding='utf-8')

  for section in config_ini: #並列処理化
    config = Config()
    config.time_interval = 60
    config.target = config_ini[section]['target']
    print_lock(
    f'section:\t{section}\n'
    f'target:\t\t{config.target}\n', lock)
    threading.Thread(target=search_thread, args=(section, config)).start()