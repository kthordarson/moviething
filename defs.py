# global definitions
import string
import re
import os
import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# imdb_regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")

imdb_regex = re.compile(r'(http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/(tt\d{7}))')
mediainfo_regex = re.compile(r'\[(\/)?mediainfo\]')  # (r'\[(\/)?mediainfo\]')
xml_title_regex = re.compile(r'\<(?:OriginalTitle|title)\>(.+)\<')
xml_year_regex = re.compile(r'\<(?:ProductionYear|year)\>(.+)\<')
xml_tag_value_regex = re.compile(r'\<(\w*)\>(.+)\<')
xml_tag_regex = re.compile(r'\<(\w*)\>(?:.+)\<')

# regex_mi_2 = r'\[\/mediainfo\]'
# imdb_regex = re.compile(r"http(?:s)?://(?:www\.)?imdb\.com/title/tt\d{7}")
# imdb_regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/(tt\d{7})")
valid_nfo_files = ('nfo', 'xml', 'txt')

valid_input_string_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
valid_tag_chars = "-_.() :/%s%s" % (string.ascii_letters, string.digits)
valid_xml_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
char_limit = 255

mediainfo_tags = [
    'aspect', 'audio bit rate', 'audio bit rate mode', 'audio channel positions', 'audio channel(s)',
    'audio channel(s)_original',
    'audio codec id', 'audio compression mode', 'audio duration', 'audio encoded date', 'audio format',
    'audio format profile',
    'audio format/info', 'audio id', 'audio language', 'audio sampling rate', 'audio stream size', 'audio tagged date',
    'bit depth',
    'bit rate', 'bits/(pixel*frame)', 'certification', 'channels', 'chroma subsampling', 'codec', 'codec id',
    'codec id/info',
    'color space', 'container', 'country', 'credits', 'director', 'display aspect ratio', 'download', 'duration',
    'durationinseconds',
    'encoded date', 'filename', 'format', 'format profile', 'format settings, cabac', 'format settings, reframes',
    'format/info',
    'frame rate', 'frame rate mode', 'genre', 'height', 'imdb information', 'imdb link', 'imdb score', 'key',
    'language',
    'languages', 'length', 'link', 'md5', 'mpaa', 'name', 'originaltitle', 'outline', 'playcount', 'plot', 'premiered',
    'rating',
    'role', 'runtime', 'sample included', 'scan type', 'size', 'source', 'stream size', 'studio', 'tagged date',
    'tagline', 'thumb',
    'title', 'tmdbId', 'total bitrate', 'type', 'video bit depth', 'video bit rate', 'video bits/(pixel*frame)',
    'video chroma subsampling', 'video codec id', 'video codec id/info', 'video color space',
    'video display aspect ratio',
    'video duration', 'video encoded date', 'video encoding settings', 'video format', 'video format profile',
    'video format settings, cabac', 'video format settings, reframes', 'video format/info', 'video frame rate',
    'video frame rate mode', 'video height', 'video id', 'video scan type', 'video stream size', 'video tagged date',
    'video width', 'video writing library', 'votes', 'watched', 'width', 'writing library', 'year'
]

vid_extensions = (
    '.mp4', '.mpeg', '.mpg', '.mp2', '.mpe', '.mvpv', '.mp4', '.m4p', '.m4v', '.mov', '.qt', '.avi', '.ts', '.mkv', '.wmv', '.ogv',
    '.webm', '.ogg'
)

min_filesize = 40000000

junkpathname = 'junkignore'
invalid_string = '.invalid'

# unwanted files / subdirs
# will be deleted automatically
unwanted_files = dict(
    subdirs=("sample", "samples"),
    txtfiles=(
        "readme.txt", "torrent downloaded from.txt", "rarbg.com.txt", "torrent-downloaded-from-extratorrent.cc.txt",
        "ahashare.com.txt"),
    images=("www.yify-torrents.com.jpg", "screenshot", "www.yts.am.jpg"),
    videos=("rarbg.com.mp4", "sample")
)

if __name__ == '__main__':
    print('defs')