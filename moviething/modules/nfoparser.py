# nfo parser
# read and parse nfo files, return valid info

import concurrent.futures
import glob
# import mmap
import os
import re
# import string
import time
# import unicodedata
from collections import defaultdict
# from xml.parsers.expat import ExpatError

from lxml import etree as et
# noinspection PyUnresolvedReferences
from xml.dom import minidom

from moviething.modules.defs import imdb_regex, mediainfo_regex, mediainfo_tags, valid_tag_chars, valid_xml_chars
# from stringutils import sanatized_string
from moviething.modules.stringutils import sanatized_string
from moviething.modules.utils import who_called_func
from pathlib import Path, PurePosixPath, PurePath, PureWindowsPath


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
    # xml_data = None
    try:
        #        tree = et.parse(file)
        #        root = tree.getroot()
        #        xml_data = etree_to_dict(root)
        return etree_to_dict(et.parse(file).getroot()).get('movie') or etree_to_dict(et.parse(file).getroot()).get(
            'Title') or None
    except Exception as e:
        print(f'ERROR: get_xml_data {file} {e}')
        return None


def get_xml_score(file):
    # todo need to fix this...
    # print(type(file))
    valid_score = 0
    if type(file) == str:
        xml_file = file
    else:
        xml_file = file.path
    try:
        data = et.parse(xml_file).getroot()
        # tag_list = [tag.tag for tag in data]
        valid_score += len([k.text for k in data.findall('id')])
        valid_score += len([k.text for k in data.findall('IMDBiD')])  # IMDbId
        valid_score += len([k.text for k in data.findall('IMDbId')])
        # valid_score += len([k.text for k in data.findall('imdb_link')])
        valid_score += len([k.text for k in data.findall('title')])
        valid_score += len([k.text for k in data.findall('Title')])
        valid_score += len([k.text for k in data.findall('originaltitle')])
        # print(f'get_xml_score: caller: {who_called_func()} {file} score: {valid_score}')
        return valid_score
    except Exception as e:
        print(f'get_xml_score: Invalid XML {xml_file} {e}')
        return 0


def is_valid_xml(file):
    # print(type(file))
    if type(file) == str:
        xml_file = file
    else:
        xml_file = file.path
    try:
        data = et.parse(xml_file).getroot()
        # score = get_xml_score(file)
        tag_list = [tag.tag for tag in data]
        # print(f'is_valid_xml: caller: {who_called_func()} {file} {score}')
        if len(tag_list) >= 1:
            return True
    except Exception as e:
        print(f'is_valid_xml: Invalid XML {xml_file} {e}')
        return False


# noinspection PySameParameterValue
def get_xml_list(movie_path):
    # return a list of valid / parsable xml files from movie_path
    # print(type(movie_path))
    if type(movie_path) is not str:
        input_movie_path = str(movie_path.path)
    else:
        input_movie_path = movie_path
    xml_list = glob.glob(input_movie_path + '/*.xml', recursive=False)
    result = [xml for xml in xml_list if is_valid_xml(xml)]
    return result


def get_nfo_list(movie_path):
    # return a list of valid / parsable nfo files from movie_path
    # print(type(movie_path))
    if type(movie_path) is not str:
        input_movie_path = str(movie_path.path)
    else:
        input_movie_path = movie_path
    nfo_list = glob.glob(input_movie_path + '/*.nfo', recursive=False)
    result = [nfo for nfo in nfo_list if is_valid_nfo(nfo)]
    return result


def get_xml(movie_path):
    # scan movie_path for valid xml, return first xml found
    # todo fix if more than one found.....
    # print(f'get_xml {movie_path}')
    # print(f'get_xml: caller {who_called_func()}')
    if type(movie_path) != str:
        # for debugging and testing
        input_movie_path = str(movie_path.path)
    else:
        input_movie_path = movie_path
    # xml = None
    # print(f'get_xml: {input_movie_path} {type(input_movie_path)} {type(movie_path)}')
    try:
        xml = glob.glob(input_movie_path + '/**.xml', recursive=False)  # movie_path+'/*.xml')
        # print(f'got xml {xml}')
    except Exception as e:
        print(f'Error in get_xml {input_movie_path} {e}')
        return None
    if len(xml) == 0:
        return None
    elif len(xml) == 1 and is_valid_xml(xml[0]):
        return xml[0]
    elif len(xml) > 1:
        print(f'Multiple xml found in {input_movie_path}')
        newxml = combine_xml(xml)
        result = et.ElementTree(element=newxml.getroot())
        result_filename = os.path.join(movie_path, PurePath(input_movie_path).parts[-1] + '.xml')
        for f in xml:
            try:
                os.rename(src=f, dst=f + '.olddata')
            except Exception as e:
                print(f'get_xml ERR {e} while renaming old xml')
                return None
        # print(type(result))
        # resultroot = result.getroot()
        try:
            result.write(result_filename)
            return result_filename
        except Exception as e:
            print(f'get_xml ERR {e} while saving new combined xml')
            return None
    else:
        return None


def combine_xml(files):
    first = None
    for filename in files:
        data = et.parse(filename).getroot()
        if first is None:
            first = data
        else:
            first.extend(data)
    if first is not None:
        result = et.ElementTree(first)
        return result


def get_xml_movie_title(xml_file):
    # extract valid movie title and year from xml_file
    # movie_title = None
    # title = None
    try:
        root = et.parse(xml_file).getroot()
        movie_title = root.find('title').text
        movie_year = root.find('year').text
        title = sanatized_string(movie_title) + ' (' + movie_year + ')'
        return title
    except Exception as e:  # as e:
        print(f'get_xml_title: {xml_file} error {e}')
        return None


def is_valid_nfo(file):
    # check if given nfo file contains extractable info, return False if not
    # data = None
    try:
        with open(file, 'r', errors='replace') as f:
            data = f.readlines()  # mmap.mmap(f.fileno(),0)
    except Exception as e:
        print(f'Error opening {file} {e}')
        return False
    if data is not None:
        # print(type(data))
        check_mi = list(filter(mediainfo_regex.match, data))
        check_imdb = imdb_regex.findall(str(data))
        # print(check_imdb)
        if len(check_mi) == 2 or len(check_imdb) >= 1:
            # nfo has valid mediainfo tags or valid imdb link/id
            return True
    return False


def get_tags_from_nfo(nfo):
    result = []
    with open(nfo, 'r', errors='replace') as file:
        data = file.readlines()
    for line in data:
        # check_imdb = None
        tagstrip = re.compile(r'\[[^\]]*\]')
        line = re.sub(tagstrip, '', line)
        check_imdb = imdb_regex.findall(str(line))  # get imdb links before sanatizing line
        if len(check_imdb) >= 1:
            result.append(('imdblink', check_imdb[0][0]))
            result.append(('IMDbId', check_imdb[0][1]))  # 57,23:             id_str = 'IMDbId'
        line = sanatized_string(line, whitelist=valid_tag_chars, replace='', format='NFC')
        if ':' in line:
            tag, value = line.split(':', maxsplit=1)
            tag = tag.strip(' :.').lower()
            # tag = tag.replace(' ', '_')
            value = value.strip(' \n').lower()
            for media_tag in mediainfo_tags:
                mr = re.compile(media_tag)
                match = mr.search(tag)
                if match and len(value) > 1:
                    xml_tag = sanatized_string(media_tag, whitelist=valid_xml_chars, format='NFC')
                    result.append((xml_tag, value))
    #            if tag in mediainfo_tags:
    #                result.append((tag,value))
    return result


def nfo_to_xml(nfo):
    # takes list of one or more nfo, extract tags and returns xml
    # xml = None
    root = et.Element('movie')
    tree = et.ElementTree(element=root)
    root = tree.getroot()
    tags = get_tags_from_nfo(nfo)
    for tag in tags:
        a = et.SubElement(root, tag[0])
        a.text = tag[1]
    # data = et.tostring(tree.getroot(), encoding='utf-8', method='xml')
    data = et.tostring(tree.getroot(), method='xml')
    dataout = minidom.parseString(data)
    pretty_data = dataout.toprettyxml(indent=' ')
    result_file = nfo + '.xml'
    if not os.path.exists(result_file):
        # with open(result_file, mode='w', encoding='utf-8') as f:
        with open(result_file, mode='w') as f:
            f.write(pretty_data)


def test_get_xml_data(xmlfile):
    data = get_xml_data(xmlfile)
    print(data.get('movie')['title'])


def test_nfo_pp(movie_path):
    nfolist = get_nfo_list(movie_path)
    nfo_to_convert = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(is_valid_nfo, nfolist)
    for result in results:
        if result:
            nfo_to_convert.append(nfo_to_convert)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(nfo_to_xml, nfo_to_convert)
    return results


# noinspection PySameParameterValue
def test_nfo_tt(movie_path):
    # fastest method !!!!
    nfolist = get_nfo_list(movie_path)
    nfo_to_convert = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(is_valid_nfo, nfolist)
    for result in results:
        if result:
            nfo_to_convert.append(nfo_to_convert)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(nfo_to_xml, nfo_to_convert)
    return results


def test_nfo(movie_path):
    nfolist = get_nfo_list(movie_path)
    # nfo_to_convert = []
    # for nfo in nfolist:
    #     if is_valid_nfo(nfo):
    #         nfo_to_convert.append(nfo)
    nfo_to_convert = [nfo for nfo in nfolist if is_valid_nfo(nfo)]
    for nfo in nfo_to_convert:
        nfo_to_xml(nfo)


def test_xml_combine():
    # res = get_xml_list('c:/Users/kthor/Documents/development/moviething/testingstuff/testxmls/')
    # res = get_xml_list('c:/Users/kthor/Documents/development/moviething/oldstuff/test')
    reslist = get_xml_list('d:/movies/test-123')
    if len(reslist) > 1:
        newxml = combine_xml(reslist)
        result = et.ElementTree(element=newxml.getroot())
        # resultroot = result.getroot()
        result.write('d:/movies/test-123/out.xml')
        # r.write()


if __name__ == '__main__':
    start = time.perf_counter()
    # test_nfo('d:/movies/test-abc')
    # finish = time.perf_counter()
    # print(f'Finished in {round(finish-start, 2)} second(s)')
    # start = time.perf_counter()
    # test_nfo_pp('d:/movies/test-abc')
    # finish = time.perf_counter()
    # print(f'Finished pp in {round(finish-start, 2)} second(s)')
    # start = time.perf_counter()
    print(f'Starting nfo_parser')
    test_nfo_tt('d:/movies/test-abc')
    finish = time.perf_counter()
    print(f'Finished pp in {round(finish - start, 2)} second(s)')
    pass
