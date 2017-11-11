import asyncio
import threading
import multiprocessing
from taskscreator import Taskcreator
from sender import SenderService

import logging.config

from get_hot_room_ids import get_room_ids

logging.config.fileConfig("logger.conf")


def start_catcher(page):
    room_ids = get_room_ids(page)
    upers = Taskcreator(rooms=room_ids)

    asyncio.ensure_future(upers.creating())

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try:
        loop.run_forever()
    except:
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.run_forever()

    loop.close()


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=4)
    for page in range(1, 5):
        pool.apply_async(start_catcher, (page,))
    pool.close()
    pool.join()
