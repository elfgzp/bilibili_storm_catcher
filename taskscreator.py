import asyncio
from bilibiliClient import bilibiliClient

import logging

logger = logging.getLogger('bili')


class Taskcreator(object):
    __slots__ = ['tasks', 'urls']

    def __init__(self, rooms):
        self.tasks = {}
        self.urls = []
        for room in rooms:
            self.urls.append(room)

    async def creating(self):
        for url in self.urls:
            danmuji = bilibiliClient(url)
            task1 = asyncio.ensure_future(danmuji.connectServer())
            task2 = asyncio.ensure_future(danmuji.HeartbeatLoop())
            self.tasks[url] = [task1, task2]
            await asyncio.sleep(0.2)

        while True:
            await asyncio.sleep(10)
            for url in self.tasks:
                item = self.tasks[url]
                task1 = item[0]
                task2 = item[1]
                if task1.done() == True or task2.done() == True:
                    if task1.done() == False:
                        task1.cancel()
                    if task2.done() == False:
                        task2.cancel()
                    print('重新进入直播间 %s' % url)
                    logging.debug('reenter %s' % url)
                    danmuji = bilibiliClient(url)
                    task11 = asyncio.ensure_future(danmuji.connectServer())
                    task22 = asyncio.ensure_future(danmuji.HeartbeatLoop())
                    self.tasks[url] = [task11, task22]
            print('len: %s' % len(self.tasks))
            logging.debug('len: %s' % len(self.tasks))
            print('now there is %s' % len(asyncio.Task.all_tasks()))
            logging.debug('now there is %s' % len(asyncio.Task.all_tasks()))
