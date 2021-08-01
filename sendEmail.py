#!/usr/bin/python
# -*—coding:utf8-*-

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import parseaddr, formataddr
import os

class SendEmail:
    def __init__(self):
        # smtp 服务器信息
        self._host = 'smtp.163.com'
        self._sender = 'XXXXX@163.com'
        self._password = 'XXXXXXX'

        self._receivers = ['XXXXX@qq.com', self._sender]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        self.smtp = smtplib.SMTP()

        # 定义邮件信息
        self._message = ""

    def connect(self):
        try:
            self.smtp.connect(self._host, 25)
            self.smtp.login(self._sender, self._password)
        except smtplib.SMTPException as e:
            print("Error: 无法发送邮件, 错误信息：{}".format(e))

    def _format_addr(self, sender):
        name, addr = parseaddr(sender)
        # if name == "":
        #     name = sender.split("@")[0]
        print(name, addr)
        return formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, str) else addr))

    def send_message(self, subject='Python SMTP 邮件测试', text=""):
        self._message = MIMEText(text, 'plain', 'utf-8')
        self._message['From'] = self._sender
        self._message['To'] = ";".join(self._receivers)
        self._message['Subject'] = Header(subject, 'utf-8')
        self.send()

    def send_html(self, subject='Python SMTP 邮件测试', text=""):
        self._message = MIMEText(text, 'html', 'utf-8')
        self._message['From'] = self._sender
        self._message['To'] = ",".join(self._receivers)
        self._message['Subject'] = Header(subject, 'utf-8')
        self.send()

    def send_attach(self, subject='Python SMTP 邮件测试', text="", files=[]):
        # 创建一个带附件的实例
        self._message = MIMEMultipart()
        self._message['From'] = self._sender
        self._message['To'] = ",".join(self._receivers)
        self._message['Subject'] = Header(subject, 'utf-8')
        # 邮件正文是MIMEText:
        self._message.attach(MIMEText(text, 'plain', 'utf-8'))
        for f in files:
            att = MIMEApplication(open(f, 'rb').read())
            att.add_header('Content-Disposition', 'attachment', filename=os.path.split(f)[-1])
            self._message.attach(att)

        self.send()

    def send_image(self, subject='Python SMTP 邮件测试', text="", file=""):
        self._message = MIMEMultipart()
        imageApart = MIMEImage(open(file, 'rb').read(), file.split('.')[-1])
        imageApart.add_header('Content-Disposition', 'attachment', filename=os.path.split(file)[-1])
        # 邮件正文是MIMEText:
        self._message.attach(MIMEText(text, 'plain', 'utf-8'))
        self._message.attach(imageApart)
        self._message['From'] = self._sender
        self._message['To'] = ";".join(self._receivers)
        self._message['Subject'] = Header(subject, 'utf-8')
        self.send()

    def send(self):
        try:
            self.smtp.sendmail(self._sender, self._receivers, self._message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print("Error: 无法发送邮件, 错误信息：{}".format(e))

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtp.quit()
        self.smtp.close()


if __name__ == '__main__':

    sm = SendEmail()
    sm.connect()
    html = """
    <p>Python 邮件发送测试...</p>
    <p><a href="http://www.runoob.com">这是一个链接</a></p>
    """
    # with open('./email_template/t1.html', 'rb') as f:
    #     sm.send_html(text=f.read())

    # sm.send_message(text=str(get_timestamp_now()))
    basedir = 'C:\\Users\\code\\'
    # filelist = [basedir + "x.doc", basedir + "x.pdf"]
    # sm.send_attach(text="这是带附件的邮件测试。。。。", files=filelist)
    sm.send_image(text="这是带图片附件的邮件测试。。。。", file=basedir + "code1627707280443.png")
