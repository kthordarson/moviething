class Tmdb_scraper(object):
    # https://api.themoviedb.org/3/movie/<id>?api_key=<apikey>&language=en-US
    def __init__ (self, id):
        self.id = id
        config = configparser.ConfigParser()
        config.read('tmdb.ini')
        self.themoviedbapikey = config['moviethingsettings']['themoviedbapikey']
    def request(self, id):
        url = 'https://api.themoviedb.org/3/movie?api_key=%s' % (self.themoviedbapikey)
        data = self.getJsonData(url, show_error = False)
