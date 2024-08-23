import requests

url: str = 'http://127.0.0.1:13500/api/users/add'
data: dict = {
    "fullname": "John_Doe",
    "username": "johndoe"
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())

url: str = 'http://127.0.0.1:13500/api/users/del'
data: dict = {
    "username": "johndoe"
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())
