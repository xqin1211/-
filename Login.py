#!/usr/bin/python
# -*—coding:utf8-*-
from email import message

from selenium import webdriver
from selenium.webdriver import ActionChains
from requests.cookies import RequestsCookieJar
import requests
from time import sleep
from url import *
import os
from PIL import Image
from chaojiying import Chaojiying_Client
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart

CJ = Chaojiying_Client()


#########################################
# webdriver.Chrome()网页操作
#########################################
class WebOperate:
    def __init__(self, url, city):
        # 不打开浏览器
        chrom_options = webdriver.ChromeOptions()
        # chrom_options.add_argument('--headless')
        # chrom_options.add_argument('--disable-gpu')
        jar = RequestsCookieJar()

        # 设置自定义下载路径
        download_path = os.getcwd() + '\\data\\' + city + '\\' + str(get_timestamp_now()) + '\\'
        mkdir(download_path)

        # 下载文件使用
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': download_path}
        chrom_options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(options=chrom_options)
        # self.browser = webdriver.Chrome()
        self._url = url

    def __enter__(self):
        self.open_browser(self._url)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get(self, url):
        self.driver.get(url)

    def open_browser(self):
        print("open browser with url {}".format(self._url))
        self.get(self._url)
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    def get_url(self, url):
        self.get(url)
        self.driver.implicitly_wait(10)

    def input(self, locator, value):
        print("user {}".format(value))
        self.driver.find_element_by_xpath(locator).send_keys(value)

    def click(self, locator):
        self.driver.find_element_by_xpath(locator).click()

    def find_element(self, locator):
        return self.driver.find_element_by_xpath(locator)

    def slider_move(self, locator):
        div = self.driver.find_element_by_xpath(locator)  # 滑块xpath
        # 实现滑动效果,重试三次
        re_operate = 3
        while re_operate > 0:
            if "验证通过" not in self.driver.page_source:
                ActionChains(self.driver).click_and_hold(on_element=div).perform()
                ActionChains(self.driver).move_to_element_with_offset(to_element=div, xoffset=30, yoffset=10).perform()
                ActionChains(self.driver).move_to_element_with_offset(to_element=div, xoffset=100, yoffset=20).perform()
                ActionChains(self.driver).move_to_element_with_offset(to_element=div, xoffset=200, yoffset=50).perform()
                re_operate = re_operate - 1
            else:
                break

    def get_cookies(self):
        return self.driver.get_cookies()

    def save_screenshot(self, file):
        self.driver.save_screenshot(file)

    # def screenshot(self, handle, file):
    #     handle.screenshot(file)

    def close(self):
        self.driver.close()

    def download(self, durl, locator):
        self.browser.get_url(durl)
        self.browser.click(locator=locator)
        sleep(3)


######################################
# 针对验证码数字明文写在html元素里的网站登录
# 沈阳监控平台
#####################################
class GenerateLogin:

    def __init__(self, city):
        self._url = Login_URL[city]["url"]
        self._user = Login_URL[city]["username"]
        self._pass = Login_URL[city]["password"]
        # self._code_url = Code_URL[city]["url"] + Code_URL[city]["param"]
        self._download_url = Spider_URL[city]["url"]
        self._xpath = Xpath[city]
        self.cookies = ""

        self.browser = WebOperate(url=self._url, city=city)

    def Login(self):
        # 1，打开浏览器，并打开网站
        self.browser.open_browser()

        # 2，输入用户名密码
        self.browser.input(locator=self._xpath["userInput"], value=self._user)
        self.browser.input(locator=self._xpath["passInput"], value=self._pass)

        # 6，点击登录
        self.browser.click(locator=self._xpath["loginBtn"])

        # 获取cookie
        self.cookies = self.browser.get_cookies()
        print(self.cookies.json())

        # return cookies

    def download(self):
        locator = ""
        self.browser.download(durl=self._download_url, locator=locator)


######################################################
# 针对登录需要移动滑块的网站，本脚本借助webdriver.Chrome实现
######################################################
class SliderLogin(GenerateLogin):
    def __init__(self, city='shanghai'):
        super().__init__(city)
        # self.download_url = Spider_URL[city]

    def Login(self):
        self.browser.open_browser()
        # input username and password
        self.browser.input(locator=self._xpath["userInput"], value=self._user)
        self.browser.input(locator=self._xpath["passInput"], value=self._pass)
        # move the slider
        self.browser.slider_move(locator=self._xpath["sliderBtn"])
        # click login button
        self.browser.click(locator=self._xpath["loginBtn"])
        self.cookies = self.browser.get_cookies
        print(self.cookies)

    def __enter__(self):
        super(SliderLogin, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(SliderLogin, self).__exit__()

    def download(self):
        locator = "//tr[./td/div[text()='数据接入协议（HS170405）']]//span"
        self.browser.download(durl=self._download_url, locator=locator)


#################################
# 针对验证码是图片的网站，需要借助第三方识别验证码：本文中使用的是’超级鹰‘
################################
class CodePicLogin(GenerateLogin):

    def __init__(self, city):
        super(CodePicLogin, self).__init__(city)

    def Login(self):
        # 1，打开浏览器，并打开网站
        self.browser.open_browser()

        # 2，输入用户名密码
        self.browser.input(locator=self._xpath["userInput"], value=self._user)
        self.browser.input(locator=self._xpath["passInput"], value=self._pass)

        # 3、截取图片验证码图片，保存到本地
        code_file = "./code/code" + str(get_timestamp_now()) + ".png"
        imgElement = self.browser.find_element(locator=self._xpath['codeImg'])
        imgElement.screenshot(code_file)

        # 4，使用第三方平台识别图片验证码
        # with open(code_file, 'rb') as img:
        #     ret = CJ.PostPic(im=img.read(), codetype=1902)
        #     self._code = ret['pic_str']

        # 5，输入验证码
        self.browser.input(locator=self._xpath["codeInput"], value=self._code)

        # 6，点击登录
        self.browser.click(locator=self._xpath["loginBtn"])

        # 获取cookie
        self.cookies = self.browser.get_cookies()
        print(self.cookies)

        # return cookies

    def download(self):
        locator = "//tr[./td/div[text()='数据接入协议（HS170405）']]//span"
        self.browser.download(durl=self._download_url, locator=locator)


######################################
# 针对验证码数字明文写在html元素里的网站登录
# 沈阳监控平台
#####################################
class CodeTextLogin(object):

    def __init__(self, city):
        super(CodeTextLogin, self).__init__(city)
        self._code = '123456'
        self.cookies = ''

    def Login(self):
        # 1，打开浏览器，并打开网站
        self.browser.open_browser()

        # 2，输入用户名密码
        self.browser.input(locator=self._xpath["userInput"], value=self._user)
        self.browser.input(locator=self._xpath["passInput"], value=self._pass)

        # 3、读取验证码元素的value，并输入验证码
        self._code = self.browser.find_element(locator=self._xpath['codeImg']).text
        print("value: {}".format(self._code))
        self.browser.input(locator=self._xpath["codeInput"], value=self._code)

        # 6，点击登录
        self.browser.click(locator=self._xpath["loginBtn"])

        # 获取cookie
        self.cookies = self.browser.get_cookies()
        print(self.cookies)

        # return cookies

    def download(self):
        locator = "//tr[./td/div[text()='数据接入协议（HS170405）']]//span"
        self.browser.download(durl=self._download_url, locator=locator)


class SendEmail:
    def __init__(self):
        # smtp 服务器信息
        self._host = 'smtp.163.com,25'
        self._sender = 'qinxue.1211@163.com'
        self._password = 'Xqin@12xue11'

        self._receivers = ['352478940@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        self.smtp = smtplib.SMTP()

        # 定义邮件信息
        self._message = ""

    def connect(self):
        self.smtp.connect(self._host)
        self.smtp.login(self._sender, self._password)

    def make_message(self, text):
        # self.smtp.sendmail(self._sender, self._receivers, message)
        self._message = MIMEText(text, 'plain', 'utf-8')
        self._message['From'] = Header("菜鸟教程", 'utf-8')
        self._message['To'] = Header("测试", 'utf-8')
        subject = 'Python SMTP 邮件测试'
        self._message['Subject'] = Header(subject, 'utf-8')

    def make_attach(self, files=[]):
        # 创建一个带附件的实例
        self._message = MIMEMultipart()
        self._message['From'] = Header("菜鸟教程", 'utf-8')
        self._message['To'] = Header("测试", 'utf-8')
        subject = 'Python SMTP 邮件测试'
        self._message['Subject'] = Header(subject, 'utf-8')

        self._message.attach(MIMEText('这是菜鸟教程Python 邮件发送测试……', 'plain', 'utf-8'))
        for f in files:
            att = MIMEText(open(f, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att["Content-Disposition"] = 'attachment; filename="%s"' % f
            self._message.attach(att)

    def send(self):
        self.smtp.sendmail(self._sender, self._receivers, self._message.as_string())

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtp.close()


if __name__ == '__main__':
    # url = platform['url']
    # city = "shanghai"
    # path = "./data/test.xls"

    # with SliderLogin(city) as sl:
    #     # print(sl.cookies)
    #     sl.download(spider_file[city], path)
    # sl = SliderLogin(city)
    # sl.Login()
    # print(sl.cookies)
    # sl.download(spider_file[city]["url"], path)

    sl = SliderLogin(city="shanghai")
    sl.Login()
    sl.download()

    # cpl = CodePicLogin(city="guojia")
    # cpl.Login()

    # ctl = CodeTextLogin(city="shenyang")
    # ctl.Login()

    # gl = GenerateLogin(city="chengdu")
    # gl.Login()
