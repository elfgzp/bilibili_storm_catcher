import logging
import aiohttp
import asyncio
from http import cookies
from pybililive.handler import danmmu_msg
from pybililive.consts import (
    LIVE_BASE_URL, SEND_DANMU_URI
)
logger = logging.getLogger('bili')


def build_cookie_with_str(cookie_str):
    simple_cookie = cookies.SimpleCookie(cookie_str)  # Parse Cookie from str
    cookie = {key: morsel.value for key, morsel in simple_cookie.items()}
    return cookie


cookie_str = 'sid=d24ub4gg; fts=1503276824; UM_distinctid=15e09e01b98495-0598b3da3e60dc-31627c01-13c680-15e09e01b99c60; rpdid=kwmooqmqlkdoswpislpxw; LIVE_BUVID=6d50208d52bbd75e052fea6895db682d; LIVE_BUVID__ckMd5=c3e520c2fbe55044; biliMzIsnew=1; biliMzTs=0; Hm_lvt_ff57561a8cad2056ebeb8790418f7c80=1505378377; __guid=136533283.2349724059770041300.1506006783656.525; buvid3=236A760C-90D4-45DE-ADA9-EBC1909C0AB11984infoc; im_seqno_2459271=2035; finger=14bc3c4e; Hm_lvt_8a6d461cf92ec46bd14513876885e489=1509712825,1509855250,1510034539,1510460734; DedeUserID=2459271; DedeUserID__ckMd5=3c272ac53b78f4fc; SESSDATA=5b1c4482%2C1513171920%2C25da359b; bili_jct=c2ecf18cf6f5fb354af88839b6ce26f9; F_S_T_2459271=1; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1510406674,1510410659,1510579907,1510579912; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1510579928'

danmu_url = r'http://{host}:{port}/{uri}'.format(
    host=LIVE_BASE_URL,
    port=80,
    uri=SEND_DANMU_URI
)

user_cookies = build_cookie_with_str(cookie_str)


async def send_danmu(danmu, room_id, color="000000", font_size='11', mode='1'):
    try:
        res = await aiohttp.request(
            'POST', danmu_url,
            data={
                'msg': danmu,
                'color': color,
                'fontsize': font_size,
                'roomid': room_id,
                'mode': mode
            },
            cookies=user_cookies
        )

        data = await res.json()
        if data['msg']:
            raise Exception(data['msg'])

    except Exception as e:
        logger.exception(e)
        logger.error('房间{} 弹幕 {} 发送失败'.format(room_id, danmu))
    else:
        logger.info('房间{}  弹幕 {} 发送成功'.format(room_id, danmu))
    finally:
        return


async def special_gift(live_obj, message):
    try:
        content = message['data'].get('39', {}).get('content')
        if content:
            await send_danmu(content, room_id=live_obj.room_id)
            logging.info('参与房间 {} 节奏风暴'.format(live_obj.room_id))
    except Exception as e:
        logging.exception(e)


async def sys_gift(live_obj, message):
    try:

        if message.get('giftId') == 39:
            res = await aiohttp.request(
                'GET',
                r'http://api.live.bilibili.com/SpecialGift/room/{}'.format(message['roomid'])
            )
            data = await res.json()
            content = data['data'].get('gift39', {}).get('content')
            if content:
                await send_danmu(content, room_id=message['roomid'])
                logging.info('参与房间 {} 节奏风暴'.format(live_obj.room_id))
    except Exception as e:
        logging.exception(e)


async def check_special_gift(live_obj, message):
    try:
        content = message['data'].get('39', {}).get('content')
        if content:
            live_obj.set_cmd_func('DANMU_MSG', danmmu_msg)
            await asyncio.sleep(5)
            live_obj.set_cmd_func('DANMU_MSG', None)
    except Exception as e:
        logging.exception(e)


async def check_sys_gift(live_obj, message):
    try:

        if message.get('giftId') == 39:
            res = await aiohttp.request(
                'GET',
                r'http://api.live.bilibili.com/SpecialGift/room/{}'.format(message['roomid'])
            )
            data = await res.json()
            content = data['data'].get('gift39', {}).get('content')
            if content:
                live_obj.set_cmd_func('DANMU_MSG', danmmu_msg)
                await asyncio.sleep(5)
                live_obj.set_cmd_func('DANMU_MSG', None)
    except Exception as e:
        logging.exception(e)


cmd_func = {
    'SPECIAL_GIFT': special_gift,
    'SYS_GIFT': sys_gift,
    # 'DANMU_MSG': danmmu_msg
}
