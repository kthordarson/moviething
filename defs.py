# global definitions
import string
import re

imdb_regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")
#imdb_regex = re.compile(r"http(?:s)?://(?:www\.)?imdb\.com/title/tt\d{7}")
# imdb_regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/(tt\d{7})")
valid_nfo_files = ('nfo', 'xml', 'txt')


valid_input_string_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

mediainfo_tags = [
    'audio bit rate', 'audio bit rate mode', 'audio channel positions', 'audio channel(s)', 'audio channel(s)_original',
    'audio codec id', 'audio compression mode', 'audio duration', 'audio encoded date', 'audio format', 'audio format profile',
    'audio format/info', 'audio id', 'audio language', 'audio sampling rate', 'audio stream size', 'audio tagged date', 'video bit depth',
    'video bit rate', 'video bits/(pixel*frame)', 'video chroma subsampling', 'video codec id', 'video codec id/info', 'video color space',
    'video display aspect ratio', 'video duration', 'video encoded date', 'video encoding settings', 'video format', 'video format profile',
    'video format settings, cabac', 'video format settings, reframes', 'video format/info', 'video frame rate', 'video frame rate mode',
    'video height', 'video id', 'video scan type', 'video stream size', 'video tagged date', 'video width', 'video writing library',
    'format', 'id','format','format/info','format profile','format settings, cabac','format settings, reframes','codec id',
    'codec id/info','duration','bit rate','width','height','display aspect ratio','frame rate mode','frame rate','color space',
    'chroma subsampling','bit depth','scan type','bits/(pixel*frame)','stream size','writing library','encoded date','tagged date',
    ]
vid_extensions = (
    'mp4', 'mpeg', 'mpg', 'mp2', 'mpe', 'mvpv', 'mp4', 'm4p', 'm4v', 'mov', 'qt', 'avi', 'ts', 'mkv', 'wmv', 'ogv', 'webm', 'ogg'
)


min_filesize = 40000000

junkpathname = 'junkignore'
invalid_string = '.invalid'

# unwanted files / subdirs
# will be deleted automatically
unwanted_files = dict(
    subdirs=("sample", "samples"),
    txtfiles=("readme.txt", "torrent downloaded from.txt", "rarbg.com.txt", "torrent-downloaded-from-extratorrent.cc.txt",
              "ahashare.com.txt"),
    images=("www.yify-torrents.com.jpg", "screenshot", "www.yts.am.jpg"),
    videos=("rarbg.com.mp4", "sample")
)

