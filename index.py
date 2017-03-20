#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re
import time
import os.path
try:
    from PIL import Image
except:
    pass
import json

# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
headers = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    'User-Agent': agent
}

# 使用登录cookie信息
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print(u"Cookie 未能加载")


def get_xsrf():
    '''_xsrf 是一个动态变化的参数'''
    index_url = 'https://www.zhihu.com'
    # 获取登录时需要用到的_xsrf
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    # 这里的_xsrf 返回的是一个list
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]


# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha
def newurl(s):
    try:
        url='https://www.zhihu.com/search?type=content&q='+s
        sx_page = session.get(url, headers=headers)
        soup = BeautifulSoup(sx_page.content, 'html.parser')
        urltitle = soup.find_all('a',class_='js-title-link')
        i=0
        nurl=[]
        while i<len(urltitle):
            nurl.append('https://www.zhihu.com'+urltitle[i].attrs['href'])
            i=i+2
        return nurl
    except:
        exit(1)
def sxurl(sxurl):
    #获取私信url
    try:
        sx_page = session.get(sxurl, headers=headers)
        soup = BeautifulSoup(sx_page.content, 'html.parser')
        followers=soup.find_all('a',class_='zm-item-link-avatar avatar-link')
        return followers
    except:
        exit(1)

def follow(name):
    headers2 = {
            'authorization':'Bearer Mi4wQUJESzI2cEs3QWdBRU1MZHAxSDZDaGNBQUFCaEFsVk5Kb0NsV0FBNkZXS0lpd1JFbDNTUUFBTVhla2FLZTVGMk1B|1485063154|4276ae68693f7ee1c95440855ee1f099c888fa4f',
            'Origin':'https://www.zhihu.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' ,
            }
    i=0
    try:
        while i<len(name):
            followersName = name[i].attrs['href'].split('/')[2]
            followersUrl = 'https://www.zhihu.com'+name[i].attrs['href']
            massageURL='https://www.zhihu.com/api/v4/members/'+followersName+'/followers'
            payload = {'some': 'data'}
            response = requests.post(massageURL, headers=headers2,data=payload) 
            if response.status_code==200:
                print '关注成功'+str(i)
            else:
                pass
            i=i+1
    except:
        pass
        
def sendMessage(tid):
    i=0
    userId=[]
    sendURL='https://www.zhihu.com/api/v4/messages'
    headers3 = {
            'authorization':'Bearer Mi4wQUJESzI2cEs3QWdBRU1MZHAxSDZDaGNBQUFCaEFsVk5Kb0NsV0FBNkZXS0lpd1JFbDNTUUFBTVhla2FLZTVGMk1B|1485068088|2202b8fed421a026cccde26cb94023cb9aff4b9d',
            'content-type': 'application/json',
            'Origin':'https://www.zhihu.com',
            'Host':'www.zhihu.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36' ,
            }
    try:
        while i<len(tid):
            followersUrl = 'https://www.zhihu.com'+tid[i].attrs['href']
            getId = session.get(followersUrl, headers=headers)
            userId.append(re.findall('&quot;(\w{32})&quot;},',getId.text)[0])
            params = {"type": "common", "content": "亲爱的知乎用户您好～窝是一只可爱的程序猿写的爬虫程序～对打扰您表示抱歉～我关注了你～希望你也关注我^_^", "receiver_hash": userId[i]}
            params_encode = json.dumps(params)
            response = requests.post(sendURL,headers=headers3,data=params_encode)
            if response.status_code==200:
                print '私信成功'+str(i)
            else:
                pass
            i=i+1
    except:
        pass
def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False
def login(secret, account):
    # 通过输入的用户名判断是否是手机号
    if re.match(r"^1\d{10}$", account):
        print(u"手机号登录 \n")
        post_url = 'https://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account,
        }
    else:
        if "@" in account:
            print(u"邮箱登录 \n")
        else:
            print(u"你的账号输入有问题，请重新登录")
            return 0
        post_url = 'https://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'email': account,
        }
    try:
        # 不需要验证码直接登录成功
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.text
        print(login_page.status_code)
        print(login_code)
    except:
        # 需要输入验证码后才能登录成功
        postdata["captcha"] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = eval(login_page.text)
        print(login_code['msg'])
    session.cookies.save()

try:
    input = raw_input
except:
    pass


if __name__ == '__main__':
    messageURL = 'http://www.zhihu.com/inbox/post'
    i=0
    if isLogin():
        sum=0
        print(u'您已经登录')
        url=newurl('帽子')
        while i<len(url):
            s=sxurl(url[i])
            follow(s)
            sendMessage(s)
            sum=sum+len(s)
            time.sleep(3)
        print '新关注了'+str(sum)+'个用户'
    else:
        account = input('username\n>  ')
        secret = input("password\n>  ")
        login(secret, account)
        
