# nfo parser
# read and parse nfo files, return valid info

import concurrent.futures
import re
from pathlib import Path
from random import randint
from xml.dom import minidom

from lxml import etree as et

from defs import (
    IMDB_REGEX, MEDIAINFO_REGEX, MEDIAINFO_TAGS, VALID_TAG_CHARS,
    VALID_XML_CHARS, XML_TYPE_LIST)
from etree import etree_to_dict
from stringutils import sanatized_string


# noinspection PyUnresolvedReferences


# from stringutils import sanatized_string

# from classes import *


def get_xml_data(file):
    # read xml data from file, convert to dict and return dict with parsed movie info
    # xml_data = None
    try:
        #        tree = et.parse(file)
        #        root = tree.getroot()
        #        xml_data = etree_to_dict(root)
        return etree_to_dict(et.parse(str(file)).getroot()).get('movie') or etree_to_dict(
            et.parse(str(file)).getroot()).get('Title') or None
    except Exception as e:
        print(f'ERROR: get_xml_data {file} {e}')
        return None


def get_xml_moviedata(file):
    # read xml data from file, convert to dict and return dict with parsed movie info
    # xml_data = None
    root = et.parse(str(file)).getroot()
    data = etree_to_dict(root)
    return data['movie']


def get_xml_score(xml_file):
    # todo need to fix this...
    # print(type(file))
    valid_score = 0
    try:
        data = et.parse(str(xml_file)).getroot()
        # tag_list = [tag.tag for tag in data]
        valid_score += len([k.text.lower() for k in data.findall('id')])
        valid_score += len([k.text.lower() for k in data.findall('imdbid')])  # IMDbId / IMDBiD
        # valid_score += len([k.text for k in data.findall('IMDbId')])
        # valid_score += len([k.text for k in data.findall('imdb_link')])
        valid_score += len([k.text.lower() for k in data.findall('title')])
        # valid_score += len([k.text for k in data.findall('Title')])
        # valid_score += len([k.text for k in data.findall('originaltitle')])
        return valid_score
    except Exception as e:
        print(f'get_xml_score: Invalid XML {xml_file} {e}')
        return 0


def is_valid_xml(xml_file):
    # print(type(file))
    try:
        data_root = et.parse(str(xml_file)).getroot()
        # data = etree_to_dict(data_root)
        if data_root.tag not in XML_TYPE_LIST:
            print(f'is_valid_xml: Invalid XML {xml_file} {data_root.tag}')
            return False
        else:
            return True
    except Exception as e:
        print(f'is_valid_xml: Invalid XML {xml_file} {e}')
        return False


def check_xml(movie_path):
    xml_list = movie_path.glob('*.xml')
    for xml_file in xml_list:
        data_root = et.parse(str(xml_file)).getroot()
        if data_root.tag == 'Title':
            print(f'check_xml: need to convert {str(xml_file)}')
    # pass


# noinspection PySameParameterValue
def get_xml_list(movie_path):
    # return a list of valid / parsable xml files from movie_path
    # print(type(movie_path))
    xml_list = movie_path.glob('*.xml')  # glob.glob(movie_path + '/*.xml', recursive=False)
    result = [xml for xml in xml_list if is_valid_xml(xml)]
    return result


def get_nfo_list(movie_path):
    # return a list of valid / parsable nfo files from movie_path
    # print(type(movie_path))
    nfo_list = movie_path.glob('*.nfo')  # glob.glob(movie_path + '/*.nfo', recursive=False)
    result = [nfo for nfo in nfo_list if is_valid_nfo(nfo)]
    return result


def get_xml(movie_path):
    # scan movie_path for valid xml, return first xml found
    # todo fix if more than one found.....
    # print(f'get_xml {movie_path}')
    # print(f'get_xml: caller {who_called_func()}')
    # xml = [xml for xml in movie_path.glob('*.xml')]
    xml = [xml for xml in movie_path.glob('*.xml')] or None
    if xml is None:
        return None
    if len(xml) == 1 and is_valid_xml(xml[0]):
        return xml[0]
    else:
        # return None
        print(f'Multiple xml found in {movie_path}')
        newxml = combine_xml(xml)
        result = et.ElementTree(element=newxml.getroot())
        result_filename = Path.joinpath(movie_path, movie_path.parts[-1] + '.xml')
        for f in xml:
            try:
                f_target = str(f) + '.' + str(randint(100, 999)) + '.olddata'
                f.rename(f_target)
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


def combine_xml(files):
    first = None
    for filename in files:
        data = et.parse(str(filename)).getroot()
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
        root = et.parse(str(xml_file)).getroot()
        movie_title = root.find('title').text
        movie_year = root.find('year').text
        title = sanatized_string(movie_title) + ' (' + movie_year + ')'
        return title
    except TypeError as e:  # as e:
        # print(f'get_xml_movie_title: {xml_file} error {e}')
        return None
    except AttributeError as e:  # as e:
        # print(f'get_xml_movie_title: {xml_file} error {e}')
        return None
    except:
        return None


def get_xml_imdb_id(xml_file):
    # get imdb id from xml
    # movie_title = None
    # title = None
    try:
        root = et.parse(str(xml_file)).getroot()
        result = [tag.text for tag in root if 'id' in tag.tag.lower()]
        return result[0] if len(result) >= 1 else None  # root.find('id').text
    except Exception as e:  # as e:
        print(f'get_xml_imdb_id: {xml_file} error {e}')
        return None


def get_xml_imdb_link(xml_file):
    # get imdb link from xml
    # movie_title = None
    # title = None
    try:
        root = et.parse(str(xml_file)).getroot()
        return root.find('imdb_link').text
    except Exception as e:  # as e:
        print(f'get_xml_imdb_link: {xml_file} error {e}')
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
        check_mi = list(filter(MEDIAINFO_REGEX.match, data))
        check_imdb = IMDB_REGEX.findall(str(data))
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
        check_imdb = IMDB_REGEX.findall(str(line))  # get imdb links before sanatizing line
        if len(check_imdb) >= 1:
            result.append(('imdblink', check_imdb[0][0]))
            result.append(('id', check_imdb[0][1]))  # 57,23:             id_str = 'IMDbId'
        line = sanatized_string(line, whitelist=VALID_TAG_CHARS, replace='', s_format='NFC')
        if ':' in line:
            tag, value = line.split(':', maxsplit=1)
            tag = tag.strip(' :.').lower()
            # tag = tag.replace(' ', '_')
            value = value.strip(' \n').lower()
            for media_tag in MEDIAINFO_TAGS:
                mr = re.compile(media_tag)
                match = mr.search(tag)
                if match and len(value) > 1:
                    xml_tag = sanatized_string(media_tag, whitelist=VALID_XML_CHARS, s_format='NFC')
                    result.append((xml_tag, value))
    #            if tag in MEDIAINFO_TAGS:
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
    # try:
    #     imdb_link = [IMDB_REGEX.search(tag[1]).group(2) for tag in tags if IMDB_REGEX.search(tag[1]) is not None]
    # except Exception:
    #     imdb_link = None
    # if imdb_link is not None:
    #     # scrape imdb link
    #     imdbdata = None  # imdb_scrape_id(imdb_link[0])
    #     for tag in imdbdata:
    #         a = et.SubElement(root, tag)
    #         a.text = imdbdata[tag]
    # [et.SubElement(root2, k) for k in imdbdata] # [print(f'k: {k} v:{imdbdata[k]}') for k in imdbdata]
    # imdb_result = parse_imdb_data(imdbdata, imdb_link[0])
    data = et.tostring(tree.getroot(), method='xml')
    dataout = minidom.parseString(data)
    pretty_data = dataout.toprettyxml(indent=' ')
    # resname = nfo.parts[-2]+'.xml'
    result_file = Path.joinpath(nfo.parent, nfo.parts[-2] + '.xml')  # nfo + '.xml'
    if Path(result_file).exists():
        # rename
        target = Path.joinpath(nfo.parent, nfo.parts[-2] + '.' + str(randint(100, 999)) + '.olddata')
        try:
            result_file.rename(target)
        except Exception as e:
            print(f'nfo_to_xml: rename error {e}')
    try:
        with open(result_file, mode='w') as f:
            f.write(pretty_data)
        # rename old nfo
        target = Path.joinpath(nfo.parent, nfo.parts[-2] + '.' + str(randint(100, 999)) + '.nfo.olddata')
    except Exception as e:
        print(f'nfo_to_xml: save error {e}')


def nfo_process_path(path):
    # convert all nfo's in path to one combined xml
    nfo_list = get_nfo_list(path)
    # [print(get_tags_from_nfo(file)) for file in nfo_list]
    # print(nfo_list)
    _ = [nfo_to_xml(file) for file in nfo_list]
    return get_xml(path)


def test_get_xml_data(xmlfile):
    data = get_xml_data(xmlfile)
    print(data.get('movie')['title'])


def test_nfo_pp(movie_path):
    nfolist = get_xml_list(movie_path)
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
    nfolist = get_xml_list(movie_path)
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
    nfolist = get_xml_list(movie_path)
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
    print('nfoparser')
    # nfo_list = get_nfo_list(Path('d:/movies_incoming/A Clockwork Orange 1971 720p BluRay x264 AC3 - Ozlem Hotpena/'))
    # [print(get_tags_from_nfo(file)) for file in nfo_list]
    # print(nfo_list)
    # [nfo_to_xml(file) for file in nfo_list]
    # start = time.perf_counter()
    # test_nfo('d:/movies/test-abc')
    # finish = time.perf_counter()
    # print(f'Finished in {round(finish-start, 2)} second(s)')
    # start = time.perf_counter()
    # test_nfo_pp('d:/movies/test-abc')
    # finish = time.perf_counter()
    # print(f'Finished pp in {round(finish-start, 2)} second(s)')
    # start = time.perf_counter()
    # print(f'Starting nfo_parser')
    # test_nfo_tt('d:/movies/test-abc')
    # finish = time.perf_counter()
    # print(f'Finished pp in {round(finish - start, 2)} second(s)')
    # pass
