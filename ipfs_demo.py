import json
from io import StringIO

import requests

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweDJmRjJFQWQwN2VENTYzY0FCY0I2OTM3MTM3NGJBYTFGNzEzMjYzQTAiLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY4NTcwODIzMDMwOSwibmFtZSI6IkRlbW8ifQ.Kz5OJga-Eg6YoHueWY5nWYLeETJUD6r6YLrxfoaE610"

meta_file = StringIO()
meta_file.write(json.dumps({
    "original_url": "https://www.youtube.com/watch?v=ui7f4OQkMgU",
    "issuer": "HBO Succession",
    "issuer_id": "HBO",
    "content_type": "video",
    "checksum": "7481a2a9f008eafd2a53b9844d782d77b3e1249f67d40ed85b376060bb9a2854"
}))
meta_file.seek(0)

response = requests.post(
    'https://api.nft.storage/upload',
    headers={
        "Authorization": f"Bearer {API_KEY}"
    },
    data=meta_file.getvalue()
)

url = f"https://{response.json()['value']['cid']}.ipfs.nftstorage.link/"
print(url)