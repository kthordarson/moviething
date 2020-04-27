# imdb scraper
from lxml import html
from lxml import etree as et
# noinspection PyUnresolvedReferences
from xml.dom import minidom
from io import StringIO, BytesIO
from bs4 import BeautifulSoup
import unicodedata
import re
import os
from requests import get

nonBreakSpace = u'\xa0'
strip_chars = ' \n'
replace_break = '\n'
title_year_regex = re.compile(r'(^.+)(\(\d{4}\).?)$')
base_url = 'http://www.imdb.com/title/'


def imdb_scrape(id):
    # id is string with valid imdb id format: tt0000000
    # returns dict with movie info
    headers = {
        "Accept-Language" : "en-US,en;q=0.5",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
    }
    data = dict()
    url = base_url + id
    try:
        page = get(url,headers=headers)
    except Exception as e:
        print(f'imdb_scrape: err in get {e}')
        return None
    try:
        soup = BeautifulSoup(page.content, 'html.parser')  # lxml / html.parser
    except Exception as e:
        print(f'imdb_scrape: err in soup {e}')
        return None
    # tree = parse(base_url+id)
    # print(tree)
    try:
        movie_data =  soup.find('div', class_ = 'title_wrapper')
        title_year = movie_data.find('h1').text.replace('\xa0', ' ')
        # title_year = title_year.replace('\xa0', ' ')
        title, year = title_year_regex.search(title_year).groups()
        info = unicodedata.normalize("NFKD",movie_data.find(class_='subtext').text).replace(replace_break, '') # .text.split('|'))
        rating, duration, genre, fulldate = info.split('|')
        # print(f'title: {title_year}')
        data['title'] = title
        data['year'] = year.strip('() ')
        data['rating'] = rating.strip(strip_chars)
        data['duration'] = duration.strip(strip_chars)
        data['genre'] = genre.strip(strip_chars)
        data['fulldate'] = fulldate.strip(strip_chars)
        data['title_year'] = title_year
        return data
    except Exception as e:
        print(f'imdb_scrape: err in scrape {e}')
        return None

def imdb_debug(id):
    data = dict()
    testfile = 'c:/Users/kthor/Documents/development/moviething/testingstuff/taxi_ff.html'
    with open(testfile, 'r') as f:
        testdata = f.read()
    soup = BeautifulSoup(testdata, 'html.parser')
    movie_data =  soup.find('div', class_ = 'title_wrapper')
    title_year = movie_data.find('h1').text.replace('\xa0', ' ')
    # title_year = title_year.replace('\xa0', ' ')
    title, year = title_year_regex.search(title_year).groups()
    info = unicodedata.normalize("NFKD",movie_data.find(class_='subtext').text).replace(replace_break, '') # .text.split('|'))
    rating, duration, genre, fulldate = info.split('|')
    # print(f'title: {title_year}')
    data['id'] = id
    data['IMDbId'] = id
    data['imdblink'] = base_url + id
    data['title'] = title
    data['year'] = year.strip('() ')
    data['rating'] = rating.strip(strip_chars)
    data['duration'] = duration.strip(strip_chars)
    data['genre'] = genre.strip(strip_chars)
    data['fulldate'] = fulldate.strip(strip_chars)
    data['title_year'] = title_year
    return data

def test_imdb_save(data_input):
    root = et.Element('movie')
    tree = et.ElementTree(element=root)
    root = tree.getroot()
    for tag in list(data_input):
        a = et.SubElement(root, tag)
        a.text = data_input[tag]
    # data = et.tostring(tree.getroot(), encoding='utf-8', method='xml')
    data = et.tostring(tree.getroot(), method='xml')
    dataout = minidom.parseString(data)
    pretty_data = dataout.toprettyxml(indent=' ')
    result_file = 'testingstuff/' + data_input['title_year'] + '.xml'
    # result_file = 'c:/Users/kthor/Documents/development/moviething/testingstuff/taxi_ff.html.xml'
#    if not os.path.exists(result_file):
        # with open(result_file, mode='w', encoding='utf-8') as f:
    with open(result_file, mode='w') as f:
        f.write(pretty_data)

if __name__ == '__main__':
    # res = imdb_scrape('tt0152930')
    res = imdb_debug('tt0152930')
    test_imdb_save(res)