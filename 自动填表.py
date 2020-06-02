import configparser
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
# 简单邮件传输协议
import smtplib
import email
import time
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class Text(object):

    def loding(self):

        conf = configparser.ConfigParser()
        conf.read(r'相关信息.ini', encoding="utf-8")
        self.account = conf['MESSAGE']['account']
        self.password = conf['MESSAGE']['password']
        self.flag = conf['MESSAGE']['flag'] 
        self.from_email = conf['MESSAGE']['from_email']
        self.to_email = conf['MESSAGE']['to_email']
        self.key = conf['MESSAGE']['key']
        

    def getCookies(self):

        url_get = 'https://cumt.cpdaily.com/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'
        chrome_options = Options()
        chrome_options.add_argument('--headless')     #调用chrome无头模式
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])       #不打印console信息
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url_get)
        driver.find_element_by_id('username').send_keys(str(self.account))
        driver.find_element_by_id('password').send_keys(str(self.password))
        driver.find_element_by_id('signIn').click()
        cookies = driver.get_cookies()
        value1 = cookies[1]['value']
        value2 = cookies[0]['value']
        cookie = {
            'Cookie': 'acw_tc=' + value1 + '; MOD_AUTH_CAS=' + value2
        }

        self.cookie = cookie


    def getData(self):

        url_checkList = 'https://cumt.cpdaily.com/wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; OPPO R11 Plus Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36 yiban/8.1.11 cpdaily/8.1.11 wisedu/8.1.11',
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        params = {
                'pageSize': 6,
                'pageNumber': 1
            }

        responed = requests.post(url=url_checkList,headers=headers,data=json.dumps(params),cookies=self.cookie)
        # 检查是否有报表
        if(responed.json()['datas']['rows'] == []):
            print("暂未发布报表")
            collectWid = ''
            self.Data = ''
        else:
            collectWid = responed.json()['datas']['rows'][0]['wid']
            formWid = responed.json()['datas']['rows'][0]['formWid']

        if(collectWid != ''):

            url_detailCollector = 'https://cumt.cpdaily.com/wec-counselor-collector-apps/stu/collector/detailCollector'
            params = {"collectorWid": collectWid}
            responed = requests.post(url=url_detailCollector,headers=headers,data=json.dumps(params),cookies=self.cookie)
            schoolTaskWid = responed.json()['datas']['collector']['schoolTaskWid']

            url_getFormFields = 'https://cumt.cpdaily.com/wec-counselor-collector-apps/stu/collector/getFormFields'
            params = {
                "pageSize":9,
                "pageNumber":1,
                "formWid":formWid,
                "collectorWid":collectWid
            }
            responed = requests.post(url=url_getFormFields,headers=headers,data=json.dumps(params),cookies=self.cookie)
            form = responed.json()['datas']['rows']

            self.Data = {'collectWid': collectWid, 'formWid': formWid, 'schoolTaskWid': schoolTaskWid, 'form': form}

    def fillForm(self):

        list_ = ['本科生','是','36~37.2℃（正常体温）','否','否','','否','','是']
        
        cnt = 0
        flag = 0
        flag_1 = 0

        form = self.Data['form']
        for item in form:
            # 必填项
            if item['isRequired'] == 1:
                # 单选
                if item['fieldType'] == 2:
                    fieldItems = item['fieldItems']
                    for i in range(0, len(fieldItems)):
                        if flag_1 == 1 :
                            i = i - 1
                            flag_1 = 0

                        if fieldItems[i]['content'] == list_[cnt]:                         
                            fieldItems[i]['isSelected'] = 1
                            flag += 1
                        else :
                            del fieldItems[i]        # 如果不删除将会报“单选只能选一个”错误！！！！！
                            flag_1 = 1 
            cnt += 1

        if cnt != 9 :
            print("表单默认值配置不正确，请检查")
        elif flag != 7 :
            print("填写错误")
        else :
            self.form = form
    

    def submitForm(self):

        formWid = self.Data['formWid']
        address = '中国江苏省徐州市铜山区学苑南路'
        collectWid = self.Data['collectWid']
        schoolTaskWid = self.Data['schoolTaskWid']
        form = self.form

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'cumt.cpdaily.com',
            'Content-Length': '69',
            'Cpdaily-Extension': '1wAXD2TvR72sQ8u+0Dw8Dr1Qo1jhbem8Nr+LOE6xdiqxKKuj5sXbDTrOWcaf v1X35UtZdUfxokyuIKD4mPPw5LwwsQXbVZ0Q+sXnuKEpPOtk2KDzQoQ89KVs gslxPICKmyfvEpl58eloAZSZpaLc3ifgciGw+PIdB6vOsm2H6KSbwD8FpjY3 3Tprn2s5jeHOp/3GcSdmiFLYwYXjBt7pwgd/ERR3HiBfCgGGTclquQz+tgjJ PdnDjA==',
            'Connection': 'Keep-Alive',
            'Referer': 'https://cumt.cpdaily.com/wec-counselor-collector-apps/stu/mobile/index.html?collectorWid=' + str(collectWid) ,
            'Origin': 'https://cumt.cpdaily.com',
            'accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'x-requested-with': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.4; VOG-AL00 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Safari/537.36  cpdaily/8.1.14 wisedu/8.1.14'
        }

        params = {
            "formWid": formWid, "address": address, "collectWid": collectWid, "schoolTaskWid": schoolTaskWid,
            "form": form
            }

        url_submitForm = 'http://cumt.cpdaily.com/wec-counselor-collector-apps/stu/collector/submitForm'
        responed = requests.post(url=url_submitForm, headers=headers, cookies=self.cookie, data=json.dumps(params))
        self.msg = responed.json()['message']

    # 若计算机名含中文，这会报编码错误

    def send_email(self):

        today_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 设置邮箱的域名
        HOST = 'smtp.qq.com'
        # 设置邮件标题
        SUBJECT = '%s : %s 今日校园打卡情况 ' % (self.msg, today_time)
        # 设置发件人邮箱
        FROM = self.from_email
        # 设置收件人邮箱
        TO = self.to_email		# 可以同时发送到多个邮箱
        message = MIMEMultipart('related')
        
        # 发送邮件正文到对方的邮箱中
        message_html = MIMEText("今日校园打卡情况：%s" % self.msg, 'plain', 'utf-8')
        message.attach(message_html)

        # 设置邮件发件人
        message['From'] = FROM
        # 设置邮件收件人
        message['To'] = TO
        # 设置邮件标题
        message['Subject'] = SUBJECT

        # 获取简单邮件传输协议的证书
        email_client = smtplib.SMTP_SSL(host='smtp.qq.com')
        # 设置发件人邮箱的域名和端口，端口为465
        email_client.connect(HOST, '465')
        
        email_client.login(FROM, self.key)
        email_client.sendmail(from_addr=FROM, to_addrs=TO, msg=message.as_string())
        # 关闭邮件发送客户端
        email_client.close()

    def main(self):
        try:
            self.loding()

            print("正在获取Cookies")
            self.getCookies()
            print("已获取Cookies")

            print("正在获取相关数据")
            self.getData()

            if(self.Data != ''):
                print("已获取相关数据")

                print("正在填报报表")
                self.fillForm()

                self.submitForm()
                print(self.msg)
        except KeyError:
            print("请检查 相关信息.ini")
        except:
            print("未知错误")
            self.msg = '！！！ 未知错误 ！！！ 赶快手动填 ！！！'
        finally:
            if self.flag == '1' :
                self.send_email()
                print("成功发送邮件")
            os.system('pause')

Text().main()