# nfo parser
# read and parse nfo files, return valid info
import os
import glob
import re
import string
import unicodedata
from lxml import etree as ET
from collections import defaultdict
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from stringutils import sanatized_string
from defs import *
# from classes import *



def etree_get_dchildren(children):
    dd = defaultdict(list)
    for dc in map(etree_to_dict, children):
        for k, v in dc.items():
            dd[k].append(v)
    return dd

def etree_to_dict(t):
    # from https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = etree_get_dchildren(children)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def get_xml_data(file):
    # read xml data from file, convert to dict and return dict with parsed movie info
    xml_data = None
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        xml_data = etree_to_dict(root)
        root_tag = root.tag
        basedata = xml_data.get(root_tag)
        if root_tag == 'Title':
            id_str = 'IMDbId'
            # title_str = 'OriginalTitle'
            # year_str = 'ProductionYear'
        elif root_tag == 'movie':
            id_str = 'id'
            # title_str = 'title'
            # year_str = 'year'
        id = basedata.get(id_str)
        # title = basedata.get(title_str)
        # year = basedata.get(year_str)
        if type(id) == list:
            id = id[0]
        # print(f'{os.path.dirname(file)}: tag: {root_tag} id: {id} t: {title} y:{year}')
        return xml_data
    except Exception as e:
        print(f'ERROR: get_xml_data {file} {e}')
        return None


def is_valid_xml(file):
    try:
        # xml_file = open(file, encoding='utf-8', errors='ignore')
        # xml_data = xml_file.read()
        # xml_file.close()
        ET.parse(file.path).getroot()
        # print(f'is_valid_xml: {root} {file}')
        return True
    except Exception as e:
        print(f'is_valid_xml: Invalid XML {file} {e}')
        return False

def get_xml(movie_path):
    # scan movie_path for valid xml, return first xml found
    # todo fix if more than one found.....
    # print(f'get_xml {movie_path}')
    if movie_path is not str:
        # for debugging and testing
        input_movie_path = str(movie_path.path)
    else:
        input_movie_path = movie_path
    xml = None
    try:
        xml = glob.glob(input_movie_path + '/*.xml', recursive=False) #movie_path+'/*.xml')
        # print(f'got xml {xml}')
    except Exception as e:
        print(f'Error in get_xml {input_movie_path} {e}')
        return None
    if len(xml) == 0:
        return None
    if len(xml) > 1:
        print(f'Multiple xml found in {input_movie_path}')
    else:
        return xml[0]

def get_xml_movie_title(xml_file):
    # extract valid movie title and year from xml_file
    movie_title = None
    title = None
    try:
        root = ET.parse(xml_file).getroot()
        movie_title = root.find('title').text
        movie_year = root.find('year').text
        title = sanatized_string(movie_title) + ' (' + movie_year + ')'
        return title
    except Exception as e:
        print(f'get_xml_title: {xml_file} error {e}')
        return None



def test_get_xml_data(xmlfile):
    data = get_xml_data(xmlfile)
    print(data.get('movie')['title'])

if __name__ == '__main__':
    test_get_xml_data('o:/Movies/Movies/Shark Tale (2004)/Shark Tale (2004).xml')
    # file = 'd:/movies/Twelve.Monkeys.1995.1080p.BluRay.H264.AAC-RARBG/Twelve.Monkeys.1995.1080p.BluRay.H264.AAC-RARBG.nfo'
    # file = 'd:/movies/[AnimeRG] Laputa Castle in the Sky (1986) [MULTI-AUDIO] [1080p] [x265] [pseudo]/torrent.nfo'
    # file = 'd:/movies/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG.nfo'
    files = (
        # parsable
        'o:/Movies/Movies/Barbie The Pearl Princess (2013)/Barbie The Pearl Princess (2014).orig.nfo',
        # not parsable
        'd:/movies/[AnimeRG] Laputa Castle in the Sky (1986) [MULTI-AUDIO] [1080p] [x265] [pseudo]/torrent.nfo',
        # parsable
        'o:/Movies/Movies/Beauty and the Beast (1991)/Beauty and the Beast cd1.orig.nfo',
        # parsable
        'o:/Movies/Movies/Dirty Grandpa (2015)/Dirty Grandpa cd1.orig.nfo',
        # parsable mediainfo
        'o:/Movies/Movies/Alice in Wonderland (2010)/Alice in Wonderland cd2.orig.nfo',
        'o:/Movies/Movies/Zoolander 2 (2016)/Zoolander 2 cd2.orig.nfo',

    )
    files = 'o:/Movies/Movies/9 Songs (2004)/9 Songs cd2.orig.txt'
    merge_files = (
        'o:/Movies/Movies/Shark Tale (2004)/Shark Tale (2004).xml',
        'c:/Users/kthor/Documents/development/moviething/oldstuff/The Lucky One (2012).xml',
        'c:/Users/kthor/Documents/development/moviething/oldstuff/test/Movie (125).xml',
    )
    nfotest = 'd:/movies/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG.nfo'
    #nfotest = 'o:/Movies/Movies/Shark Tale (2004)/Shark Tale (2004).xml'
#    xml_files = glob.glob('c:/Users/kthor/Documents/development/moviething/oldstuff/test/' + '/*.xml')
    xml_files = glob.glob('o:/movies/movies' + '/**/*.xml', recursive=True)
    testfiles = (
        'c:/Users/kthor/Documents/development/moviething/oldstuff/test/test1.xml',
        'c:/Users/kthor/Documents/development/moviething/oldstuff/test/test2.xml',
        'c:/Users/kthor/Documents/development/moviething/oldstuff/test/test3.xml',
        'c:/Users/kthor/Documents/development/moviething/oldstuff/test/test4.xml',
    )
    testmerge = (
        'o:/Movies/Movies/Dirty Grandpa (2015)/Dirty Grandpa.xml',
        'o:/Movies/Movies/Dirty Grandpa (2015)/Dirty Grandpa (2015).xml',
    )
    test1 =(
    'd:/movies/A Clockwork Orange 1971 720p BluRay x264 AC3 - Ozlem Hotpena/A Clockwork Orange 1971 720p BluRay x264 AC3 - Ozlem Hotpena.xml',
    'd:/movies/Alien.1979.Directors.Cut.1080p.BluRay.H264.AAC-RARBG/Alien.1979.Directors.Cut.1080p.BluRay.H264.AAC-RARBG.xml',
    'd:/movies/Howls.Moving.Castle.2004.720p.BluRay.x264-x0r/Howls.Moving.Castle.2004.720p.BluRay.x264-x0r.xml',
    'd:/movies/Reservoir Dogs (1992)/Reservoir Dogs (1992).xml',
    'd:/movies/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG.xml',
    'd:/movies/Twelve.Monkeys.1995.1080p.BluRay.H264.AAC-RARBG/Twelve.Monkeys.1995.1080p.BluRay.H264.AAC-RARBG.xml',
    )
    nfo1 = 'c:/Users/kthor/Documents/development/moviething/oldstuff/invalid/Zoolander 2 cd2.orig.nfo.invalid'
    nfo1_out = 'c:/Users/kthor/Documents/development/moviething/oldstuff/invalid/Zoolander 2 cd2.orig.nfo.invalid.out'
    nfo1_out = 'c:/Users/kthor/Documents/development/moviething/testingstuff/nfo.out.test'
    nfo2 = 'd:\movies\Howls.Moving.Castle.2004.720p.BluRay.x264-x0r\Howls.Moving.Castle.2004.720p.BluRay.x264-x0r.nfo'
    # nfo_extractor(nfotest,nfo1_out, dry_run=False)
    testdir1 = 'd:/movies/[AnimeRG] Laputa Castle in the Sky (1986) [MULTI-AUDIO] [1080p] [x265] [pseudo]/'
    #for nfo_in in nfotest:
    #    nfo_extractor(nfo_in,nfo1_out, dry_run=False)
    #for file in test1:
    #    t = get_xml_movie_title(file)
    #    print(t)
    # d = combine_xml(testmerge)
    # print(d)
    # e = ET.ElementTree(d)
    # e.write('o:/Movies/Movies/Dirty Grandpa (2015)/Dirty Grandpa (2015)-merged.xml')
        #d = merge_xml_files(testmerge, dry_run=True)
    #merge_xml_files(merge_files)
    

