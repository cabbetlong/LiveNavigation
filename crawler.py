import asyncio
import re
from urllib.parse import urlparse

import aiohttp
from Dict2Class import Dict2Class
from config import *


def douyu(html):
    room_name = re.search('roomName:\s"(.*?)"', html, re.S).group(1)
    is_live = re.search('isLive:\s(\d+),', html, re.S).group(1)
    return room_name, int(is_live)


def panda(json_html):
    json_obj = Dict2Class(json_html)
    return json_obj.data.roominfo.name, json_obj.data.videoinfo.address


def huya(html):
    room_name = re.search('<h1\sid="J_roomTitle">(.*?)</h1>', html, re.S).group(1)
    return room_name, '上次' not in html


def init_url_func(origin_url):
    url_obj = urlparse(origin_url)
    for base_url in BASE_URLS:
        end_index = url_obj.netloc.rfind('.')
        domain = url_obj.netloc[4:end_index]
        if domain in base_url:
            return base_url.format(room=url_obj.path[1:]), eval(domain)


class Live:

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self._direct_url, self._parse = init_url_func(url)
        self.room_name, self.is_live = '', 0

    async def get_live_status(self):
        if not self._parse:
            print("Couldn't find parse function for this live site!")
            return '', False
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(self._direct_url) as r:
                        if r.status == 200:
                            html = await r.json()
                        else:
                            return '', False
                except aiohttp.client_exceptions.ClientResponseError:  # 先以json格式解析，若失败则以text解析
                    html = await r.text()
                except aiohttp.ClientError as e:
                    print(e)
                    return '', False
        except aiohttp.ClientError as e:
            print(e)
            return '', False

        parse_result = self._parse(html)
        if parse_result:
            self.room_name, self.is_live = parse_result


def get_lives():
    for name, origin_url in LIVES.items():
        yield Live(name, origin_url)


def live_urls():
    # 异步获取直播结果
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    lives = list(get_lives())
    to_do = [live.get_live_status() for live in lives]
    wait_coro = asyncio.wait(to_do)
    loop.run_until_complete(wait_coro)
    loop.close()

    return lives


if __name__ == '__main__':
    live_urls()
