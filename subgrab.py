import os
import re
import time
import hashlib
import requests
import platform
import sys
import codecs
import unidecode
from pathlib import Path

languages = {
    "en": "English",
}


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
        hash_result = hashlib.md5(data).hexdigest()
        print(f'{name} {size} {hash_result}')
    return hash_result


def request_subtitile(film_hash):

    url = "http://api.thesubdb.com/?action=search&hash={}".format(film_hash)
    header = {
        "user-agent": "SubDB/1.0 (SubGrabber/1.0; https://github.com/kthordarson/SubGrabber.git)"}
    req = requests.get(url, headers=header)
    print(f'http status {req.status_code}')
    if req.status_code == 200:
        sub_results = req.content.decode('utf-8')
        sub_langs = sub_results.split(",")
        print(f"Subtitles {sub_langs}")
        return True
    else:
        print(f"Error {req.status_code}")
        return False


def write_srt(data, file):
    filename = Path(file).with_suffix('.srt')
    with open(filename, 'wb') as f:
        f.write(data)
    f.close()
    print(f'Saved subtitle {filename}')


def thesubdb_grabber():
    files = []
    files.append(
        "d:/movies/Terminator.(1984).H264.Ita.Eng.Ac3.5.1.sub.ita.eng.[BaMax71].mkv")
    files.append("d:/movies/A Clockwork Orange 1971 720p BluRay x264 AC3 - Ozlem Hotpena/A Clockwork Orange 1971 720p BluRay x264 AC3 - Ozlem Hotpena.mp4")
    for file in files:
        film_hash = get_hash(name=file)
        if request_subtitile(film_hash):
            url = "http://api.thesubdb.com/?action=download&hash={}&language=en".format(
                film_hash)
            header = {
                "user-agent": "SubDB/1.0 (SubGrabber/1.0; https://github.com/kthordarson/SubGrabber.git)"}
            req = requests.get(url, headers=header)
            if req.status_code == 200:
                write_srt(req.content,  file)
            else:
                print(f"Error {req.status_code}")
