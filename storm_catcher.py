import multiprocessing
from taskscreator import Taskcreator
import asyncio
import logging.config
from get_hot_room_ids import get_room_ids

logging.config.fileConfig("logger.conf")


def start_catcher(page):
    room_ids = get_room_ids(page)
    creator = Taskcreator(rooms=room_ids)

    asyncio.ensure_future(creator.creating())

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try:
        loop.run_forever()
    except Exception as e:
        logging.exception(e)
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.run_forever()

    loop.close()


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=5)
    for page in range(1, 6):
        pool.apply_async(start_catcher, (page,))
    pool.close()
    pool.join()



    # room_ids = []
    # for page in range(1, 11):
    #     room_ids += get_room_ids(page)
    # creator = Taskcreator(rooms=room_ids)
    #
    # asyncio.ensure_future(creator.creating())
    #
    # loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    # try:
    #     loop.run_forever()
    # except Exception as e:
    #     logging.exception(e)
    #     for task in asyncio.Task.all_tasks():
    #         task.cancel()
    #     loop.run_forever()
    #
    # loop.close()
