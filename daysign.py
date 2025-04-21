import os
import re
import time
import httpx
import traceback
import random
from contextlib import contextmanager
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from flaresolverr import FlareSolverrHTTPClient

SEHUATANG_HOST = 'www.sehuatang.net'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

FID = 103  # 高清中文字幕

REPLY_TIMES = os.getenv('REPLY_TIMES_98TANG', 1)

AUTO_REPLIES = (
    '感谢楼主精彩分享，资源很棒，收藏支持一下！',
    '这片子的画质和剧情都非常优秀，感谢分享！',
    '太给力了，福利满满，支持楼主继续更新！',
    '等了好久终于等到这部资源，开心！感谢！',
    '剧情紧凑，演员表现实在太棒了，必须支持！',
    '感谢大佬无私奉献，这片真的超级棒！',
    '封面和剧情一样精彩，感谢楼主搬运分享！',
    '看得我热血沸腾，楼主简直是资源之神！',
    '感谢楼主用心搬运，好资源必须支持！',
    '等这部片子很久了，终于让我等到了！',
    '演技出色，剧情耐看，封面也非常棒！',
    '收藏收藏，这资源真的太棒了，支持！',
    '感谢老板分享这么高质量的资源，超棒！',
    '封面非常吸引人，内容也相当精彩！',
    '剧情合理，演员表现也相当不错，点赞！',
    '画质清晰，剧情也挺带感，感谢楼主！',
    '福利满满，精彩十足，必须支持一下！',
    '这部片子真是让我欲罢不能，太赞了！',
    '剧情节奏非常舒服，演员表现到位！',
    '感谢楼主坚持分享，优质资源多多！',
    '这剧情设定太带感了，演员演技炸裂！',
    '太喜欢这类剧情了，感谢楼主分享！',
    '片源清晰，剧情饱满，值得收藏支持！',
    '资源真的特别棒，收藏点赞全给你！',
    '楼主搬运辛苦了，感谢提供好片！',
    '剧情太棒了，演技也很在线，顶！',
    '支持楼主无私奉献，片子真不错！',
    '这片子真的太良心了，感谢楼主！',
    '剧情细节很棒，演员演绎也自然！',
    '感谢楼主，画质剧情都非常优秀！',
    '收藏+点赞，期待楼主更多好资源！',
    '太刺激了，这剧情简直让我上头！',
    '感谢楼主高质量分享，太精彩了！',
    '剧情超出预期，演员表现很给力！',
    '感谢分享！这部片子我等了好久！',
    '剧情紧凑流畅，封面也相当诱惑！',
    '片子实在是太棒了，感谢楼主！',
    '福利多多，剧情也不拖沓，顶住！',
    '这剧情实在太顶了，演员也超棒！',
    '感谢楼主辛苦搬运，福利满满！',
    '画质清晰，剧情丰富，收藏！',
    '片子精彩，封面内容都相当棒！',
    '福利超赞，剧情也非常棒，点赞！',
    '感谢楼主辛苦整理，资源真棒！',
    '剧情很正，演技也很自然，棒！',
    '这资源真的强，感谢楼主无私！',
    '剧情内容饱满，画质清晰自然！',
    '感谢楼主福利资源，太棒了！',
    '收藏必备，剧情封面都非常棒！',
    '演员表现非常出彩，剧情流畅！',
    '太喜欢这类型了，感谢楼主！',
    '感谢楼主不定期更新，超棒！',
    '剧情好，画质棒，福利满满！',
    '剧情超赞，演员演技非常棒！',
    '收藏收藏，这片必须收藏！',
    '感谢楼主搬运高质量福利！',
    '画质和剧情都非常带感！',
    '剧情和演员都很棒，收藏！',
    '感谢楼主用心制作福利！',
    '剧情流畅，画质清晰，棒！',
    '片子相当精彩，福利超多！',
    '感谢楼主持续搬运好片！',
    '演技到位，剧情也非常棒！',
    '资源太棒了，楼主辛苦了！',
    '这片子剧情和福利都有！',
    '画质清晰，剧情紧凑！',
    '福利片中的精品，收藏！',
    '剧情合理，福利满分！',
    '感谢楼主高质量作品！',
    '剧情紧凑，封面好看！',
    '楼主资源质量一流！',
    '剧情满分，画质高清！',
    '感谢楼主精彩福利！',
    '剧情丰满，福利多多！',
    '演员出彩，剧情带劲！',
    '剧情饱满，封面吸引！',
    '演技自然，剧情舒服！',
    '剧情太赞，画质满分！',
    '资源清晰，福利满满！',
    '剧情好看，福利到位！',
    '楼主资源真是极品！',
    '剧情内容特别带感！',
    '演员演绎特别到位！',
    '感谢楼主好片分享！',
    '画质超清，剧情带劲！',
    '福利满满，剧情合理！',
    '收藏级别资源，棒！',
    '剧情到位，演员超棒！',
    '演技自然，剧情超棒！',
    '剧情扎实，福利充足！',
    '剧情精彩，封面带感！',
    '资源高清，剧情丰满！',
    '福利片的天花板啊！',
    '剧情和福利兼备！',
    '福利片之中的精品！',
    '剧情精彩，福利十足！',
    '剧情带感，演技自然！',
    '画质清晰，剧情在线！',
    '剧情丰富，福利满分！',
    '剧情紧凑，演技棒！',
    '福利精彩，剧情满分！',
    '剧情炸裂，演技爆表！',
    '资源超赞，剧情带劲！',
    '剧情舒服，福利多多！',
    '剧情和画质双优！',
    '剧情清晰，福利精彩！',
    '剧情流畅，画质超棒！',
    '剧情顶级，福利满分！',
    '剧情稳定，福利超值！',
    '福利充足，剧情不拖沓！',
    '剧情合理，封面诱人！',
    '剧情饱满，福利劲爆！',
    '剧情爆棚，画质高清！',
    '剧情细腻，福利满满！',
    '剧情感人，福利到位！',
    '剧情节奏好，福利棒！',
    '剧情特别，演技优秀！',
    '福利片中的战斗机！',
    '剧情满分，演技自然！',
    '剧情舒服，演出自然！',
    '福利超棒，剧情稳！',
    '剧情扎实，演技棒！',
    '剧情紧凑，演绎自然！',
    '剧情饱满，演技在线！',
    '剧情丰满，福利炸裂！',
    '福利给力，剧情不水！',
    '剧情流畅，演出自然！',
    '剧情不拖沓，福利强！',
    '剧情节奏好，演技佳！',
    '剧情满分，画质棒！',
    '福利超值，剧情满分！',
    '剧情合理，演员棒！',
    '剧情炸裂，福利劲爆！',
    '福利高能，剧情稳！',
    '福利高能，剧情紧凑！',
    '剧情精彩，福利满分！',
    '剧情走心，福利到位！',
    '剧情感人，演技自然！',
    '剧情不水，福利满分！',
    '福利片中的王者！',
    '剧情合理，演技好！',
    '剧情扎实，福利超多！',
    '剧情吸引人，福利棒！',
    '剧情爆棚，福利给力！',
    '剧情流畅，福利超值！',
    '福利超多，剧情也好！',
    '剧情顶级，福利充足！',
    '福利十足，剧情满分！',
    '剧情顶级，演技在线！',
    '福利满分，剧情扎实！',
    '剧情超棒，福利炸裂！',
    '福利超棒，剧情紧凑！',
    '剧情带劲，福利满分！',
    '福利到位，剧情精彩！',
    '福利丰富，剧情优秀！',
    '剧情充足，福利满满！',
    '福利劲爆，剧情满分！',
    '剧情稳定，福利满格！',
    '福利到位，剧情稳！',
)




def daysign(
    cookies: dict,
    flaresolverr_url: str = None,
    flaresolverr_proxy: str = None,
) -> bool:
    with (FlareSolverrHTTPClient(url=flaresolverr_url,
                                 proxy=flaresolverr_proxy,
                                 cookies=cookies,
                                 http2=True)
          if flaresolverr_url else httpx.Client(cookies=cookies, http2=True)) as client:

        @contextmanager
        def _request(method, url, *args, **kwargs):
            r = client.request(method=method, url=url,
                               headers={
                                   'user-agent': DEFAULT_USER_AGENT,
                                   'x-requested-with': 'XMLHttpRequest',
                                   'dnt': '1',
                                   'accept': '*/*',
                                   'sec-ch-ua-mobile': '?0',
                                   'sec-ch-ua-platform': 'macOS',
                                   'sec-fetch-site': 'same-origin',
                                   'sec-fetch-mode': 'cors',
                                   'sec-fetch-dest': 'empty',
                                   'referer': f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&mod=sign',
                                   'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                               }, *args, **kwargs)
            try:
                r.raise_for_status()
                yield r
            finally:
                r.close()

        age_confirmed = False
        age_retry_cnt = 3
        while not age_confirmed and age_retry_cnt > 0:
            with _request(method='get', url=f'https://{SEHUATANG_HOST}/') as r:
                if (v := re.findall(r"safeid='(\w+)'", r.text, re.MULTILINE | re.IGNORECASE)) and (safeid := v[0]):
                    print(f'set age confirm cookie: _safe={safeid}')
                    client.cookies.set(name='_safe', value=safeid)
                else:
                    age_confirmed = True
                age_retry_cnt -= 1

        if not age_confirmed:
            raise Exception('failed to pass age confirmation')

        with _request(method='get', url=f'https://{SEHUATANG_HOST}/forum.php?mod=forumdisplay&fid={FID}') as r:
            tids = re.findall(r"normalthread_(\d+)", r.text, re.MULTILINE | re.IGNORECASE)

        # Post comments to forums
        for _ in range(int(REPLY_TIMES)):
            tid = random.choice(tids)
            print(f'choose tid = {tid} to comment')

            with _request(method='get', url=f'https://{SEHUATANG_HOST}/forum.php?mod=viewthread&tid={tid}&extra=page%3D1') as r:
                soup = BeautifulSoup(r.text, 'html.parser')
                formhash = soup.find('input', {'name': 'formhash'})['value']

            message = random.choice(AUTO_REPLIES)

            with _request(method='post', url=f'https://{SEHUATANG_HOST}/forum.php?mod=post&action=reply&fid={FID}&tid={tid}&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1',
                          data={
                              'file': '',
                              'message': message,
                              'posttime': int(time.time()),
                              'formhash': formhash,
                              'usesig': '',
                              'subject': '',
                          }) as r:
                print(f'comment to: tid = {tid}, message = {message}')
                print(r.text)

            time.sleep(random.randint(16, 20))

        with _request(method='get', url=f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&mod=sign') as r:
            pass

        with _request(method='get', url=f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&ac=sign&infloat=yes&handlekey=pc_click_ddsign&inajax=1&ajaxtarget=fwin_content_pc_click_ddsign') as r:
            soup = BeautifulSoup(r.text, 'xml')
            html = soup.find('root').string
            root = BeautifulSoup(html, 'html.parser')
            id_hash = (root.find('span', id=re.compile(r'^secqaa_'))['id']).removeprefix('secqaa_')
            formhash = root.find('input', {'name': 'formhash'})['value']
            signtoken = root.find('input', {'name': 'signtoken'})['value']
            action = root.find('form', {'name': 'login'})['action']
            print(f'signform values: id_hash={id_hash}, formhash={formhash}, signtoken={signtoken}')
            print(f'action href: {action}')

        with _request(method='get', url=f'https://{SEHUATANG_HOST}/misc.php?mod=secqaa&action=update&idhash={id_hash}&{round(random.random(), 16)}') as r:
            qes_rsl = re.findall(r"'(.*?) = \?'", r.text, re.MULTILINE | re.IGNORECASE)

            if not qes_rsl or not qes_rsl[0]:
                raise Exception('invalid or empty question!')
            qes = qes_rsl[0]
            ans = eval(qes)
            print(f'verification question: {qes} = {ans}')
            assert type(ans) == int

        with _request(method='post', url=f'https://{SEHUATANG_HOST}/{action.lstrip("/")}&inajax=1',
                      data={'formhash': formhash, 'signtoken': signtoken, 'secqaahash': id_hash, 'secanswer': ans}) as r:
            return r.text


def retrieve_cookies_from_curl(env: str) -> dict:
    cURL = os.getenv(env, '').replace('\\', ' ')
    try:
        import uncurl
        return uncurl.parse_context(curl_command=cURL).cookies
    except ImportError:
        print("uncurl is required.")


def retrieve_cookies_from_fetch(env: str) -> dict:
    def parse_fetch(s: str) -> dict:
        ans = {}
        exec(s, {'fetch': lambda _, o: ans.update(o), 'null': None})
        return ans
    cookie_str = parse_fetch(os.getenv(env))['headers']['cookie']
    return dict(s.strip().split('=', maxsplit=1) for s in cookie_str.split(';'))


def preprocess_text(text) -> str:
    if 'xml' not in text:
        return text

    try:
        root = ET.fromstring(text)
        cdata = root.text
        soup = BeautifulSoup(cdata, 'html.parser')
        for script in soup.find_all('script'):
            script.decompose()
        return soup.get_text()
    except:
        return text


def push_notification(title: str, content: str) -> None:
    def telegram_send_message(text: str, chat_id: str, token: str, silent: bool = False) -> None:
        r = httpx.post(url=f'https://api.telegram.org/bot{token}/sendMessage',
                       json={'chat_id': chat_id, 'text': text, 'disable_notification': silent, 'disable_web_page_preview': True})
        r.raise_for_status()

    try:
        from notify import telegram_bot
        telegram_bot(title, content)
    except ImportError:
        chat_id = os.getenv('TG_USER_ID')
        bot_token = os.getenv('TG_BOT_TOKEN')
        if chat_id and bot_token:
            telegram_send_message(f'{title}\n\n{content}', chat_id, bot_token)


def main():
    # 定义多个账号的环境变量标识符列表
    account_env_vars = [
        ('FETCH_98TANG_1', 'CURL_98TANG_1'),
        ('FETCH_98TANG_2', 'CURL_98TANG_2'),
        ('FETCH_98TANG_3', 'CURL_98TANG_3'),
        # 可以继续添加更多账号
    ]

    # 循环处理每个账号
    for fetch_var, curl_var in account_env_vars:
        cookies = {}

        if os.getenv(fetch_var):
            cookies = retrieve_cookies_from_fetch(fetch_var)
        elif os.getenv(curl_var):
            cookies = retrieve_cookies_from_curl(curl_var)

        try:
            raw_html = daysign(
                cookies=cookies,
                flaresolverr_url=os.getenv('FLARESOLVERR_URL'),
                flaresolverr_proxy=os.getenv('FLARESOLVERR_PROXY'),
            )

            if '签到成功' in raw_html:
                title, message_text = '98堂 每日签到', re.findall(r"'(签到成功.+?)'", raw_html, re.MULTILINE)[0]
            elif '已经签到' in raw_html:
                title, message_text = '98堂 每日签到', re.findall(r"'(已经签到.+?)'", raw_html, re.MULTILINE)[0]
            elif '需要先登录' in raw_html:
                title, message_text = '98堂 签到异常', f'Cookie无效或已过期，请重新获取'
            else:
                title, message_text = '98堂 签到异常', raw_html
        except IndexError:
            title, message_text = '98堂 签到异常', f'正则匹配错误'
        except Exception as e:
            title, message_text = '98堂 签到异常', f'错误原因：{e}'
            # log detailed error message
            traceback.print_exc()

        # process message data
        message_text = preprocess_text(message_text)

        # log to output
        print(message_text)

        # telegram notify
        push_notification(title, message_text)


if __name__ == '__main__':
    main()
