# coding: utf-8
import os
import re
import time
import errno
import requests
import configparser
import chromedriver_binary
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

#保守
def hosh(url):
  while len(driver.find_elements_by_name('FROM')) != 0:  #dat落ちまで繰り返す
    print('THREAD NOT ARCHIEVED')
    time_wait = time_interval
    date_latest_raw = driver.find_elements_by_xpath('//div/div/span[@class="date"]')[-1].text
    date_latest = int(parse(date_latest_raw[:10]+date_latest_raw[13:]).timestamp())
    date_now = int(time.time())
    time_diff = date_now - date_latest
    print(
    'date_latest_raw:\t' + date_latest_raw +
    '\ndate_latest:\t' + str(date_latest) +
    '\ndate_now:\t' + str(date_now) +
    '\ntime_diff:\t' + str(time_diff) + 'sec')
    if time_interval < time_diff: #最終書き込み時刻からの経過時間が閾値を超えたら書き込む
      print('POST')
      driver.find_element_by_name('FROM').send_keys(name)
      driver.find_element_by_name('MESSAGE').send_keys(message)
      driver.find_element_by_name('mail').send_keys(str(time_interval) + '秒')
      driver.find_element_by_name("submit").click()
      try:  #Cookie切れ対応
        driver.find_element_by_xpath('//input[@value="上記全てを承諾して書き込む"]').click()
      except NoSuchElementException:
        pass 
    else:
      print('NOT POST')
      time_wait = time_interval - time_diff
    print('time_wait:\t' + str(time_wait) + 'sec')
    print('WAIT')
    time.sleep(time_wait) #超過予想時刻まで待機
    driver.get(url)  
  print('THREAD ARCHIEVED')

#設定読み込み
config_ini = configparser.ConfigParser()
config_ini_path = 'config.ini'
if not os.path.exists(config_ini_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)
config_ini.read(config_ini_path, encoding='utf-8')
thread_list = 'http://rosie.5ch.net/operatex/subback.html'  #スレ一覧URL
time_interval = int(config_ini['DEFAULT']['time_interval'])
target_title = config_ini['DEFAULT']['target_title']
name = config_ini['DEFAULT']['name']
message = config_ini['DEFAULT']['message']
print(
'time_interval:\t' + str(time_interval) +
'\ntarget_title:\t' + target_title +
'\nname:\t\t' + name +
'\nmessage:\t' + message)
options = Options() #chromedriver_binary及びchromeバージョン87以上のみで使えるコマンド
options.add_argument('--headless')
options.add_argument('--incognito')

#実行部
while 1:
  response = requests.get(thread_list) #スレ一覧を開く
  response.encoding = response.apparent_encoding 
  thread_number = re.findall('<a href=\"([0-9]{10}/l50)\">.+?'+target_title+'.+?</a>', response.text) #スレを検索
  if not thread_number: #スレが見つからなければ保守間隔分だけ待機
    print('THREAD NOT FOUND')
    print('WAIT')
    time.sleep(time_interval) #待機
  else:
    print('THREAD FOUND')
    url = 'https://hebi.5ch.net/test/read.cgi/news4vip/' + thread_number[0].replace('l50', 'l0')
    print('url:\t\t'+url)
    driver = webdriver.Chrome() #Chrome起動
    driver.implicitly_wait(10)
    driver.get(url)  #スレを開く
    hosh(url) #保守
    driver.quit()