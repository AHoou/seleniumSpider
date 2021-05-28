import json
import math
import os
import random
import re
import time
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

chromeOptions = webdriver.ChromeOptions()


def login(smsurl, itemDict):
    """先定义一个正常登录的方法，获取登录前和登录后的cookie"""
    # chromeOptions.add_argument("--proxy-server=http://10.112.136.174:9100")
    # driver = webdriver.Chrome(chrome_options=chromeOptions, executable_path='DIRVER\chromedriver.exe')
    driver = webdriver.Chrome(executable_path='DIRVER\chromedriver.exe')
    driver.maximize_window()
    driver.get(smsurl)
    time.sleep(2)
    # 排除其他弹出窗干扰
    try:
        other = driver.find_element_by_xpath('//*[@id="body"]/div[2]/div/div[2]')
        if other.is_enabled():
            other.click()
    except Exception as notfountde:
        pass
    # 登录
    driver.find_element_by_xpath('//*[@id="kioc8i8g_login"]/a[1]').click()
    driver.find_element_by_xpath('//*[@id="kln22343_wechat"]').click()
    driver.implicitly_wait(3)
    driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[1]/td/div/input').send_keys("15122887395")
    driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[2]/td/div/input').send_keys("aaaa1111")
    driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[4]/td/button').click()
    driver.implicitly_wait(3)
    time.sleep(2)

    for id, name in itemDict.items():
        try:
            print('共2532个药品，正在爬取第' + str(id) + "个药品名")
            # 输入以及点击事件
            # #方式1，在下拉候选框中搜索——>无法刷新页面值
            # driver.find_element_by_xpath('//*[@id="kiy4jaeu_toggle"]').click()  # 点击下拉按钮步骤1
            # driver.find_element_by_id('kiy4jaeu_toggle').click()  # 点击下拉按钮步骤2
            # driver.implicitly_wait(2)
            # driver.find_element_by_xpath('//*[@id="kiy6v4ja_bottom"]/table/tr[1]/td[2]/div/div/div/input').clear()  # 清空名称输入框
            # driver.find_element_by_xpath('//*[@id="kiy6v4ja_bottom"]/table/tr[1]/td[2]/div/div/div/input').send_keys(info[0])
            # driver.implicitly_wait(2)
            # driver.find_element_by_xpath('//*[@id="kiy6v4ja_bottom"]/table/tr[2]/td[2]/div/div/div/input').clear()  # 清空企业名称输入框
            # driver.find_element_by_xpath('//*[@id="kiy6v4ja_bottom"]/table/tr[2]/td[2]/div/div/div/input').send_keys(info[-1])
            # driver.implicitly_wait(2)

            # # 方式2 直接在搜索框搜索
            driver.find_element_by_xpath('//*[@id="kiy4cx57_autobox"]/div/div/input').clear()  # 清空名称输入框
            driver.find_element_by_xpath('//*[@id="kiy4cx57_autobox"]/div/div/input').send_keys(name)
            driver.implicitly_wait(2)
            driver.find_element_by_xpath('//*[@id="kiy4uhi3_btn"]/button').click()
            driver.implicitly_wait(random.randint(5, 8))
            # 获取第一页源代码
            html_source = driver.page_source
            # 解析条目数和页数
            html = etree.HTML(html_source, etree.HTMLParser())
            itemsNumberString = html.xpath('//*[@id="kmq44q29_box"]/div[4]/div[1]/span/text()')
            itemsNumber = int(re.findall(r"\d+\.?\d*", itemsNumberString[0])[0])
            pageNumber = math.ceil(itemsNumber / 20)
            if itemsNumber > 0:
                # 保存第一页详情
                rows = driver.find_elements_by_xpath('//*[@id="kmq44q29_box"]/div[3]/div/div[3]/table/tbody//div//div/a')
                saveDetails(driver, id, str(0 + 1), rows)
            if pageNumber > 0:
                # 翻页
                for pageN in range(pageNumber):
                    nextPage = driver.find_element_by_xpath('//*[@id="kmq44q29_box"]/div[4]/div[2]/div/button[2]/i')
                    if EC.element_to_be_clickable(nextPage):
                        nextPage.click()
                        driver.implicitly_wait(random.randint(5, 8))
                        time.sleep(2)
                        rows = driver.find_elements_by_xpath('//*[@id="kmq44q29_box"]/div[3]/div/div[3]/table/tbody//div//div/a')
                        saveDetails(driver, id, str(pageN + 1), rows)
        except Exception as e:
            print(e)
            driver.quit()
            driver = webdriver.Chrome(executable_path='DIRVER\chromedriver.exe')
            driver.maximize_window()
            driver.get(smsurl)
            time.sleep(2)
            # 排除其他弹出窗干扰
            try:
                other = driver.find_element_by_xpath('//*[@id="body"]/div[2]/div/div[2]')
                if other.is_enabled():
                    other.click()
            except Exception as notfountde:
                pass
            # 登录
            driver.find_element_by_xpath('//*[@id="kioc8i8g_login"]/a[1]').click()
            driver.find_element_by_xpath('//*[@id="kln22343_wechat"]').click()
            driver.implicitly_wait(3)
            driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[1]/td/div/input').send_keys("15122887395")
            driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[2]/td/div/input').send_keys("aaaa1111")
            driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[4]/td/button').click()
            driver.implicitly_wait(3)
            time.sleep(2)
    driver.quit()


def loadItemList(jsonFilePath):
    with open(jsonFilePath, 'r', encoding='utf-8') as jf:
        itemDct = json.load(jf)
    jf.close()
    return itemDct


def isDownload(htmlFolder):
    downloadSet = set()
    for html_Name in os.listdir(htmlFolder):
        htmlName = int(html_Name.split('_')[0])
        downloadSet.add(htmlName)
    print(downloadSet)
    return downloadSet


def saveDetails(driver, id, pageNum, rows):
    for rowNum, rowItem in enumerate(rows):
        rowItem.click()
        driver.switch_to.window(driver.window_handles[1])
        driver.implicitly_wait(2)
        time.sleep(2)
        html_source = driver.page_source
        f = open('pageDetails/' + str(id.zfill(5)) + '_' + str(pageNum) + '_' + str(rowNum) + '.html', mode="w", encoding="utf-8")
        f.write(html_source)
        f.close()
        driver.close()
        # 定位回原来的页面
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)


def main(idx):
    url = 'https://www.wuxuwang.com/yaopinsms'
    jsonFilePath = r'originalFiles/idAndName/id2names.json'
    htmlFolder = r'E:\PyProject\spider_wuxuwang\pageDetails'
    downloadSet = isDownload(htmlFolder)
    itemDict = loadItemList(jsonFilePath)
    itemDictNew = {}
    for k, v in itemDict.items():
        # if int(k) > max(list(downloadSet)):
        if int(k) > idx and (int(k) not in list(downloadSet)):
            itemDictNew[k] = v
    print(itemDictNew)
    print(len(itemDictNew))
    login(url, itemDictNew)


if __name__ == '__main__':
    idx = 455
    main(idx)
