import configparser
import json

from requests import get

HEADERS_XML = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

HEADERS = {
    "Accept-Language" : "en-US,en;q=0.5",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
}

class TmdbScraper(object):
    # https://api.themoviedb.org/3/movie/<id>?api_key=<apikey>&language=en-US
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('tmdb.ini')
        self.themoviedbapikey = config['moviethingsettings']['themoviedbapikey']
        self.movie_data = None

    def request(self, tmdb_id):
        url = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=en-US' % (tmdb_id, self.themoviedbapikey)
        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US
        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78
        try:
            print(f'TmdbScraper: request to tmdb url: {url}')
            pagedata = get(url, headers=HEADERS_XML).content
            return json.loads(pagedata)
            # todo convert to xml https://github.com/nicklasb/py-json-lxml/blob/master/json_lxml.py
        except Exception as e:
            print(f'tmdb_scrape: err in get {e}')
            return None
    def parse_data(self, pagedata):
        # todo do stuff with data
        return pagedata

    def fetch_id(self, tmdb_id):
        self.movie_data = self.parse_data(self.request(tmdb_id))

if __name__ == '__main__':
    print('scraper_tmdb')
    # test_scraper = TmdbScraper()
    # test_scraper.fetch_id('tt0152930')
    # print(test_scraper.movie_data)
    # print(foo['title'])
    #[print(f't: {t} v: {foo[t]}') for t in foo]
    #tmdb_tags = [k for k in foo]
    #print(tmdb_tags)
