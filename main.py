import asyncio
import threading

from taskscreator import Taskcreator
from sender import SenderService

import logging.config

from get_hot_room_ids import get_room_ids

logging.config.fileConfig("logger.conf")

if __name__ == '__main__':
    lock = threading.Lock()

    room_ids = []
    for page in range(1, 6):
        room_ids += get_room_ids(page)
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
