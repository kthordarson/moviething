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
    config = configparser.ConfigParser()
    config.read('tmdb.ini')
    themoviedbapikey = config['moviethingsettings']['themoviedbapikey']

    def request(self, tmdb_id):
        url = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=en-US' % (tmdb_id, self.themoviedbapikey)
        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US
        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78
        try:
            print(f'tmdb url: {url}')
            pagedata = get(url, headers=HEADERS_XML).content
            return json.loads(pagedata)
        except Exception as e:
            print(f'tmdb_scrape: err in get {e}')
            return None

if __name__ == '__main__':
    print('scraper_tmdb')
    # t = TmdbScraper()
    # foo = t.request('tt0152930')
    # print(foo['title'])
    #[print(f't: {t} v: {foo[t]}') for t in foo]
    #tmdb_tags = [k for k in foo]
    #print(tmdb_tags)
