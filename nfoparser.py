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
# from defs import *
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
    # print(type(file))
    if type(file) == str:
        xml_file = file
    else:
        xml_file = file.path
    try:
        # xml_file = open(file, encoding='utf-8', errors='ignore')
        # xml_data = xml_file.read()
        # xml_file.close()
        ET.parse(xml_file).getroot()
        # print(f'is_valid_xml: {root} {file}')
        return True
    except Exception as e:
        # print(f'is_valid_xml: Invalid XML {xml_file} {e}')
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
    pass
