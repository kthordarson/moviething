# nfo parser
# read and parse nfo files, return valid info
# import argparse
# import codecs
# import hashlib
import os
# import platform
import re
import string
import unicodedata
# import sys
# import time
#import xml.etree.ElementTree as ET
from lxml import etree as ET
from collections import defaultdict
from xml.dom import minidom
from xml.parsers.expat import ExpatError
# from pathlib import Path

# import requests
# import unidecode

valid_input_string_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

mediainfo_tags = [
    'audio bit rate', 'audio bit rate mode', 'audio channel positions', 'audio channel(s)', 'audio channel(s)_original',
    'audio codec id', 'audio compression mode', 'audio duration', 'audio encoded date', 'audio format', 'audio format profile',
    'audio format/info', 'audio id', 'audio language', 'audio sampling rate', 'audio stream size', 'audio tagged date', 'video bit depth',
    'video bit rate', 'video bits/(pixel*frame)', 'video chroma subsampling', 'video codec id', 'video codec id/info', 'video color space',
    'video display aspect ratio', 'video duration', 'video encoded date', 'video encoding settings', 'video format', 'video format profile',
    'video format settings, cabac', 'video format settings, reframes', 'video format/info', 'video frame rate', 'video frame rate mode',
    'video height', 'video id', 'video scan type', 'video stream size', 'video tagged date', 'video width', 'video writing library',
    'format', 'id','format','format/info','format profile','format settings, cabac','format settings, reframes','codec id','codec id/info','duration','bit rate','width','height','display aspect ratio','frame rate mode','frame rate','color space','chroma subsampling','bit depth','scan type','bits/(pixel*frame)','stream size','writing library','encoded date','tagged date',
    ]


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class XMLCombiner(object):
    # https://stackoverflow.com/questions/14878706/merge-xml-files-with-nested-elements-without-external-libraries
    def __init__(self, filenames):
        self.filenames = filenames
        self.roots = []
        for f in filenames:
            try:
                root = ET.parse(f.path).getroot()
                self.roots.append(root)
            except Exception as e:
                print(f'XMLCombiner: Error parsing xml {f} {e}')
                exit(-1)
        # assert len(filenames) > 0, 'No filenames!'
        # save all the roots, in order, to be processed later
        # self.roots = [ET.parse(f).getroot() for f in filenames]

    def combine(self):
        for r in self.roots[1:]:
            # combine each element with the first one, and update that
            self.combine_element(self.roots[0], r)
        # return the string representation
        # return ET.tostring(self.roots[0])
        return ET.ElementTree(element=self.roots[0])

    def combine_element(self, one, other):
        """
        This function recursively updates either the text or the children
        of an element if another element is found in `one`, or adds it
        from `other` if not found.
        """
        # Create a mapping from tag name to element, as that's what we are fltering with
        # mapping = {el.tag: el for el in one}
        mapping = {(el.tag, hashabledict(el.attrib)): el for el in one}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    # Update the text
                    # mapping[el.tag].text = el.text
                    mapping[(el.tag, hashabledict(el.attrib))].text = el.text
                except KeyError:
                    # An element with this name is not in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    # mapping[el.tag] = el
                    # Add it
                    one.append(el)
            else:
                try:
                    # Recursively process the element, and update it in the same way
                    # self.combine_element(mapping[el.tag], el)
                    self.combine_element(
                        mapping[(el.tag, hashabledict(el.attrib))], el)
                except KeyError:
                    # Not in the mapping
                    # mapping[el.tag] = el
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    # Just add it
                    one.append(el)


def sanatized_string(input_string, whitelist=valid_input_string_chars, replace=''):
    # replace spaces
    for r in replace:
        input_string = input_string.replace(r, '_')

    # keep only valid ascii chars
    cleaned_input_string = unicodedata.normalize(
        'NFKD', input_string).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_input_string = ''.join(
        c for c in cleaned_input_string if c in whitelist)
    if len(cleaned_input_string) > char_limit:
        print("Warning, input_string truncated because it was over {}. input_strings may no longer be unique".format(char_limit))
    return cleaned_input_string[:char_limit]


def get_nfo_data(file):
    nfo_data = {}
    nfo_file = open(file, encoding='utf-8', errors='ignore')
    nfo_raw = nfo_file.readlines()
    regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")
    mediacheck_mi_1 = False
    mediacheck_mi_2 = False
    # check_mi_2 = False
    is_mediainfofile = False
    imdb_link = None
    for line in nfo_raw:
        match = re.search(regex, line)
        if match:
            imdb_link = match[0]
        if '[mediainfo]' in line:
            # working on mediainfo file...
            mediacheck_mi_1 = True
            # print('check_mi_2diainfo start tag')
        if '[/mediainfo]' in line:
            mediacheck_mi_2 = True
            # print('mediainfo end tag')
        if mediacheck_mi_1 and mediacheck_mi_2:
            # found check_mi_2ening and closing mediainfo tags... probably valid info...
            is_mediainfofile = True
            # print('Valid mediainfo')
    if imdb_link:
        nfo_data['imdb_link'] = imdb_link
    else:
        # no imdb info...
        return None
    if is_mediainfofile:
        nfo_data['mediainfo'] = extract_mediainfo_tags(file)
        # nfo_data.append(media_info)
    # result = {nfo_data[i]: nfo_data[i + 1] for i in range(0, len(nfo_data), 2)}
    # print(type(result))
    return nfo_data


def extract_mediainfo_tags(file):
    # tags = None
    # nfo_data = None
    nfo_file = open(file, encoding='utf-8', errors='ignore')
    nfo_raw = nfo_file.readlines()
    mediainfo = False
    videopart = False
    audiopart = False
    part_tag = '_'
    tag_list = {}
    for line in nfo_raw:
        if line == '':
            part_tag = '---'
        if '[mediainfo]' in line:
            # working on mediainfo file...
            # print('mediainfo start')
            mediainfo = True
        if 'Video' in line:
            videopart = True
            part_tag = 'Video'
        if 'Audio' in line:
            videopart = False
            audiopart = True
            part_tag = 'Audio'
        if 'Menu #' in line:
            part_tag == line
            videopart = False
            audiopart = False
            # print('menu')
            # print(line)
        if mediainfo and (videopart or audiopart):
            # line = line.strip()
            if ':' in line:
                tag, value = line.split(':', maxsplit=1)
                tag = part_tag + ' ' + tag.strip()
                value = value.strip()
                tag_list[tag] = value
                # print(f'{part_tag} tag: {tag}  ---- {value}')
    # tags = sorted(set(tag_list))
    return tag_list


def is_valid_txt(file):
    # try to find valid imdb link from txt file
    regex_imdb = re.compile(
        r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")
    try:
        data = open(file, 'r', encoding='utf-8').read()
    except Exception as e:
        print(f'Error opening {file} {e}')
        data = None
        return False
    if data is not None:
        check_imdb = re.findall(regex_imdb, data)
        if len(check_imdb) >= 1:
            # contains valid imdb link return True
            # print(check_imdb)
            return True
    return False


def is_valid_nfo(file):
    # check if given nfo file contains extractable info, return False if not
    # regex for nfo containing mediainfo
    regex_mi_1 = r'\[mediainfo\]'
    regex_mi_2 = r'\[\/mediainfo\]'
    # regex to find imdb link
    regex_imdb = re.compile(
        r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")
    check_mi_1 = False
    check_mi_2 = False
    data = None
    try:
        data = open(file, 'r', encoding='utf-8').read()
    except Exception as e:
        print(f'Error opening {file} {e}')
        data = None
        return False
    if data is not None:
        check_mi_1 = re.findall(regex_mi_1, data)
        check_mi_2 = re.findall(regex_mi_2, data)
        if len(check_mi_1) + len(check_mi_2) == 2:
            # contains valid mediainfo, return True
            return True
        check_imdb = re.findall(regex_imdb, data)
        if len(check_imdb) >= 1:
            # contains valid imdb link return True
            # print(check_imdb)
            return True
    return False


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                else:
                    aDict = {element[0].tag: XmlListConfig(element)}
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            elif element.items():
                self.update({element.tag: dict(element.items())})
            else:
                self.update({element.tag: element.text})


def get_xml_dict(file):
    tree = ET.parse(source=file)
    root = tree.getroot()
    xmldict = XmlDictConfig(root)
    # print(xmldict)
    return xmldict


def etree_to_dict(t):
    # from https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
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
    tree = ET.parse(source=file)
    root = tree.getroot()
    xml_data = etree_to_dict(root)
    return xml_data


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


def get_xml_movie_title(nfo_file):
    movie_title = None
    title = None
    try:
        if nfo_file.name == 'movie.xml':
            root = ET.parse(nfo_file).getroot()
            movie_title = root.find('OriginalTitle').text
            movie_year = root.find('ProductionYear').text
            title = sanatized_string(movie_title) + ' (' + movie_year + ')'
            return title
        else:
            root = ET.parse(nfo_file).getroot()
            movie_title = root.find('title').text
            movie_year = root.find('year').text
            title = sanatized_string(movie_title) + ' (' + movie_year + ')'
    except Exception as e:
        print(f'Error extracting xml movie title from {nfo_file.path} {e}')
        exit(-1)
    return title


def xml_merge_nfo_files(files, dry_run):
    # merger...
    # todo fix output filename
    r = XMLCombiner(files).combine()
    result = ET.ElementTree(element=r.getroot())
    guess_regex = re.compile(r'^(.*)[^\(](\(\d{4}\)$)')
    title = result.find('title')
    if title is not None: title = title.text
    year = result.find('year')
    if year is not None: year = year.text
    if title is None or year is None:
        guess_data = os.path.basename(os.path.dirname(files[0].path))
        guess = re.search(guess_regex, guess_data)
        title = guess.group(1)
        year = guess.group(2)
    # if title is None:
    #     guessed_title = os.path.basename(os.path.dirname(files[0].path))
    #     print(f'xml_merge_nfo: got no title {files}')
    #     print(f'Guessed title {guessed_title}')
    #     # exit(-1)
    
    # if year is None:
    #     print(f'xml_merge_nfo: got no year {files}')
    #     exit(-1)

    # todo rename / delete old files
    for file in files:
        new_name = file.path + '.old_data'
        try:
            if not dry_run:
                os.rename(src=file, dst=new_name)
            print(f'file: {file.path} renamed to {new_name}')
        except Exception as e:
            print(f'Rename {file} failed {e}')
            # return False
    final_xml = os.path.dirname(files[0]) + '/' + sanatized_string(title) + ' (' + year + ').merged.xml'
    print(f'Saving merged xml as {final_xml}')
    if not dry_run:
        try:
            result.write(final_xml, xml_declaration=True, encoding='utf-8')
            return True
        except Exception as e:
            print(f'Error saving final xml {e}')
            return False
    return True

def nfo_extractor(nfo_file, result_file, dry_run):
    root = ET.Element('movie')
    tree = ET.ElementTree(element=root)
    root = tree.getroot()
    imdb_link = None
    imdb_regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/(tt\d{7})")
    tag_regex_1 = re.compile(r"^(\w|\s)+[^\.]")
    try:
        f = open(nfo_file, mode='r', encoding='utf-8', errors='ignore')
    except FileNotFoundError as e:
        print(f'nfo_extractor: {e}')
        return
    lines = f.read().split('\n')
    tag_count = 0
    for line in lines:
        imdb_match = re.search(imdb_regex, line)
        if imdb_match:
            imdb_link = imdb_match.group(0)
            imdb_id = imdb_match.group(1)
            a = ET.SubElement(root,'imdb_link')
            a.text = imdb_link
            a = ET.SubElement(root,'id')
            a.text = imdb_id
            tag_count += 1
        else:
            try:
                tag, value = line.split(':', maxsplit=1)
                tag = tag.strip()
#                tag = tag.replace(' ','')
                value = value.strip()
                if tag == 'ID': tag = None # used by imdb
                if tag.lower() in mediainfo_tags:
                    tag = tag.replace(' ', '')
                    tag_count += 1
                    # print(f't: {tag} v: {value} c: {tag_count}')
                    a = ET.SubElement(root,tag)
                    a.text = value
                    
            except:
                pass
    if imdb_link is not None:
        tree = ET.ElementTree(root)
        try:
            tree.write(result_file, pretty_print=True, xml_declaration=True,   encoding="utf-8")
            print(f'Extracted {tag_count} from {nfo_file} saved as {result_file}')            
            if not dry_run:
                os.rename(src=nfo_file, dst=nfo_file + '.invalid')
            return True
        except Exception as e:
            print(f'{e}')
            exit(-1)
    else:
        print(f'No IMDB link/id found in {nfo_file}')
        if not dry_run:
            os.rename(src=nfo_file, dst=nfo_file + '.invalid')
        return False
    return True

if __name__ == '__main__':
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
    files = ('o:/Movies/Movies/9 Songs (2004)/9 Songs cd2.orig.txt',)
    merge_files = (
        'c:/Users/kthor/Documents/development/moviething/oldstuff/movie.xml',
        'c:/Users/kthor/Documents/development/moviething/oldstuff/The Lucky One (2012).xml',
        'c:/Users/kthor/Documents/development/moviething/oldstuff/The Lucky One 2012.xml')
    nfotest = 'd:/movies/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG.nfo'
    nfo_extractor(nfotest, 'testingstuff/testout.xml')
    #xml_merge_nfo_files(merge_files)
