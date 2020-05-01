# global definitions
import string
import re
import os
import sys

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

mediacenter_tags = ['LocalTitle', 'OriginalTitle', 'ForcedTitle', 'IMDBrating', 'ProductionYear', 'MPAARating', 'Added', 'IMDB', 'IMDbId', 'RunningTime', 'TMDbId', 'Language', 'Country', 'Budget', 'Revenue', 'Persons', 'Genres', 'Description', 'Studios', 'Awards', 'BackdropURL', 'Director', 'FullCertifications', 'FormalMPAA', 'Votes', 'ShortDescription', 'Outline', 'Plot', 'PosterURL', 'TagLine', 'TagLines', 'Top250', 'TrailerURL', 'Website', 'WritersList', 'title', 'originaltitle', 'rating', 'votes', 'top250', 'year', 'plot', 'outline', 'tagline', 'mpaa', 'credits', 'director', 'playcount', 'id', 'tmdbid', 'set', 'sorttitle', 'trailer', 'watched', 'studio', 'genre', 'country', 'actor', 'fanart', 'fileinfo', 'runtime', 'thumb', 'alternativetitle', 'premiered', 'createdate', 'stars', 'language', 'dateadded', 'locked', 'SortTitle', 'CDUniverseId', 'Tagline', 'Taglines', 'Type', 'Synopsis', 'VideoAspect', 'VideoBitrate', 'VideoCodec', 'VideoCodecRaw', 'VideoFileSize', 'VideoHeight', 'VideoLength', 'VideoQuality', 'VideoWidth', 'AudioBitrate', 'AudioChannels', 'AudioCodec', 'AudioCodecRaw', 'AudioFrequency', 'AspectRatio', 'MediaInfo', 'VideoHasSubtitles', 'certification', 'filenameandpath']
kodi_tags =         ['title', 'originaltitle', 'sorttitle', 'rating', 'votes', 'year', 'plot', 'outline', 'tagline', 'runtime', 'mpaa', 'id', 'genre', 'country', 'studio', 'credits', 'director', 'trailer', 'actor', 'thumb', 'fanart', 'top250', 'playcount', 'tmdbid', 'set', 'watched', 'fileinfo', 'LocalTitle', 'OriginalTitle', 'ForcedTitle', 'IMDBrating', 'ProductionYear', 'MPAARating', 'Added', 'IMDB', 'IMDbId', 'RunningTime', 'TMDbId', 'Language', 'Country', 'Budget', 'Revenue', 'Persons', 'Genres', 'Description', 'Studios', 'Awards', 'BackdropURL', 'Director', 'FullCertifications', 'FormalMPAA', 'Votes', 'ShortDescription', 'Outline', 'Plot', 'PosterURL', 'TagLine', 'TagLines', 'Top250', 'TrailerURL', 'Website', 'WritersList', 'premiered', 'banner', 'discart', 'logo', 'clearart', 'landscape', 'extrathumb', 'extrafanart', 'certification', 'tmdbId', 'ids', 'producer', 'languages', 'source', 'imdb_link', 'alternativetitle', 'createdate', 'stars', 'language', 'dateadded', 'locked', 'lastplayed', 'tag', 'releasedate', 'Format', 'Duration', 'Encodeddate', 'Formatprofile', 'CodecID', 'Bitrate', 'Width', 'Height', 'Displayaspectratio', 'Frameratemode', 'Framerate', 'Colorspace', 'Chromasubsampling', 'Bitdepth', 'Scantype', 'Streamsize', 'Writinglibrary', 'filenameandpath', 'videosource', 'SortTitle', 'CDUniverseId', 'Tagline', 'Taglines', 'Type', 'Taggeddate', 'tmdb', 'tmdbcolid', 'uniqueid', 'datemodified']
vid_extensions = (
    '.mp4', '.mpeg', '.mpg', '.mp2', '.mpe', '.mvpv', '.mp4', '.m4p', '.m4v', '.mov', '.qt', '.avi', '.ts', '.mkv', '.wmv', '.ogv',
    '.webm', '.ogg'
)
all_extracted_tags = ['fileinfo', 'title', 'originaltitle', 'sorttitle', 'year', 'premiered', 'rating', 'votes', 'top250', 'outline', 'plot', 'tagline', 'country', 'fanart', 'runtime', 'mpaa', 'genre', 'credits', 'director', 'studio', 'trailer', 'playcount', 'createdate', 'stars', 'LocalTitle', 'OriginalTitle', 'ForcedTitle', 'IMDBrating', 'ProductionYear', 'MPAARating', 'Added', 'IMDB', 'IMDbId', 'RunningTime', 'TMDbId', 'Language', 'Country', 'Budget', 'Revenue', 'Persons', 'Genres', 'Description', 'Studios', 'Awards', 'BackdropURL', 'Director', 'FullCertifications', 'FormalMPAA', 'Votes', 'ShortDescription', 'Outline', 'Plot', 'PosterURL', 'TagLine', 'TagLines', 'Top250', 'TrailerURL', 'Website', 'WritersList', 'VideoAspect', 'VideoBitrate', 'VideoCodec', 'VideoCodecRaw', 'VideoFileSize', 'VideoHeight', 'VideoLength', 'VideoQuality', 'VideoWidth', 'AudioBitrate', 'AudioChannels', 'AudioCodec', 'AudioCodecRaw', 'AudioFrequency', 'AspectRatio', 'MediaInfo', 'VideoHasSubtitles', 'CDUniverseId', 'SortTitle', 'Synopsis', 'set', 'thumb', 'certification', 'id', 'ids', 'tmdbId', 'watched', 'tag', 'actor', 'producer', 'languages', 'tmdbid', 'banner', 'discart', 'logo', 'clearart', 'landscape', 'extrathumb', 'extrafanart', 'source', 'imdb_link', 'alternativetitle', 'language', 'dateadded', 'locked', 'lastplayed', 'releasedate', 'Format', 'Duration', 'Encodeddate', 'Formatprofile', 'CodecID', 'Bitrate', 'Width', 'Height', 'Displayaspectratio', 'Frameratemode', 'Framerate', 'Colorspace', 'Chromasubsampling', 'Bitdepth', 'Scantype', 'Streamsize', 'Writinglibrary', 'filenameandpath', 'videosource', 'Tagline', 'Taglines', 'Type', 'Taggeddate', 'tmdb', 'tmdbcolid', 'uniqueid', 'datemodified', 'Actors', 'ContentRating', 'FirstAired', 'Genre', 'IMDB_ID', 'Overview', 'Network', 'Rating', 'Runtime', 'SeriesID', 'SeriesName', 'Status', 'ID', 'EpisodeID', 'EpisodeName', 'EpisodeNumber', 'DVD_chapter', 'DVD_discid', 'DVD_episodenumber', 'DVD_season', 'GuestStars', 'ProductionCode', 'Writer', 'SeasonNumber', 'absolute_number', 'seasonid', 'seriesid', 'airsafter_season', 'airsbefore_episode', 'airsbefore_season', 'Combined_episodenumber', 'Combined_season', 'filename']

xml_type_list = ['movie', 'Title', 'Series', 'Item']

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