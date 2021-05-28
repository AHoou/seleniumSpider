#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import base64
import json
import uuid
import os
import requests
from tqdm import tqdm

login_url = 'http://123.206.16.66:9108/api/login'
general_url = 'http://123.206.16.66:9108/api/general'


def get_guid():
    return str(uuid.uuid4()).replace("-", "")


def login(name, pwd):
    params = {'name': name, 'pwd': pwd}
    result = requests.post(login_url, json=params)
    print(result)
    if result.status_code == 200:
        result = result.json()
        print(result)
        return result
    return None


def general(token, img, json_path):
    """
    全文识别
    :param token:
    :return:
    """
    '''
    with open(pic_path, 'rb') as fr:
        img = base64.b64encode(fr.read())
        img = str(img, encoding="utf-8")
    '''
    img = base64.b64encode(img)
    img = str(img, encoding="utf-8")
    params = {
        'guid': get_guid(),
        'mtype': 'general',
        'image_bytes': img,
        'token': token
    }
    result = requests.post(general_url, json=params)
    print(result)
    if result.status_code == 200:
        result = result.json()
        if result['result']['code'] != -1:
            with open(json_path, 'w', encoding='utf-8') as fw:
                fw.write(json.dumps(result['result'], indent=4, ensure_ascii=False))
    return result


def all_text_ocr(pic, json):
    token = None
    login_result = login('dyy', 'dyy@butpt')
    if login_result:
        token = login_result['token']
        print("\n全文识别:")
        result = general(token, pic, json)
    return result


def text_for_ocr(img):
    token = None
    login_result = login('dyy', 'dyy@butpt')
    if login_result:
        token = login_result['token']
        print("\n全文识别:")
    params = {
        'guid': get_guid(),
        'mtype': 'general',
        'image_bytes': img,
        'token': token
    }
    result = requests.post(general_url, json=params)
    print(result)
    if result.status_code == 200:
        result = result.json()
    return result


def main():
    input_file_path = './images'
    json_path = './json'
    i = 0
    for root, dirs, files in os.walk(input_file_path):
        for file in files:
            if os.path.splitext(file)[1].lower() == '.png' or os.path.splitext(file)[1].lower() == '.jpg':
                i += 1
                with open(os.path.join(root, file), 'rb') as f_r:
                    json_store_path = json_path + '/' + str(i) + '.json'
                    img = f_r.read()
                    result = all_text_ocr(img, json_store_path)
                    print(result)
                    # with open(file + ".json", 'w', encoding='utf-8')as jf:
                    #     json.dump(result, jf, ensure_ascii=False, indent=4)
                    #     jf.close()


def post_url(url, data=None, json=None):
    res = requests.post(url, data=data, json=json)
    if res.status_code == 200:
        res = res.json()
        return res
    else:
        return res.status_code


def imagePDF_to_general_pdf_structure(general_pdf_structure):
    page_list = []
    url_ocr = 'http://123.206.18.208:10001/ocr/api/v1.1/kerjlvckvjikemnljkcvje/recognition'
    for page in general_pdf_structure['page_list']:
        image = page['rotated_image']
        guid = get_guid()
        params = {'guid': guid, 'fname': page['fname'], 'image': image, 'include_pts': 'true', 'include_ys': 'true'}
        result = post_url(url_ocr, data=params)
        page_list.append(result)
    general_pdf_structure['page_list'] = page_list


def general_get_api(image):
    image = str(base64.b64encode(image), encoding="utf-8")
    url_ocr = 'http://123.206.18.208:10001/ocr/api/v1.1/kerjlvckvjikemnljkcvje/recognition'
    guid = get_guid()
    params = {'guid': guid, 'fname': guid, 'image': image, 'include_pts': 'true', 'include_ys': 'true'}
    result = post_url(url_ocr, data=params)
    return result


def position_rows(text):
    """按坐标分行"""
    min_row_proportion = 0.7  # 最小行相交比例
    if len(text) == 1:
        return {1: [text[0]]}
    # 将text按照y排序
    sort_text = sorted(text, key=lambda n: n['y'])
    rows_dict = {}
    k = 1
    row_text = []
    max_y = -1
    # 将排好序的text同时列出数据和数据下标,并进行行内排序
    for i, item in enumerate(sort_text):
        # 最后一组
        if i + 1 == len(sort_text):
            if len(item['words'].strip()):  # strip()除去首尾空格
                if item['y'] <= max_y:
                    row_text.append(item)
                else:
                    if row_text:
                        row_text.sort(key=lambda n: n['x'])
                        rows_dict[k] = row_text
                        row_text = [item]
                        k += 1
                row_text.sort(key=lambda n: n['x'])
                rows_dict[k] = row_text
            else:
                if row_text:
                    row_text.sort(key=lambda n: n['x'])
                    rows_dict[k] = row_text
        # 前i-1组
        else:
            if len(item['words'].strip()) == 0:
                continue
            if item['y'] <= max_y:
                row_text.append(item)
            else:
                if row_text:
                    row_text.sort(key=lambda n: n['x'])
                    rows_dict[k] = row_text
                    row_text = []
                    k += 1
                max_y = item['y'] + item['h'] * min_row_proportion
                row_text.append(item)
    return rows_dict


def ocrResult2json(result, jsonPath):
    lines = []
    rows_dict = result['text']
    for row_dict in rows_dict:
        new_row_dict = {"text": row_dict["words"].strip()}
        lines.append(new_row_dict)
    up_lines = {"lines": lines}

    new_dict_Result = {"regions": [up_lines]}
    new_dict = {"Result": new_dict_Result}
    with open(jsonPath, 'w', encoding='utf-8')as jf:
        json.dump(new_dict, jf, ensure_ascii=False, indent=4)
        jf.close()


if __name__ == '__main__':
    fail_list = []

    imgFolder = r'E:\PyProject\spider_wuxuwang\pagesImgs'
    jsonFolder = r'E:\PyProject\spider_wuxuwang\pagesJson'

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

    # 将失败记录到文件中
    if len(fail_list):
        with open('failNames.txt', 'w', encoding='utf-8')as ff:
            for name in fail_list:
                ff.write(name + '\n')
        ff.close()
