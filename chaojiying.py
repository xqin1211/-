#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5
from url import *


class Chaojiying_Client(object):

    def __init__(self, username='qinxue', password='westone0628', soft_id='920315'):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype=1902):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        4006 -- 1~6位纯数字 -- 15提分（1元=1000题分）
        1902 -- 常见4~6位英文数字 -- 10,12,15提分（1元=1000题分）
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def ReportError(self, im_id='4006'):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


class CodeLogin(object):

    def __init__(self, city):
        # pass
        self._url = Login_URL[city]["url"]
        self._user = Login_URL[city]["username"]
        self._pass = Login_URL[city]["password"]
        # https://www.evsafety.cn/VerifyCode/VerifyCode?t=637630293543310647
        self._code_url = Code_URL[city]["url"] + Code_URL[city]["param"]
        self._download_url = spider_file[city]["url"]
        self._code = ""

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"

        }
        self.session = requests.session()

    def __enter__(self):
        self.Login()

    def get_sample(self):
        # 下载图片
        res = requests.get(self._code_url, headers=self.headers)

        # 保存图片，二进制写入
        filename = "./code/code" + str(get_timestamp_now()) + ".jpg"
        with open(filename, 'wb') as fp:
            fp.write(res.content)
            fp.flush()

        return filename

    def Login(self):
        chaojiying = Chaojiying_Client()

        # 获取验证码图片
        code_img = self.get_sample()

        # 第三方打码平台'超级鹰'进行识别验证码
        # with open(code_img, 'rb').read() as img:
        #     ret = chaojiying.PostPic(img)
        #     self._code = ret['pic_str']
        with open(code_img, 'rb') as img:
            ret = chaojiying.PostPic(img.read())
            self._code = ret['pic_str']

        # 构造登录data uname=gqft&pwd=gtmcmail_8800&veryCode=32816&ck=false
        data = {
            'uname': self._user,
            'pwd': self._pass,
            'eryCode': self._code,  # 识别出的验证码结果
            'ck': "false"
        }
        print(data)

        # 登录
        res = self.session.post(self._url, headers=self.headers, data=data)
        print(res.text)

    def download(self, output_path):
        res = self.session.get(self._download_url, stream=False)
        with open(output_path, mode='wb') as f:
            f.write(res.content)


class CodeLoginWithSelenium(object):

    def __init__(self, city):
        self._url = Login_URL[city]["url"]
        self._user = Login_URL[city]["username"]
        self._pass = Login_URL[city]["password"]
        # https://www.evsafety.cn/VerifyCode/VerifyCode?t=637630293543310647
        self._code_url = Code_URL[city]["url"] + Code_URL[city]["param"]
        self._download_url = spider_file[city]["url"]
        self._code = ""

    def Login(self):
        pass


if __name__ == '__main__':
    # file = "C://Users//xqin//Desktop//监控平台//yangben//code.jpg"
    # chaojiying = Chaojiying_Client('qinxue', 'westone0628', '920315')  # 用户中心>>软件ID 生成一个替换 96001
    # im = open(file, 'rb').read()  # 本地图片文件路径， WIN系统须要//
    # print(chaojiying.PostPic(im, 4006))  # 1902 验证码类型 1~6个纯数字， 官方网站>>价格体系

    path = "./data/tt.xlsx"
    cl = CodeLogin("beijing")
    cl.Login()
    cl.download(path)
