import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

#保守
def hosh(url):
  while len(driver.find_elements_by_name('FROM')) > 0:  #dat落ちまで繰り返す
    print('THREAD NOT ARCHIEVED')
    time_wait = time_interval
    date_last = int(re.findall('data-date=\"([0-9]+)\"', driver.page_source)[-1]) #最終書き込み時刻を取得
    date_now = int(time.time()) + 3600 * 9
    time_diff = date_now - date_last
    print('date_last:\t' + str(date_last))
    print('date_now:\t' + str(date_now))
    print('time_diff:\t' + str(time_diff) + 'sec')
    if time_interval < time_diff: #最終書き込み時刻からの経過時間が閾値を超えたら書き込む
      print('POST')
      driver.find_element_by_name('FROM').send_keys(name)
      driver.find_element_by_name('mail').send_keys(str(time_interval)+'秒')
      driver.find_element_by_name('MESSAGE').send_keys(message)
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
    time.sleep(time_wait)
    driver.get(url)  
  print('THREAD ARCHIEVED')

#設定
thread_list = 'https://hebi.5ch.net/news4vip/subback.html'  #スレ一覧URL
time_interval = 3480 #保守間隔（秒）
target_title = 'テスト' #検索スレタイ
name = ''  #書き込み時名前
message = '保守'  #書き込み時本文
print('time_interval:\t' + str(time_interval))
print('target_title:\t' + target_title)
print('name:\t\t' + name)
print('message:\t' + message) 

#Chrome起動
driver = webdriver.Chrome()
driver.implicitly_wait(10)

#実行部
while 1:
  driver.switch_to.window(driver.window_handles[0]) #タブの切り替え
  driver.get(thread_list) #スレ一覧を開く
  if len(driver.find_elements_by_partial_link_text(target_title)) > 0:  #スレを検索
    print('THREAD FOUND')
    driver.find_element_by_partial_link_text(target_title).click()  #スレを開く
    driver.switch_to.window(driver.window_handles[1]) #タブ切り替え
    url = driver.current_url  #スレURLを取得
    print('url:\t\t'+url)
    hosh(url) #保守
  else: #スレが見つからなければ保守間隔分だけ待機
    print('THREAD NOT FOUND')
    print('WAIT')
    time.sleep(time_interval) #待機
