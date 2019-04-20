import time
from email.mime.multipart import MIMEMultipart
import pymysql
import requests
from requests.exceptions import RequestException
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header


class news:
    def __init__(self):
        self.db = pymysql.connect("139.199.36.66", "root", "abc132465987", "schoolnews")
        self.cursor = self.db.cursor()

    def getNews(self, url):
        try:
            reponse = requests.get(url)
            if reponse.status_code == 200:
                reponse.encoding = 'utf-8'
                return reponse.text
            else:
                return None
        except RequestException:
            return None

    def getFirstNew(self, html):
        result = re.compile('<li.*?line_u8_0.*?href="..(.*?)".*?title="(.*?)">', re.S)
        itrm = re.findall(result, html)
        for i in itrm:
            yield {
                'link': 'http://jwcw.xatu.cn' + i[0],
                'title': i[1]
            }

    def getArticle(self, artUrl):
        try:
            artReponse = requests.get(artUrl)
            if artReponse.status_code == 200:
                artReponse.encoding = 'utf-8'
                artHtml = artReponse.text
                artResult = re.compile('日期(.*?)下一条', re.S)
                item = re.findall(artResult, artHtml)
                for i in item:
                    yield {
                        'content': i
                    }
            else:
                return None
        except RequestException:
            return None

    def sendEmail(self, title, content):
        # 配置邮箱账户及收发人信息
        sender = 'everythinggrows@163.com'
        receivers = ['1020854430@qq.com']
        mail_host = 'smtp.163.com'
        mail_user = 'everythinggrows@163.com'
        mail_pass = 'egofficialmu123'

        # 构建MIMEMultipart对象，并在其中添加邮件内容信息
        message = MIMEMultipart()
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        message['From'] = 'everythinggrows@163.com'
        message['To'] = '1020854430@qq.com'
        subject = title
        print(subject)
        message['Subject'] = Header(subject, 'utf-8')

        # 发送邮件
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功！")
        except smtplib.SMTPException:
            print("邮件发送失败！")

    def doSome(self):
        print("go to dosome")
        url = 'http://jwcw.xatu.cn/tzgg/xs.htm'
        html = news.getNews(self, url)
        for it in news.getFirstNew(self, html):
            articleUrl = it.get('link')
            artTitle = it.get('title')
            for em in news.getArticle(self, articleUrl):
                con = em.get('content')
                sqlSelect = 'SELECT * FROM last_title WHERE id = 1'
                sqlUpdate = 'UPDATE last_title SET title = \'' + artTitle + '\' WHERE id = 1 '
                print(sqlUpdate)
                self.cursor.execute(sqlSelect)
                result = self.cursor.fetchall()
                res = result[0][1]
                print("db=%s" % res)
                if artTitle == res:
                    break
                else:
                    self.cursor.execute(sqlUpdate)
                    self.db.commit()
                    news.sendEmail(self, artTitle, con)


if __name__ == '__main__':
    r = news()
    while True:
        r.doSome()
        time.sleep(2 * 60 * 60)
