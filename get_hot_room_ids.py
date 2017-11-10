import requests
import json


def get_room_ids(page):
    url = 'http://api.live.bilibili.com/area/liveList'
    response = requests.get(url, params={'area': 'all', 'order': 'online', 'page': page})
    data = json.loads(response.content)
    room_ids = []
    if data['code'] == 0:
        room_ids = [each['roomid'] for each in data['data']]
    return room_ids
