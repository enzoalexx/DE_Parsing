# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.


import requests
import json

url = 'https://cloud-api.yandex.net/v1/'
token = 'AgAAAAA99-93ABXfhDqmJBGWtk35kNEIyZVsR3M'
headers = {
    'Content-Type': 'application/json',
    'Authorization': token
}
disk_info = 'disk'
folder_info = 'disk/resources'
disk = requests.get(f'{url}{disk_info}')
disk.json()
disk = requests.get(f'{url}{disk_info}', headers=headers)
disk.json()
disk = requests.get(f'{url}{folder_info}?path=app:/', headers=headers)
for i in disk.json()['_embedded']['items']:
    print(i['name'])
with open('disk.json', 'w') as f:
    json.dump(disk.json(), f)
