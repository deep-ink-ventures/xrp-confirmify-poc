from base64 import b64encode
from io import BytesIO

import requests
from pytube import YouTube

access_token = requests.post('http://localhost:8000/api/v1/auth/jwt/create/', json=dict(
    email='chp@deep-ink.ventures', password='testtest'
)).json()['access']

with BytesIO() as tmp_file:
    YouTube("https://www.youtube.com/watch?v=ui7f4OQkMgU").streams.first().stream_to_buffer(tmp_file)
    encoded = "data:video/3gpp;base64," + b64encode(tmp_file.getvalue()).decode()

    response = requests.post('http://localhost:8000/api/v1/contents/', json=dict(
        binary=encoded
    ), headers={
        'Authorization': f'Bearer {access_token}'
    })
    print(response.json())
