import hashlib
from io import BytesIO

from pytube import YouTube

with BytesIO() as tmp_file:
    YouTube("https://www.youtube.com/watch?v=ui7f4OQkMgU").streams.first().stream_to_buffer(tmp_file)

    # sha256 hash of the file
    tmp_file.seek(0)
    m = hashlib.sha256()
    m.update(tmp_file.getbuffer())

    video_hash = m.hexdigest()

print(video_hash)
