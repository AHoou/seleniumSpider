"""
    南京ocr接口模板
"""

# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import base64
import json
import uuid
import os
import requests

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


if __name__ == '__main__':
    # 方式1
    fr = open('pagesImgs/00001_1_kmpwqybf_company.png', 'rb')
    image = fr.read()
    result = general_get_api(image)
    print(result)

    # 方式2
    # main()
