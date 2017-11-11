import asyncio
import threading
import time
from bilibiliClient import bilibiliClient


def test_thread(client):
    while True:
        time.sleep(3)
        data = b'{"cmd":"SPECIAL_GIFT","data":{"39":{"id":136368,"time":90,"hadJoin":0,"num":1,"content":"\xe5\x89\x8d\xe6\x96\xb9\xe9\xab\x98\xe8\x83\xbd\xe9\xa2\x84\xe8\xad\xa6\xef\xbc\x8c\xe6\xb3\xa8\xe6\x84\x8f\xe8\xbf\x99\xe4\xb8\x8d\xe6\x98\xaf\xe6\xbc\x94\xe4\xb9\xa0","action":"start"}}}'
        client.parseDanMu(data)


if __name__ == '__main__':
    bilibili_client = bilibiliClient(4153177)
    asyncio.ensure_future(bilibili_client.connectServer())
    asyncio.ensure_future(bilibili_client.HeartbeatLoop())
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try:
        test_t = threading.Thread(target=test_thread, args=(bilibili_client,))
        test_t.setDaemon(True)
        test_t.start()
        loop.run_forever()
    except:
        loop.close()
