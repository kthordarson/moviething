import configparser
from requests import get
import json

headers_xml = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

headers = {
    "Accept-Language" : "en-US,en;q=0.5",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
}

class Tmdb_scraper(object):
    # https://api.themoviedb.org/3/movie/<id>?api_key=<apikey>&language=en-US
    config = configparser.ConfigParser()
    config.read('tmdb.ini')
    themoviedbapikey = config['moviethingsettings']['themoviedbapikey']

    def request(self, id):
        url = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=en-US' % (id,self.themoviedbapikey)
        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78&language=en-US
        #  https://api.themoviedb.org/3/movie/tt0152930?api_key=0d8017b2a539fb2b314f25ace5e9aa78
        try:
            print(f'tmdb url: {url}')
            pagedata = get(url,headers=headers_xml).content
            return json.loads(pagedata)
        except Exception as e:
            print(f'tmdb_scrape: err in get {e}')
            return None
        
if __name__ == '__main__':
    t = Tmdb_scraper()
    foo = t.request('tt0152930')
    print(foo)