import json
from datetime import datetime
from typing import List, Optional


class Genre:
    id: int
    name: str

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


class ProductionCompany:
    id: int
    logo_path: Optional[str]
    name: str
    origin_country: str

    def __init__(self, id: int, logo_path: Optional[str], name: str, origin_country: str) -> None:
        self.id = id
        self.logo_path = logo_path
        self.name = name
        self.origin_country = origin_country

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


class ProductionCountry:
    iso_3166_1: str
    name: str

    def __init__(self, iso_3166_1: str, name: str) -> None:
        self.iso_3166_1 = iso_3166_1
        self.name = name

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


class SpokenLanguage:
    iso_639_1: str
    name: str

    def __init__(self, iso_639_1: str, name: str) -> None:
        self.iso_639_1 = iso_639_1
        self.name = name

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


class Movie:
    adult: bool
    backdrop_path: str
    belongs_to_collection: None
    budget: int
    genres: List[Genre]
    homepage: str
    id: int
    imdb_id: str
    original_language: str
    original_title: str
    overview: str
    popularity: float
    poster_path: str
    production_companies: List[ProductionCompany]
    production_countries: List[ProductionCountry]
    release_date: datetime
    revenue: int
    runtime: int
    spoken_languages: List[SpokenLanguage]
    status: str
    tagline: str
    title: str
    video: bool
    vote_average: float
    vote_count: int

    def __init__(self, adult=False, backdrop_path='', belongs_to_collection=[], budget=0, genres=[], homepage='', id=0,
                 imdb_id='', original_language='', original_title='', overview='', popularity=0, poster_path='',
                 production_companies=[], production_countries=[], release_date=None, revenue=0, runtime=0,
                 spoken_languages=[], status='', tagline='', title='', video=False, vote_average=0,
                 vote_count=0) -> None:
        self.adult = adult
        self.backdrop_path = backdrop_path
        self.belongs_to_collection = belongs_to_collection
        self.budget = budget
        self.genres = genres
        self.homepage = homepage
        self.id = id
        self.imdb_id = imdb_id
        self.original_language = original_language
        self.original_title = original_title
        self.overview = overview
        self.popularity = popularity
        self.poster_path = poster_path
        self.production_companies = production_companies
        self.production_countries = production_countries
        self.release_date = release_date
        self.revenue = revenue
        self.runtime = runtime
        self.spoken_languages = spoken_languages
        self.status = status
        self.tagline = tagline
        self.title = title
        self.video = video
        self.vote_average = vote_average
        self.vote_count = vote_count

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id


if __name__ == "__main__":
    print("testmovieclass")
    jsonfile = "apitest.txt"
    with open(jsonfile) as f:
        data = f.read()
    jsondata = json.loads(data)
    # print(jsondata)
    m = Movie(**jsondata)
    print(m)
    print(m.title)
    print(m.production_companies)
    print(m.production_countries)
