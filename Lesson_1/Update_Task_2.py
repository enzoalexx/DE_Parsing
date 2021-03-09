# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.


import requests
import json

url = 'https://api.themoviedb.org/3/movie/'
movie_id = '76341'
headers = {'content-Type': 'application/json;charset=utf-8',
           'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwZDI5ZGUyM2NlOWZhMjZiMjhhNTg1MzMzNjZmOWNiYSIsInN1YiI6IjYwNDc0MmNjNmNmM2Q1MDA0NjE4NGNkMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.qtcwUpYl7BFd6Ik99pN57YUoubJvI-_nxxAgrhFT2JE'
           }
params = {'language': 'en', 'genre_ids': '[18]'}
req = requests.get(f'{url}{movie_id}', headers=headers)
print(req.ok)
print('Заголовки: \n',  req.headers)
print('Ответ: \n',  req.text)
url_2 = 'https://api.themoviedb.org/3/list/'
list_id = '124'
original_language = 'en'
req_2 = requests.get(f'{url_2}{list_id}', params=params, headers=headers)
print('Ответ: \n',  req_2.text)
with open('req_2.json', 'w') as f:
    json.dump(req_2.json(), f)
