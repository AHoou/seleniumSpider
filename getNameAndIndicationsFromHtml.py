import json
import os
from bs4 import BeautifulSoup
from lxml import etree
import openpyxl
from tqdm import tqdm


def html2xml(html_path):
    html = etree.parse(html_path, etree.HTMLParser())
    htmlString = etree.tostring(html)
    return htmlString


def getNameFromHtml(htmlStr):
    names = []
    page = etree.HTML(htmlStr)
    aTitles = page.xpath('//div[@class="kmpwqybf_name"]/a')
    for aTitle in aTitles:
        title = aTitle.get('title').strip()
        names.append(title)
    return names


def getIndicationFromHtml(htmlStr):
    indications = []
    bs_xml = BeautifulSoup(htmlStr, features="lxml")
    for item in ['kmpwqybf_indication']:
        divs = bs_xml.findAll('div', {'class': item})
        for div in divs:
            pContent = ''
            for pItem in div.findAll('p'):
                pContent += pItem.text.strip()
            indications.append(pContent)
    return indications


def getCompanyOrStrengthFromJson(jsonPath):
    with open(jsonPath, 'r', encoding='utf-8')as jf:
        linesContent = json.load(jf)["Result"]["regions"][0]["lines"]
    jf.close()
    linesText = []
    for lineContent in linesContent:
        text = lineContent['text'].replace('\r\n', ' ')
        linesText.append(text)
    return linesText


def getMedicineEntry(htmlFolder, jsonFolder):
    medicineItems = []
    failNames = []
    for htmlFile in os.listdir(htmlFolder):
        htmlFilePath = os.path.join(htmlFolder, htmlFile)
        try:
            # 从html中解析名称和适应症
            htmlString = html2xml(htmlFilePath)
            names = getNameFromHtml(htmlString)
            indications = getIndicationFromHtml(htmlString)
            # 从json文件中解析规格和生产公司
            jsonFilePathCompany = os.path.join(jsonFolder, htmlFile.split('.html')[0] + '_kmpwqybf_company.json')
            jsonFilePathStrength = os.path.join(jsonFolder, htmlFile.split('.html')[0] + '_kmpwqybf_strength.json')
            companies = getCompanyOrStrengthFromJson(jsonFilePathCompany)
            strengths = getCompanyOrStrengthFromJson(jsonFilePathStrength)
            for item in list(zip(names, companies, strengths, indications)):
                medicineItems.append(item)
        except Exception as e:
            failNames.append(htmlFile + " ### " + str(e))
    return medicineItems, failNames


def writeExcel(medItems, excelName):
    f = openpyxl.Workbook()
    table = f.active
    for rowNum, rowItem in enumerate(medItems):
        for colNum, colItem in enumerate(list(rowItem)):
            table.cell(row=rowNum + 1, column=colNum + 1, value=colItem)
    f.save(excelName + '.xlsx')


if __name__ == '__main__':
    htmlFolder = r'E:\PyProject\spider_wuxuwang\pages'
    jsonFolder = r'E:\PyProject\spider_wuxuwang\pagesJson1'
    excelName = 'demo'

    medicineItems, failNames = getMedicineEntry(htmlFolder, jsonFolder)
    writeExcel(medicineItems, excelName)

    # 将失败的html记录到文件中
    if len(failNames):
        with open('failHtmlNames.txt', 'w', encoding='utf-8')as ff:
            for name in failNames:
                ff.write(name + '\n')
        ff.close()
