# -*- coding: utf-8 -*-

import time
import requests
import os
import http.cookies as Cookie
import http.cookiejar as cookielib
import urllib.request as urllib2

from configs.global_settings import (
    LOGIN_HEADER,
    SEND_URL
)
from configs.personal_settings import SEND_FORMAT


class SenderService(object):
    """提供弹幕发送服务。
    """
    __slots__ = ['room_id', 'session', 'cookie', 'opener', 'login_header']

    def __init__(self, room_id):
        """初始化服务。
        :params: room_id: 直播间号。
        """
        self.room_id = room_id
        self.login_header = ''
        self.session = requests.Session()
        # 设置cookie
        self.cookie = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(
            cookie_handler, urllib2.HTTPHandler)
        self.do_login()

    def set_room_id(self, room_id):
        self.room_id = room_id

    def _try_login_with_file_cookie(self):
        if os.path.exists('cookie.data'):
            cookie = cookielib.MozillaCookieJar()
            cookie.load('cookie.data', ignore_discard=True, ignore_expires=True)
            self.cookie = cookie
            self.opener = self._build_opener()
            return self._check_login()
        else:
            return False

    def do_login(self):
        # 载入登陆设置
        self._pre_login()
        # 获取 登陆必要参数
        if not self._try_login_with_file_cookie():
            while 1:
                cookie = input('请输入cookie:')
                # 进行登录
                if not self._login(cookie):
                    continue
                else:
                    break

    def _pre_login(self):
        """进行登录前信息配置信息。"""
        # 将页面信息加入头部
        self.login_header = LOGIN_HEADER
        for i in self.cookie:
            self.login_header['Cookie'] = i.name + '=' + i.value

    def _build_opener_with_cookie_str(self, cookie_str, domain='', path='/'):
        simple_cookie = Cookie.SimpleCookie(cookie_str)  # Parse Cookie from str
        cookiejar = cookielib.MozillaCookieJar('cookie.data')  # No cookies stored yet

        for c in simple_cookie:
            cookie_item = cookielib.Cookie(
                version=0, name=c, value=str(simple_cookie[c].value),
                port=None, port_specified=None,
                domain=domain, domain_specified=None, domain_initial_dot=None,
                path=path, path_specified=None,
                secure=None,
                expires=None,
                discard=None,
                comment=None,
                comment_url=None,
                rest=None,
                rfc2109=False,
            )
            cookiejar.set_cookie(cookie_item)
        cookiejar.save(ignore_discard=True, ignore_expires=True)
        return cookiejar

    def _build_opener(self):
        return urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))

    def _login(self, cookie):
        """登陆操作。

        :params: user_id: 用户账户或邮箱。
        :params: password: 密码。
        """
        self.cookie = self._build_opener_with_cookie_str(cookie)
        self.opener = self._build_opener()

        return self._check_login()

    def _check_login(self):
        result = self.opener.open('http://live.bilibili.com/User/getUserInfo')
        if result.msg == 'OK':
            return True
        else:
            print(u'登录失败')
            return False

    def send_a_danmaku(self, danmaku):
        """发送一条弹幕。
        :params: room_id: 直播间号。
        :params: danmaku: 弹幕信息。
        """

        data = SEND_FORMAT
        data["msg"] = danmaku
        data["roomid"] = self.room_id
        data["rnd"] = time.time() * 1000
        response = self.session.post(
            SEND_URL,
            data=data,
            cookies=self.cookie
        )
        response.raise_for_status()
        if response.json().get('code') == 0:
            print("弹幕{}已发出".format(danmaku))
        else:
            print(response.json().get('msg'))
        return True
