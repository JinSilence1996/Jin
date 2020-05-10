# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
description
"""

import traceback
import json

import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal


def three_sum(nums):
    """
    :type nums: List[int]
    :rtype: List[List[int]]
    """
    res = []
    nums.sort()
    idx = 0
    while idx < len(nums):
        numx = nums[idx]
        if numx >= 0:
            break
        idy = idx + 1
        lenth = len(nums) - 1
        while idy < lenth:
            if numx + nums[idy] + nums[lenth] == 0:
                res.append((numx, nums[idy], -numx - nums[idy]))
                idy = len(nums) - list(reversed(nums)).index(nums[idy]) - 1
                lenth = nums.index(nums[lenth]) - 1
            elif numx + nums[idy] + nums[lenth] > 0:
                lenth = lenth - 1
            else:
                idy = idy + 1
        idx = len(nums) - list(reversed(nums)).index(numx)
    if nums.count(0) >= 3:
        res.append((0, 0, 0))
    return res

def test_request():
    """
    测试requests
    """
    baseurl = 'http://toodo.fun/funs/hot/api.php'
    headers = {
        'Host': 'toodo.fun',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                        'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                        'Chrome/84.0.4133.0 Safari/537.36 Edg/84.0.508.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,' \
                    'image/webp,image/apng,*/*;' \
                        'q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }
    req = requests.get(baseurl, params={'type': 'bilibili'}, headers=headers)
    req.encoding = 'utf-8'
    print(json.loads(req.text))

class DownloadUi(QtWidgets.QDialog):
    """
    下载数据
    """
    mySignal = pyqtSignal(list)
    downloadurl = ''

    def getstart(self):
        """
        下载数据
        """
        try:
            self.mySignal.emit([self.downloadurl, 16, "F:\\"])
        except:
            print(traceback.format_exc())


if __name__ == '__main__':
    print(three_sum([-1, 0, 1, 2, -1, -4]))
    DownloadUi().getstart()
