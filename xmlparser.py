# xml parsing
import os
import re
import time
import hashlib
import requests
import platform
import sys
import codecs
import unidecode
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
# valid_tags = ['title', 'originaltitle', 'rating', 'votes', 'top250', 'year', 'plot', 'outline', 'tagline', 'mpaa', 'credits', 'director',
#             'playcount', 'id', 'tmdbid', 'set', 'sorttitle', 'trailer', 'watched', 'studio', 'genre', 'country', 'actor', 'thumb', 'fanart', 'fileinfo', 'LocalTitle', 'OriginalTitle', 'ForcedTitle', 'IMDBrating', 'ProductionYear', 'MPAARating', 'Added', 'IMDB', 'IMDbId', 'RunningTime', 'TMDbId', 'Language', 'Country', 'Budget', 'Revenue', 'Persons', 'Genres', 'Description', 'Studios', 'Awards', 'BackdropURL', 'Director', 'FullCertifications', 'FormalMPAA', 'Votes', 'ShortDescription', 'Outline', 'Plot', 'PosterURL', 'TagLine', 'TagLines', 'Top250', 'TrailerURL', 'Website', 'WritersList'
#              ]

valid_tags = ['actor', 'added', 'awards', 'backdropurl', 'budget', 'country', 'credits', 'description', 'director', 'fanart', 'fileinfo', 'forcedtitle', 'formalmpaa', 'fullcertifications', 'genre', 'genres', 'id', 'imdb', 'imdbid', 'imdbrating', 'language', 'localtitle', 'mpaa', 'mpaarating', 'originaltitle', 'outline', 'persons', 'playcount', 'plot', 'posterurl', 'productionyear', 'rating', 'revenue', 'runningtime', 'set', 'shortdescription', 'sorttitle', 'studio', 'studios', 'tagline', 'taglines', 'thumb', 'title', 'tmdbid', 'top250', 'trailer', 'trailerurl', 'votes', 'watched', 'website', 'writerslist', 'year']

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

def read_xml(file):
    # read xml, return structured movie info or None if failed
    # todo validate xml before returning imcomplete data....
    data = None
    xml_file = open(file, encoding='utf-8', errors='ignore')
    xml_data = xml_file.readlines()
    xml_file.close()
    root = ET.parse(file).getroot()
    children = list(root)
    for subchild in children:
        print(subchild.tag, subchild.text)
        if len(list(subchild)) > 1:
            for k in list(subchild):
                print(f'\t{k.tag}: {k.text}')

    return data




def get_xml_config(file):
    xml_file = open(file, encoding='utf-8', errors='ignore')
    xml_data = xml_file.read()
    xml_file.close()
    root = ET.fromstring(xml_data)
    xml_config = XmlListConfig(root)
    print(xml_config)
    return xml_config


def xml_merge(file1, file2):
    # todo finish
    # if root.tag == 'movie' - use as source
    # if root.tag == 'title' - copy....
    # resulting xml will have same filename as movie file and title
    # if more than one xml, keep only new xml from merge

    result_file = None
    xmlfile1 = open(file1, encoding='utf-8', errors='ignore')
    xmldata1 = xmlfile1.read()
    xmlfile1.close()

    xmlfile2 = open(file2, encoding='utf-8', errors='ignore')
    xmldata2 = xmlfile2.read()
    xmlfile2.close()

    root1 = ET.parse(file1).getroot()
    root1a = ET.parse(file1)
    root2 = ET.parse(file2).getroot()
    root3 = ET.Element('movie')
    for ch in list(root1):
        root3.append(ch)

    for ch in list(root2):
        print(ch.tag)
        print(root3.find(ch.tag))
        if root3.find(ch.tag) is None:
            root3.append(ch)
    root = ET.ElementTree(element=root3)
    root.write('oldstuff/xmlout1.xml')
    return result_file


def get_valid_tags(file):
    valid_tags = []
    xml_file = open(file, encoding='utf-8', errors='ignore')
    xml_data = xml_file.read()
    xml_file.close()
    root = ET.parse(file).getroot()
    for ch in list(root):
            valid_tags.append(ch.tag.lower())    
    valid_tags = sorted(set(valid_tags))
    return valid_tags


if __name__ == '__main__':

    file1 = 'oldstuff/127 Hours (2010).xml'
    file2 = 'oldstuff/movie.xml'
    file3 = 'o:/Movies/Movies/Bee Movie (2007)/Bee Movie.xml'
    file4 = 'o:/Movies/Movies/Bee Movie (2007)/Bee Movie (2007).xml'
    file5 = 'o:/Movies/Movies/Father of the Bride (1991)/Father of the Bride (1991).xml'
    file6 = 'o:/Movies/Movies/Father of the Bride (1991)/movie.xml'
    files = ('oldstuff/127 Hours (2010).xml', 'oldstuff/movie.xml', 'o:/Movies/Movies/Bee Movie (2007)/Bee Movie.xml', 'o:/Movies/Movies/Bee Movie (2007)/Bee Movie (2007).xml', 'o:/Movies/Movies/Father of the Bride (1991)/Father of the Bride (1991).xml', 'o:/Movies/Movies/Father of the Bride (1991)/movie.xml',)
    #tree = ET.parse(source=file5)
    #root = tree.getroot()
    for file in files:
        res = get_xml_data(file)
        # print(res)
        movie = res.get('movie',None)
        if not movie:
            movie = res.get('Title', None)
        if movie: 
            print(movie)
            id = movie.get('id', None)
            if not id:
                id = movie.get('IMDB', None)
            if id: 
                print(id)
            else:
                print(f'no id in {file}')
        if not movie:
            print(file)
    #print(res)
#    print(res['movie']['id'])
#    print(res.get('IMDbId', None))

	# <watched></watched>
	# <id>tt0389790</id>
	# <id moviedb="imdb">tt0389790</id>
	# <id moviedb="tmdb">5559</id>
	# <id moviedb="themoviedb">5559</id>
	# <filenameandpath></filenameandpath>
