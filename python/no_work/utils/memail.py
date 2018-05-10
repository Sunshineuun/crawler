#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(error_info):
    email_host = 'smtp.tech-winning.com'  # 发件服务器地址
    sender = 'qiushengming@tech-winning.com'  # 发件人
    password = 'Winning123'  # 密码，如果是授权码就填授权码
    receiver = 'qiushengming@aliyun.com'  # 收件人

    msg = MIMEMultipart()
    msg['Subject'] = 'crawler error'  # 标题
    msg['From'] = 'python-crawler'  # 发件人昵称
    msg['To'] = 'qiushengming'  # 收件人昵称

    text = MIMEText(error_info, 'plain')  # 签名
    msg.attach(text)

    # 发送
    smtp = smtplib.SMTP()
    smtp.connect(email_host, 25)
    smtp.login(sender, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
