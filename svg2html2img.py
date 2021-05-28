import os
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from tqdm import tqdm

fail_list = []


def svg2html(html_path, page_html_path):
    html = etree.parse(html_path, etree.HTMLParser())
    result = etree.tostring(html)
    bs_xml = BeautifulSoup(result, features="lxml")
    for item in ['kmpwqybf_strength', 'kmpwqybf_company']:
        divs = bs_xml.findAll('div', {'class': item})
        new_html_content = ''
        for div in divs:
            new_div = '<div class="' + str(item) + '">' + str(div.contents[0]) + '</div>'
            new_html_content += new_div
        new_html = '<!DOCTYPE html><html><body>' + '\n' + new_html_content + '\n' + '</body></html>'
        with open(page_html_path.split('.html')[0] + '_' + str(item) + '.html', 'w', encoding='utf-8')as hf:
            hf.write(new_html)
        hf.close()
    return


def getChromeDriver():
    options = webdriver.ChromeOptions()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(900, 800)
    return driver


def html2img(driver, url, imgFolder):
    driver.get(url)
    driver.implicitly_wait(2)
    imgPath = os.path.join(imgFolder, os.path.basename(url).split('.html')[0] + ".png")
    driver.get_screenshot_as_file(imgPath)


def run(pageFolder, pageHtmlFolder, pageImgFolder):
    if not os.path.exists(pageHtmlFolder):
        os.mkdir(pageHtmlFolder)
    if not os.path.exists(pageImgFolder):
        os.mkdir(pageImgFolder)

    # 1.将源html网页中的svg标签取出组建新的html
    for pageName in tqdm(os.listdir(pageFolder)):
        pagePath = os.path.join(pageFolder, pageName)
        pageHtmlPath = os.path.join(pageHtmlFolder, pageName)
        svg2html(pagePath, pageHtmlPath)
    print('-' * 20 + "svg2html done" + '-' * 20)

    # 2.创建谷歌驱动
    chromeDriver = getChromeDriver()

    # 3.将新的html转为图片
    for pageHtmlName in tqdm(os.listdir(pageHtmlFolder)):
        pageHtmlPath = os.path.abspath(os.path.join(pageHtmlFolder, pageHtmlName))
        # print("html2png: " + str(pageHtmlName))
        try:
            html2img(chromeDriver, pageHtmlPath, pageImgFolder)
        except WebDriverException:
            chromeDriver.quit()
            fail_list.append(os.path.basename(pageHtmlPath))
            print(len(fail_list))
    print('-' * 20 + "html2png done" + '-' * 20)

    # 4.关闭驱动
    try:
        chromeDriver.quit()
    except Exception as quitExp:
        pass

    # 5.将失败的html记录到文件中
    if len(fail_list):
        with open('failHtmlNames.txt', 'w', encoding='utf-8')as ff:
            for name in fail_list:
                ff.write(name + '\n')
        ff.close()


if __name__ == '__main__':
    pageFolder = 'pages'
    pageHtmlFolder = 'pagesHtml'
    pageImgFolder = 'pagesImgs'
    run(pageFolder, pageHtmlFolder, pageImgFolder)
