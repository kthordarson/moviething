import configparser
import json

from requests import get

HEADERS_XML = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
}


class TmdbScraper(object):
    # https://api.themoviedb.org/3/movie/<id>?api_key=<apikey>&language=en-US
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('tmdb.ini')
        self.themoviedbapikey = config['moviethingsettings']['themoviedbapikey']
        self.movie_data = None

    def request_id(self, tmdb_id):
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
        self.movie_data = self.parse_data(self.request_id(tmdb_id))

    def search(self, query, year):
        result = None
        # https://api.themoviedb.org/3/search/movie?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US&query=Princess%20Mononoke&page=1&include_adult=false&year=1997

        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US
        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78
        try:
            query = query.replace(' ', '%20')
            url = 'https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1&include_adult=false&year=%s' % (
                self.themoviedbapikey, query, year)
            print(f'TmdbScraper: search {query} {year}')
            print(f'TmdbScraper: request to tmdb url: {url}')
            pagedata = get(url, headers=HEADERS_XML).content
            return json.loads(pagedata)
            # todo convert to xml https://github.com/nicklasb/py-json-lxml/blob/master/json_lxml.py
        except Exception as e:
            print(f'tmdb_scrape: err in get {e}')
            return None
        return result


if __name__ == '__main__':
    print('scraper_tmdb')
    with open('apitest2.json', 'r') as f:
        jsonraw = f.read()
    jsondata = json.loads(jsonraw)
    for res in jsondata['results']:
        print(f'Title: {res["title"]}')
        print(f'\tID: {res["id"]}')
        print(f'\tDate: {res["release_date"]}')
        print(f'\tOverview: {res["overview"]}')
    # test_scraper = TmdbScraper()
    # search = test_scraper.search(query='The Witch', year='2015')  # The Witch (2015)
    # print(search)
    # print(test_scraper.movie_data)
    # print(foo['title'])
    # [print(f't: {t} v: {foo[t]}') for t in foo]
    # tmdb_tags = [k for k in foo]
    # print(tmdb_tags)
# https://api.themoviedb.org/3/movie/?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US?query=The%20Witch&page=1&include_adult=false&year=2015
# https://api.themoviedb.org/3/search/movie?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US?query=The%20Witch&page=1&include_adult=false&year=2015
# https://api.themoviedb.org/3/search/movie?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US&query=The%20Witch&page=1&include_adult=false&year=2015
