import asyncio
from bilibiliClient import bilibiliClient

if __name__ == '__main__':
    bilibili_client = bilibiliClient(264)
    asyncio.ensure_future(bilibili_client.connectServer())
    asyncio.ensure_future(bilibili_client.HeartbeatLoop())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try:
        loop.run_forever()
    except:
        loop.close()
