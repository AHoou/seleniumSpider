import math
import os
import random
import re
import shutil
import time
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from getNameAndIndicationsFromHtml import writeExcel, getMedicineEntry
from ocr2jsonNanjing import general_get_api, ocrResult2json

# url地址
url = 'https://www.wuxuwang.com/yaopinsms'

# 结果文件夹
resultFolder = './result'

# 中间结果文件夹
pagesFolder = './pages'
pagesHtmlFolder = './pagesHtml'
pagesImgsFolder = './pagesImgs'
pagesJsonFolder = './pagesJson'

# chrome配置
chromePath = "DIRVER/chromedriver.exe"  # windows
# chromePath = "/usr/local/bin/chromedriver"  # linux
chromeOptions = Options()
user_agent_list = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17']
chromeOptions.add_argument("--no-sandbox")  # bypass OS security model
chromeOptions.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
chromeOptions.add_argument('--headless')
chromeOptions.add_argument('blink-settings=imagesEnabled=false')
chromeOptions.add_argument('--disable-gpu')

fail_list = []


def createFolder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


def initFolders(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
    else:
        shutil.rmtree(folder)
        os.mkdir(folder)


def list2dict(medicineNameList):
    idAndName_dict = {}
    id = 1
    for medicineName in medicineNameList:
        idAndName_dict[id] = medicineName.strip()
        id += 1
    return idAndName_dict


def loginAndGetDriver(wuxurl):
    random_id = random.randint(0, 5)
    chromeOptions.add_argument(f'user-agent={user_agent_list[random_id]}')
    driver = webdriver.Chrome(executable_path=os.path.abspath(chromePath), chrome_options=chromeOptions)
    driver.maximize_window()
    driver.get(wuxurl)
    time.sleep(2)
    # 排除其他弹出窗干扰
    try:
        other = driver.find_element_by_xpath('//*[@id="body"]/div[2]/div/div[2]')
        if other.is_enabled():
            other.click()
    except Exception as notFoundError:
        pass
    # 登录
    driver.implicitly_wait(3)
    driver.find_element_by_xpath('//*[@id="kioc8i8g_login"]/a[1]').click()
    driver.find_element_by_xpath('//*[@id="kln22343_wechat"]').click()
    driver.implicitly_wait(3)
    driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[1]/td/div/input').send_keys("15122887395")  # 用户名
    driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[2]/td/div/input').send_keys("aaaa1111")  # 密码
    driver.find_element_by_xpath('//*[@id="pane-first"]/form/table/tr[4]/td/button').click()
    time.sleep(1)
    return driver


def loginAndGetItems(wuxurl, itemDict, itemNum):
    driver = loginAndGetDriver(wuxurl)
    # 检索并爬取
    for id, name in itemDict.items():
        try:
            print('    Step3:共' + str(itemNum) + '个药品，正在爬取第' + str(id) + "个药品")
            driver.implicitly_wait(3)
            driver.find_element_by_xpath('//*[@id="kiy4cx57_autobox"]/div/div/input').clear()  # 清空名称输入框
            driver.find_element_by_xpath('//*[@id="kiy4cx57_autobox"]/div/div/input').send_keys(name)
            time.sleep(1)
            driver.find_element_by_xpath('//*[@id="kiy4uhi3_btn"]/button').click()
            time.sleep(2)
            # 获取第一页源代码并解析页数
            html_source = driver.page_source
            html = etree.HTML(html_source, etree.HTMLParser())
            itemsNumberString = html.xpath('//*[@id="kmq44q29_box"]/div[4]/div[1]/span/text()')
            itemsNumber = int(re.findall(r"\d+\.?\d*", itemsNumberString[0])[0])  # 获取条数
            pageNumber = math.ceil(itemsNumber / 20)
            if pageNumber > 0:
                for pageN in range(pageNumber):  # 翻页，如果只有一页，翻页会失效依然是第一页
                    nextPage = driver.find_element_by_xpath('//*[@id="kmq44q29_box"]/div[4]/div[2]/div/button[2]/i')
                    if EC.element_to_be_clickable(nextPage):
                        nextPage.click()
                        driver.implicitly_wait(5)
                        html_source_subPage = driver.page_source
                        f = open(os.path.join(pagesFolder, str(str(id).zfill(5)) + '_' + str(pageN + 1) + '.html'), mode="w", encoding="utf-8")
                        f.write(html_source_subPage)
                        f.close()
                        time.sleep(2)
        except Exception as e:
            fail_list.append("download html fail:" + str(id) + '  ' + str(name) + "  failReason:" + str(e))
            driver.close()
            driver = loginAndGetDriver(wuxurl)  # 重新启动
    driver.quit()


def svg2html(html_path, page_html_path, size_3, size_10, size_20):
    html = etree.parse(html_path, etree.HTMLParser())
    result = etree.tostring(html)
    bs_xml = BeautifulSoup(result, features="lxml")
    for item in ['kmpwqybf_strength', 'kmpwqybf_company']:
        divs = bs_xml.findAll('div', {'class': item})
        itemNums = len(divs)
        new_html_content = ''
        for div in divs:
            new_div = '<div class="' + str(item) + '">' + str(div.contents[0]) + '</div>'
            new_html_content += new_div
        pre_padding = '<!DOCTYPE html><html><body><table height="100%" width="100%" border="0" cellpadding="0" cellspacing="100"><tr valign="middle" align="center"><td valign="middle" align="center">' + '\n'
        after_padding = '\n' + '</td></tr></table></body></html>'
        new_html = pre_padding + new_html_content + after_padding
        new_html_name = page_html_path.split('.html')[0] + '_' + str(item) + '.html'
        with open(new_html_name, 'w', encoding='utf-8')as hf:
            hf.write(new_html)
        hf.close()
        if itemNums <= 3:
            size_3.append(os.path.basename(new_html_name))
        elif 3 < itemNums <= 10:
            size_10.append(os.path.basename(new_html_name))
        else:
            size_20.append(os.path.basename(new_html_name))
    return size_3, size_10, size_20


def getChromeDriver(w, h):
    driver = webdriver.Chrome(executable_path=os.path.abspath(chromePath), chrome_options=chromeOptions)
    driver.set_window_size(w, h)
    return driver


def html2imgByDiffSize(w, h, pageHtmlNameList, pageHtmlFolder, pageImgFolder):
    # 2.创建谷歌驱动
    chromeDriver = getChromeDriver(w, h)
    # 3.将新的html转为图片
    for pageHtmlName in pageHtmlNameList:
        pageHtmlPath = os.path.abspath(os.path.join(os.path.abspath(pageHtmlFolder), pageHtmlName))
        try:
            chromeDriver.get("file:///" + pageHtmlPath)
            chromeDriver.implicitly_wait(2)
            imgPath = os.path.join(pageImgFolder, os.path.basename(pageHtmlPath).split('.html')[0] + ".png")
            chromeDriver.get_screenshot_as_file(imgPath)

        except WebDriverException as e:
            chromeDriver.close()
            fail_list.append(str(os.path.basename(pageHtmlPath)) + '  html2imgfail: ' + str(e))
    # 4.关闭驱动
    try:
        chromeDriver.quit()
    except Exception as quitExp:
        pass


def converter(pageFolder, pageHtmlFolder, pageImgFolder):
    # 1.将源html网页中的svg标签取出组建新的html
    # 这里要根据网页中药品条目的多少进行分类，保证最终svg图片大小适合以提高ocr识别率
    size_3 = []  # 药品数目小于等于3时，窗口宽高为800*400
    size_10 = []  # 药品数目大于3且小于等于7时，窗口宽高为800*800
    size_20 = []  # 药品数目小于等于3时，窗口宽高为800*800
    for pageName in os.listdir(pageFolder):
        pagePath = os.path.join(os.path.abspath(pageFolder), pageName)
        pageHtmlPath = os.path.join(os.path.abspath(pageHtmlFolder), pageName)
        size_3, size_10, size_20 = svg2html(pagePath, pageHtmlPath, size_3, size_10, size_20)
    # print('-' * 20 + "svg2html done" + '-' * 20)

    # 2.3.4. 将html转化为图片并根据不同的窗口大小截图
    if len(size_3):
        html2imgByDiffSize(800, 400, size_3, pageHtmlFolder, pageImgFolder)
        time.sleep(1)
    if len(size_10):
        html2imgByDiffSize(800, 800, size_10, pageHtmlFolder, pageImgFolder)
        time.sleep(1)
    if len(size_20):
        html2imgByDiffSize(800, 800, size_20, pageHtmlFolder, pageImgFolder)
        time.sleep(1)
    # print('-' * 20 + "html2png done" + '-' * 20)


def svg2jsonByOCR(imgFolder, jsonFolder):
    for img in tqdm(os.listdir(imgFolder)):
        imgPath = os.path.join(imgFolder, img)
        jsonPath = os.path.join(jsonFolder, img.split('.png')[0] + '.json')
        try:
            fr = open(imgPath, 'rb')
            image = fr.read()
            result = general_get_api(image)
            ocrResult2json(result, jsonPath)
        except Exception as e:
            fail_list.append(str(imgPath) + "  " + str(e))


def main(medicineNameList, excelName):
    # 1. 清空上次爬取的文件
    print("Step1:清除上次的中间文件...")
    initFolders(pagesFolder)
    initFolders(pagesHtmlFolder)
    initFolders(pagesImgsFolder)
    initFolders(pagesJsonFolder)
    print("Step1:清除上次的中间文件完成")

    # 2. 将去重的list转为dict，其中key=id,value=medicineName
    print("Step2:将列表转为字典...")
    idAndNameDict = list2dict(medicineNameList)
    print("Step2:将列表转为字典完成")

    # 3. 爬取网页文件
    print("Step3:根据药品名称爬取网页...")
    loginAndGetItems(url, idAndNameDict, len(idAndNameDict))
    print("Step3:根据药品名称爬取网页完成")

    # 4. 将网页文件中的svg转化为图片
    print("Step4:提取网页中的svg字段转化为图片...")
    converter(pagesFolder, pagesHtmlFolder, pagesImgsFolder)
    print("Step4:提取网页中的svg字段转化为图片完成")

    # 5. 将svg进行ocr识别生成json
    print("Step5:将图片进行OCR识别...")
    svg2jsonByOCR(pagesImgsFolder, pagesJsonFolder)
    time.sleep(1)
    print("Step5:将图片进行OCR识别完成")

    # 6. 解析html获取药品名称呼和适应症，解析json获取公司名称和药品规格
    print("Step6:解析各字段并组合...")
    medicineItems, failNames = getMedicineEntry(pagesFolder, pagesJsonFolder)
    time.sleep(1)
    print("Step6:解析各字段并组合完成")

    # 7. 写入excel
    print("Step7:写入excel...")

    excelPath = os.path.join(resultFolder, excelName)
    writeExcel(medicineItems, excelPath)
    print("Step7:写入excel完成")

    # 8. 将失败记录到文件中
    for fn in failNames:
        fail_list.append(fn)
    with open('failFiles.txt', 'w', encoding='utf-8')as ff:
        if len(fail_list):
            for name in fail_list:
                ff.write(name + '\n')
        ff.close()


if __name__ == '__main__':
    medicineList = ["去氧肾上腺素", "扑尔伪麻片", "右美沙芬"]
    excelName = time.strftime("/%Y-%m-%d_%H_%M_%S", time.localtime(time.time()))
    main(medicineList, excelName)
