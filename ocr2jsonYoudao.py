# -*- coding: utf-8 -*-
import json
import os
import sys
import uuid
import requests
import base64
import hashlib

from imp import reload

import time

from tqdm import tqdm

reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/ocrapi'
APP_KEY = '108fa1b7943bccd5'
APP_SECRET = 'MNfv8aJ935BQNt09EHs4wcGCkIPNQoh9'


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(imgPath, jsonPath):
    f = open(imgPath, 'rb')  # 二进制方式打开图文件
    q = base64.b64encode(f.read()).decode('utf-8')  # 读取文件内容，转换为base64编码
    f.close()

    data = {}
    data['detectType'] = '10012'
    data['imageType'] = '1'
    data['langType'] = 'auto'
    data['img'] = q
    data['docType'] = 'json'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['sign'] = sign

    response = do_request(data)
    content = json.loads(response.content.decode("utf-8"), encoding='utf-8')
    with open(jsonPath, 'w', encoding='utf-8')as jf:
        json.dump(content, jf, ensure_ascii=False, indent=4)
        jf.close()


if __name__ == '__main__':
    imgFolder = r'E:\PyProject\spider_wuxuwang\images1'
    jsonFolder = r'E:\PyProject\spider_wuxuwang\json1'
    for img in tqdm(os.listdir(imgFolder)):
        imgPath = os.path.join(imgFolder, img)
        jsonPath = os.path.join(jsonFolder, img.split('.png')[0] + '.json')
        connect(imgPath, jsonPath)
