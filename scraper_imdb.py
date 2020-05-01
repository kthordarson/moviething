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
import time
import random
from pathlib import Path

nonBreakSpace = u'\xa0'
strip_chars = ' \n'
replace_break = '\n'
title_year_regex = re.compile(r'(^.+)(\(\d{4}\).?)$')
base_url = 'http://www.imdb.com/title/'

headers_xml = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
}


def imdb_scrape_id(id, debug=False):
    # id is string with valid imdb id format: tt0000000
    # returns dict with movie info
    # data = dict()
    url = base_url + id
    try:
        page = get(url, headers=headers_xml)
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
        if debug:
            return soup
        data = parse_imdb_data(soup, id)
        return data
    except Exception as e:
        print(f'imdb_scrape: err in scrape {e}')
        return None


def parse_imdb_data(soup, id):
    data = dict()
    movie_data = soup.find('div', class_='title_wrapper')
    title_year = movie_data.find('h1').text.replace('\xa0', ' ').strip()
    # title_year = title_year.replace('\xa0', ' ')
    title, year = [_.strip('() ') for _ in title_year_regex.search(title_year).groups()]
    info = unicodedata.normalize("NFKD", movie_data.find(class_='subtext').text).replace(replace_break,
                                                                                         '')  # .text.split('|'))
    rating, duration, genre, fulldate = [_.strip() for _ in info.split('|')]
    # print(f'title: {title_year}')
    data['id'] = id
    data['IMDbId'] = id
    data['imdb_link'] = base_url + id
    data['title'] = title
    data['year'] = year
    data['title_year'] = title_year
    data['rating'] = rating
    data['duration'] = duration
    data['genre'] = genre
    data['fulldate'] = fulldate
    data['plotsummary'] = soup.find('div', class_='summary_text').text.strip()
    return data


def scrape_by_id(imdbid, dest):
    # scrape id and save to dest
    data_input = imdb_scrape_id(imdbid)
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
    result_file = Path.joinpath(dest, data_input[
        'title_year'] + '.xml')  # 'testingstuff/' + data_input['title_year'] + '.xml'
    # result_file = 'c:/Users/kthor/Documents/development/moviething/testingstuff/taxi_ff.html.xml'
    with open(result_file, mode='w') as f:
        f.write(pretty_data)
    print(f'scraper: Saved {result_file}')


def scrape_movie(movie):
    new_data = None
    # scrape movie info...
    # sltime = random.randint(2,9)
    print(f'scrape_movie: Start scraping {movie.moviefile} imdb_id {movie.get_imdb_id()}')
    # time.sleep(sltime) # sleep for imdb.... maybe pointless ?
    new_data = imdb_scrape_id(movie.get_imdb_id())
    if new_data is not None:
        print(f'scrape_movie: Done scraping {movie.moviefile} imdb_id {movie.get_imdb_id()}')
        return new_data
    else:
        print(f'scrape_movie: scrape failed!')
        return None
    # test_imdb_save(new_data)
    return new_data


def imdb_debug(id):
    testfile = 'c:/Users/kthor/Documents/development/moviethingtesting/data/taxi_ff.html'
    with open(testfile, 'r') as f:
        testdata = f.read()
    soup = BeautifulSoup(testdata, 'html.parser')
    data = parse_imdb_data(soup, id)
    return data


def dump_imdb_soup(id, dumpfile):
    dump = imdb_scrape_id(id, debug=True)
    with open(dumpfile, 'wb') as f:
        f.write(dump.encode('utf-8'))


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
    with open(result_file, mode='w') as f:
        f.write(pretty_data)
    print(f'scraper: Saved {result_file}')


if __name__ == '__main__':
    pass
    # res = imdb_scrape_id('tt0152930')
    # res = imdb_debug('tt0152930')
    # test_imdb_save(res)
    # dumpfile = 'c:/Users/kthor/Documents/development/moviethingtesting/imdbsoup1.dat'
    # dumpfilexml = 'c:/Users/kthor/Documents/development/moviethingtesting/imdbsoup1.dat'
    # dump_imdb_soup('tt0152930', dumpfile)

# soup2 = BeautifulSoup(testdata2, 'xml')
# jsondata = soup2.find('script',type="application/ld+json" )
# with open(testfile2, 'r', encoding='utf-8') as f:
# ...:     testdata2 = f.read()
# soup2 = BeautifulSoup(testdata2, 'xml')
# json.loads(soup2.find('script', type='application/ld+json').text.replace('\n',''))
