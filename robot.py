import requests
import json
import time
import urllib
import re
import logging
import random

logging.basicConfig(level=logging.INFO,#控制台打印的日志级别
                    filename='robot.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    #日志格式
                    )

verifyKey = 'INITKEYXegd2lRo'

path_head = 'http://127.0.0.1:8088'
verify_path  ='/verify'
bind_path = '/bind'
getMsg_path = '/fetchMessage?sessionKey=%s&count=10'
send_group_message = '/sendGroupMessage'

r=requests.post(url=path_head + verify_path, data='{"verifyKey":"'+verifyKey+'"}')
print("r",r)
print("---",r.text)
r=json.loads(r.text)

sessionId = r['session']

r=requests.post(url=path_head + bind_path, data='{"sessionKey":"'+sessionId+'", "qq":"2155654750"}')

def get_group_msg(o):
    for i in o['messageChain']:
        if i['type'] == 'Plain':
            return i['text']
    return ''

def get_group_msgObject(o):
    for i in o['messageChain']:
        if i['type'] == 'Plain':
            return {'type': 'Plain', 'compare': i['text']}
    for i in o['messageChain']:
        if i['type'] == 'Image':
            return {'type': 'Image', 'compare': i['imageId'], 'url': i['url']}
    return None

def isSameMsgObject(o1, o2):
    if o1['type'] != o2['type']:
        return False

    return o1['compare'] == o2['compare']

def get_group_id(o):
    if 'sender' in o and 'group' in o['sender']:
        return o['sender']['group']['id']
    else:
        return None

def get_user_id(o):
    return o['sender']['id']
        

def get_magnet(fanhao):
    headers = {
        'Cookie': 'Hm_lvt_15e963b881954b9210deec054fd013cc=1632642958; Challenge=013a1c9f614b4656e58aee4d936a4bfc; ex=1; PHPSESSID=g84j4mkqindmresc7rd7js9tv6; Hm_lpvt_15e963b881954b9210deec054fd013cc=1632837937',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
    }
    cili_search = 'http://clb0.top/s/%s.html'
    fanhao = urllib.parse.quote(fanhao)

    magnet_htmls = []
    try:
        r=requests.get(url=cili_search % fanhao, headers = headers)
        magnet_htmls = re.findall('href="(/detail.*?)"', r.text)
        print(magnet_htmls)
    except:
        print("%s出错了" % fanhao)

    magnets = []
    for url in magnet_htmls[:3]:
        r=requests.get(url='http://clb0.top' + url, headers = headers)
        magnet = re.findall('href="(magnet.*?)"', r.text)
        if len(magnet) > 0:
            magnets.append(magnet[0])
    print(magnets)
    return magnets


def toHtmlPage(mags):
    if not mags or len(mags) == 0:
        return 'empty', ''

    page = ''
    for mag in mags:
        page += '<a style="font-size: 300%;" href="' + mag + '">' + mag + '</a></br>'
    page += '<script>setTimeout(()=>{window.location.href="'+mags[0]+'"}, 1000)</script>'
    page = '<body>' + page + '</body>'

    alpha = list('abcdefghijklmnopqrstuvwxyz')
    randomName = ''.join([random.choice(alpha) for i in range(10)])
    return randomName, page

recorder = {
    0: {
        'msg': {},
        'users': {},
        "sended": False
    }
}
while True:
    r = requests.get(url=path_head + getMsg_path % sessionId)
    print(r.text)

    is_sleep = True
    for msg in json.loads(r.text)['data']:
        logging.info(json.dumps(msg))
        if (msg['type'] == 'GroupMessage'):
            is_sleep = False

            if not get_group_id(msg) or not get_group_msgObject(msg):
                continue

            # 复读机 文字
            if get_group_id(msg) in recorder and isSameMsgObject(get_group_msgObject(msg), recorder[get_group_id(msg)]['msg']):
                recorder[get_group_id(msg)]['users'][get_user_id(msg)] = 0
            else:
                recorder[get_group_id(msg)] = {'msg':get_group_msgObject(msg), 'users':{get_user_id(msg): 0}, "sended": False}
            
            if not recorder[get_group_id(msg)]['sended'] and len(recorder[get_group_id(msg)]['users']) == 2:
                m = {}
                if recorder[get_group_id(msg)]['msg']['type'] == 'Plain':
                    m = {
                        "sessionKey": sessionId,
                        "target": get_group_id(msg),
                        "messageChain": [{"type": 'Plain', "text": recorder[get_group_id(msg)]['msg']['compare']}]
                    }
                elif recorder[get_group_id(msg)]['msg']['type'] == 'Image':
                    m = {
                        "sessionKey": sessionId,
                        "target": get_group_id(msg),
                        "messageChain": [{"type": 'Image', "url": recorder[get_group_id(msg)]['msg']['url']}]
                    }

                r = requests.post(
                    url=path_head + send_group_message, data=json.dumps(m))
                recorder[get_group_id(msg)]['sended'] = True

            # 复读机 图片
            

            # 磁力
            if get_group_msg(msg).strip().startswith('灰灰 '):
                magnets = get_magnet(get_group_msg(
                    msg).strip().lstrip('灰').strip())
                randomName, page = toHtmlPage(magnets)

                if len(magnets) == 0:
                    magnets.append(
                        '没找到'+get_group_msg(msg).strip().lstrip('灰').strip())
                m = {
                    "sessionKey": sessionId,
                    "target": get_group_id(msg),
                    "messageChain": [{"type": "Plain", "text": '\r\n'.join(magnets)}]
                    # "messageChain": [{"type": "Plain", "text": 'https://mcpix.cn/virtual/shortHttp/' + randomName}]
                }
                r = requests.post(
                    url=path_head + send_group_message, data=json.dumps(m))

    if is_sleep:
        time.sleep(0.1)

