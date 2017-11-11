import asyncio
import aiohttp
import random
from struct import *
import json
import requests
import logging
from sender import SenderService

logger = logging.getLogger('bili')


class bilibiliClient():
    __slots__ = ['_roomId', '_ChatPort', '_protocolversion', '_reader', '_writer', 'connected', '_UserCount',
                 '_ChatHost', '_sender', '_uid', 'log_danmaku', 'log_danmaku_count']

    def __init__(self, room_id):
        self._roomId = room_id
        self._ChatPort = 788
        self._uid = 0
        self._protocolversion = 1
        self._reader = 0
        self._writer = 0
        self.connected = False
        self._UserCount = 0
        self._ChatHost = 'livecmt-1.bilibili.com'
        self._sender = SenderService(room_id)
        self.log_danmaku = False
        self.log_danmaku_count = 0

    async def connectServer(self):
        # print('正在进入房间。。。。。')
        try:
            with aiohttp.ClientSession() as s:
                async with s.get('http://api.live.bilibili.com/room/v1/Room/room_init?id=' + str(self._roomId)) as r:
                    json_str = await r.text()
                    data = json.loads(json_str)
                    ROOMID = data['data']['room_id']
                self._roomId = int(ROOMID)
        except:
            return

        reader, writer = await asyncio.open_connection(self._ChatHost, self._ChatPort)
        self._reader = reader
        self._writer = writer
        # print('链接弹幕中。。。。。')
        if await self.SendJoinChannel(self._roomId):
            self.connected = True
            print('进入房间成功。。。。。%s' % self._roomId)
            try:
                await self.ReceiveMessageLoop()
            except:  # 发生异常直接退出该 task
                return

    async def HeartbeatLoop(self):
        while not self.connected:
            await asyncio.sleep(0.5)

        while self.connected:
            await self.SendSocketData(0, 16, self._protocolversion, 2, 1, "")
            await asyncio.sleep(30)

    async def SendJoinChannel(self, channelId):
        self._uid = (int)(100000000000000.0 + 200000000000000.0 * random.random())
        body = '{"roomid":%s,"uid":%s}' % (channelId, self._uid)
        await self.SendSocketData(0, 16, self._protocolversion, 7, 1, body)
        return True

    async def SendSocketData(self, packetlength, magic, ver, action, param, body):
        bytearr = body.encode('utf-8')
        if packetlength == 0:
            packetlength = len(bytearr) + 16
        sendbytes = pack('!IHHII', packetlength, magic, ver, action, param)
        if len(bytearr) != 0:
            sendbytes = sendbytes + bytearr
        self._writer.write(sendbytes)
        await self._writer.drain()

    async def ReceiveMessageLoop(self):
        while self.connected == True:
            tmp = await self._reader.read(4)
            expr, = unpack('!I', tmp)
            tmp = await self._reader.read(2)
            tmp = await self._reader.read(2)
            tmp = await self._reader.read(4)
            num, = unpack('!I', tmp)
            tmp = await self._reader.read(4)
            num2 = expr - 16

            if num2 != 0:
                num -= 1
                if num == 0 or num == 1 or num == 2:
                    tmp = await self._reader.read(4)
                    num3, = unpack('!I', tmp)
                    # print('直播间号%s房间人数为 %s' % (self._roomId, num3))
                    self._UserCount = num3
                    continue
                elif num == 3 or num == 4:
                    tmp = await self._reader.read(num2)
                    # strbytes, = unpack('!s', tmp)
                    try:  # 为什么还会出现 utf-8 decode error??????
                        messages = tmp.decode('utf-8')
                    except:
                        continue
                    self.parseDanMu(messages)
                    continue
                elif num == 5 or num == 6 or num == 7:
                    tmp = await self._reader.read(num2)
                    continue
                else:
                    if num != 16:
                        tmp = await self._reader.read(num2)
                    else:
                        continue

    def parseDanMu(self, messages):
        try:
            dic = json.loads(messages)
        except Exception as e:  # 有些情况会 jsondecode 失败，未细究，可能平台导致
            pass
        else:
            cmd = dic['cmd']
            if cmd == 'SYS_GIFT':

                try:
                    if dic.get('giftId') == 39:
                        response = requests.get('http://api.live.bilibili.com/SpecialGift/room/%s' % dic['roomid'])
                        json_str = response.content.decode('utf-8')
                        data = json.loads(json_str)
                        content = data.get('gift39', {}).get('content')
                        if content:
                            self._sender.send_a_danmaku(content)
                            self.log_danmaku = True
                            logging.info('SPECIAL_GIFT room {}'.format(self._roomId))
                            logging.info(messages)
                            logging.info('参与{}节奏风暴抽奖'.format(self._roomId))
                            logging.info('Storm room {}'.format(self._roomId))
                except Exception as e:
                    logging.exception(e)

                return

            if cmd == 'SPECIAL_GIFT':
                try:
                    content = dic['data'].get('39', {}).get('content')
                    if content:
                        self._sender.send_a_danmaku(content)
                        self.log_danmaku = True
                        logging.info('SYS_GIFT room {}'.format(self._roomId))
                        logging.info(messages)
                        logging.info('参与{}节奏风暴抽奖'.format(self._roomId))
                        logging.info('Storm room {}'.format(self._roomId))
                except Exception as e:
                    logging.exception(e)

                return
            # if cmd == 'DANMU_MSG' and dic['info'][2][0] == 2459271:
            if cmd == 'DANMU_MSG':
                commentText = dic['info'][1]
                commentUser = dic['info'][2][1]
                isAdmin = dic['info'][2][2] == '1'
                isVIP = dic['info'][2][3] == '1'
                if isAdmin:
                    commentUser = '管理员 ' + commentUser
                if isVIP:
                    commentUser = 'VIP ' + commentUser
                try:
                    print('房间:' + str(self._roomId) + commentUser + ' say: ' + commentText)
                except:
                    pass

                self.log_danmaku_count += 1

                if self.log_danmaku_count >= 10:
                    self.log_danmaku = False
                    self.log_danmaku_count = 0
                return
