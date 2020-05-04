# global definitions
import re
import string

# IMDB_REGEX = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")

IMDB_REGEX = re.compile(r'(http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/(tt\d{7}))')
MEDIAINFO_REGEX = re.compile(r'\[(\/)?mediainfo\]')  # (r'\[(\/)?mediainfo\]')
XML_TITLE_REGEX = re.compile(r'\<(?:OriginalTitle|title)\>(.+)\<')
XML_YEAR_REGEX = re.compile(r'\<(?:ProductionYear|year)\>(.+)\<')
XML_TAG_VALUE_REGEX = re.compile(r'\<(\w*)\>(.+)\<')
XML_TAG_REGEX = re.compile(r'\<(\w*)\>(?:.+)\<')

YEAR_REGEX = re.compile(r'((?:19[0-9]|20[012])[0-9])')
CODEC_REGEX = re.compile(r'XViD|XVID|xvid|Xvid|XviD|x264|h\\.?264')
QUALITY_REGEX = re.compile(r'((?:DVD|HD|B[Rr]|BD|WEB)[RrIiPp]{3}|[HP]DTV|H?D?CAM|[Bb]lu[Rr]ay|DVDSCR|WEB-DL)')
RESOLUTION_REGEX = re.compile(r'([0-9]{3,4}p)')

# regex_mi_2 = r'\[\/mediainfo\]'
# IMDB_REGEX = re.compile(r"http(?:s)?://(?:www\.)?imdb\.com/title/tt\d{7}")
# IMDB_REGEX = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/(tt\d{7})")
VALID_NFO_FILES = ('nfo', 'xml', 'txt')

VALID_INPUT_STRING_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)
VALID_TAG_CHARS = "-_.() :/%s%s" % (string.ascii_letters, string.digits)
VALID_XML_CHARS = "-_.()%s%s" % (string.ascii_letters, string.digits)
CHAR_LIMIT = 255
# fmt: off
MEDIAINFO_TAGS = [
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

MEDIACENTER_TAGS = ['LocalTitle', 'OriginalTitle', 'ForcedTitle', 'IMDBrating', 'ProductionYear', 'MPAARating', 'Added',
                    'IMDB', 'IMDbId', 'RunningTime', 'TMDbId', 'Language', 'Country', 'Budget', 'Revenue', 'Persons',
                    'Genres', 'Description', 'Studios', 'Awards', 'BackdropURL', 'Director', 'FullCertifications',
                    'FormalMPAA', 'Votes', 'ShortDescription', 'Outline', 'Plot', 'PosterURL', 'TagLine', 'TagLines',
                    'Top250', 'TrailerURL', 'Website', 'WritersList', 'title', 'originaltitle', 'rating', 'votes',
                    'top250', 'year', 'plot', 'outline', 'tagline', 'mpaa', 'credits', 'director', 'playcount', 'id',
                    'tmdbid', 'set', 'sorttitle', 'trailer', 'watched', 'studio', 'genre', 'country', 'actor', 'fanart',
                    'fileinfo', 'runtime', 'thumb', 'alternativetitle', 'premiered', 'createdate', 'stars', 'language',
                    'dateadded', 'locked', 'SortTitle', 'CDUniverseId', 'Tagline', 'Taglines', 'Type', 'Synopsis',
                    'VideoAspect', 'VideoBitrate', 'VideoCodec', 'VideoCodecRaw', 'VideoFileSize', 'VideoHeight',
                    'VideoLength', 'VideoQuality', 'VideoWidth', 'AudioBitrate', 'AudioChannels', 'AudioCodec',
                    'AudioCodecRaw', 'AudioFrequency', 'AspectRatio', 'MediaInfo', 'VideoHasSubtitles', 'certification',
                    'filenameandpath']
KODI_TAGS = ['title', 'originaltitle', 'sorttitle', 'rating', 'votes', 'year', 'plot', 'outline', 'tagline', 'runtime',
             'mpaa', 'id', 'genre', 'country', 'studio', 'credits', 'director', 'trailer', 'actor', 'thumb', 'fanart',
             'top250', 'playcount', 'tmdbid', 'set', 'watched', 'fileinfo', 'LocalTitle', 'OriginalTitle',
             'ForcedTitle', 'IMDBrating', 'ProductionYear', 'MPAARating', 'Added', 'IMDB', 'IMDbId', 'RunningTime',
             'TMDbId', 'Language', 'Country', 'Budget', 'Revenue', 'Persons', 'Genres', 'Description', 'Studios',
             'Awards', 'BackdropURL', 'Director', 'FullCertifications', 'FormalMPAA', 'Votes', 'ShortDescription',
             'Outline', 'Plot', 'PosterURL', 'TagLine', 'TagLines', 'Top250', 'TrailerURL', 'Website', 'WritersList',
             'premiered', 'banner', 'discart', 'logo', 'clearart', 'landscape', 'extrathumb', 'extrafanart',
             'certification', 'tmdbId', 'ids', 'producer', 'languages', 'source', 'imdb_link', 'alternativetitle',
             'createdate', 'stars', 'language', 'dateadded', 'locked', 'lastplayed', 'tag', 'releasedate', 'Format',
             'Duration', 'Encodeddate', 'Formatprofile', 'CodecID', 'Bitrate', 'Width', 'Height', 'Displayaspectratio',
             'Frameratemode', 'Framerate', 'Colorspace', 'Chromasubsampling', 'Bitdepth', 'Scantype', 'Streamsize',
             'Writinglibrary', 'filenameandpath', 'videosource', 'SortTitle', 'CDUniverseId', 'Tagline', 'Taglines',
             'Type', 'Taggeddate', 'tmdb', 'tmdbcolid', 'uniqueid', 'datemodified']

TMDB_TAGS = ['adult', 'backdrop_path', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id', 'imdb_id',
             'original_language', 'original_title', 'overview', 'popularity', 'poster_path', 'production_companies',
             'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'tagline',
             'title', 'video', 'vote_average', 'vote_count']

VID_EXTENSIONS = (
    '.mp4', '.mpeg', '.mpg', '.mp2', '.mpe', '.mvpv', '.mp4', '.m4p', '.m4v', '.mov', '.qt', '.avi', '.ts', '.mkv',
    '.wmv', '.ogv',
    '.webm', '.ogg'
)
ALL_EXTRACTED_TAGS = ['fileinfo', 'title', 'originaltitle', 'sorttitle', 'year', 'premiered', 'rating', 'votes',
                      'top250', 'outline', 'plot', 'tagline', 'country', 'fanart', 'runtime', 'mpaa', 'genre',
                      'credits', 'director', 'studio', 'trailer', 'playcount', 'createdate', 'stars', 'LocalTitle',
                      'OriginalTitle', 'ForcedTitle', 'IMDBrating', 'ProductionYear', 'MPAARating', 'Added', 'IMDB',
                      'IMDbId', 'RunningTime', 'TMDbId', 'Language', 'Country', 'Budget', 'Revenue', 'Persons',
                      'Genres', 'Description', 'Studios', 'Awards', 'BackdropURL', 'Director', 'FullCertifications',
                      'FormalMPAA', 'Votes', 'ShortDescription', 'Outline', 'Plot', 'PosterURL', 'TagLine', 'TagLines',
                      'Top250', 'TrailerURL', 'Website', 'WritersList', 'VideoAspect', 'VideoBitrate', 'VideoCodec',
                      'VideoCodecRaw', 'VideoFileSize', 'VideoHeight', 'VideoLength', 'VideoQuality', 'VideoWidth',
                      'AudioBitrate', 'AudioChannels', 'AudioCodec', 'AudioCodecRaw', 'AudioFrequency', 'AspectRatio',
                      'MediaInfo', 'VideoHasSubtitles', 'CDUniverseId', 'SortTitle', 'Synopsis', 'set', 'thumb',
                      'certification', 'id', 'ids', 'tmdbId', 'watched', 'tag', 'actor', 'producer', 'languages',
                      'tmdbid', 'banner', 'discart', 'logo', 'clearart', 'landscape', 'extrathumb', 'extrafanart',
                      'source', 'imdb_link', 'alternativetitle', 'language', 'dateadded', 'locked', 'lastplayed',
                      'releasedate', 'Format', 'Duration', 'Encodeddate', 'Formatprofile', 'CodecID', 'Bitrate',
                      'Width', 'Height', 'Displayaspectratio', 'Frameratemode', 'Framerate', 'Colorspace',
                      'Chromasubsampling', 'Bitdepth', 'Scantype', 'Streamsize', 'Writinglibrary', 'filenameandpath',
                      'videosource', 'Tagline', 'Taglines', 'Type', 'Taggeddate', 'tmdb', 'tmdbcolid', 'uniqueid',
                      'datemodified', 'Actors', 'ContentRating', 'FirstAired', 'Genre', 'IMDB_ID', 'Overview',
                      'Network', 'Rating', 'Runtime', 'SeriesID', 'SeriesName', 'Status', 'ID', 'EpisodeID',
                      'EpisodeName', 'EpisodeNumber', 'DVD_chapter', 'DVD_discid', 'DVD_episodenumber', 'DVD_season',
                      'GuestStars', 'ProductionCode', 'Writer', 'SeasonNumber', 'absolute_number', 'seasonid',
                      'seriesid', 'airsafter_season', 'airsbefore_episode', 'airsbefore_season',
                      'Combined_episodenumber', 'Combined_season', 'filename', 'adult', 'backdrop_path',
                      'belongs_to_collection', 'budget', 'genres', 'homepage', 'id', 'imdb_id', 'original_language',
                      'original_title', 'overview', 'popularity', 'poster_path', 'production_companies', 'production_countries',
                      'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'tagline', 'title', 'video', 'vote_average', 'vote_count']

XML_TYPE_LIST = ['movie', 'Title', 'Series', 'Item', 'ffprobe']

MIN_FILESIZE = 40000000

JUNKPATHNAME = 'junkignore'
INVALID_STRING = '.invalid'

# unwanted files / subdirs
# will be deleted automatically
UNWANTED_FILES = dict(
    subdirs=("sample", "samples"),
    txtfiles=(
        "readme.txt", "torrent downloaded from.txt", "rarbg.com.txt", "torrent-downloaded-from-extratorrent.cc.txt",
        "ahashare.com.txt"),
    images=("www.yify-torrents.com.jpg", "screenshot", "www.yts.am.jpg"),
    videos=("rarbg.com.mp4", "sample")
)
# fmt: on
if __name__ == '__main__':
    print('defs')
