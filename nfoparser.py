# nfo parser
# read and parse nfo files, return valid info
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

mediainfo_tags = ['Audio Bit rate', 'Audio Bit rate mode', 'Audio Channel positions', 'Audio Channel(s)', 'Audio Channel(s)_Original', 'Audio Codec ID', 'Audio Compression mode', 'Audio Duration', 'Audio Encoded date', 'Audio Format', 'Audio Format profile', 'Audio Format/Info', 'Audio ID', 'Audio Language', 'Audio Sampling rate', 'Audio Stream size', 'Audio Tagged date', 'Video Bit depth', 'Video Bit rate', 'Video Bits/(Pixel*Frame)', 'Video Chroma subsampling',
                  'Video Codec ID', 'Video Codec ID/Info', 'Video Color space', 'Video Display aspect ratio', 'Video Duration', 'Video Encoded date', 'Video Encoding settings', 'Video Format', 'Video Format profile', 'Video Format settings, CABAC', 'Video Format settings, ReFrames', 'Video Format/Info', 'Video Frame rate', 'Video Frame rate mode', 'Video Height', 'Video ID', 'Video Scan type', 'Video Stream size', 'Video Tagged date', 'Video Width', 'Video Writing library']


def get_nfo_data(file):
    nfo_data = {}
    nfo_file = open(file, encoding='utf-8', errors='ignore')
    nfo_raw = nfo_file.readlines()
    regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")
    mediacheck1 = False
    mediacheck2 = False
    is_mediainfofile = False
    imdb_link = None
    for line in nfo_raw:
        match = re.search(regex, line)
        if match:
            imdb_link = match[0]
        if '[mediainfo]' in line:
            # working on mediainfo file...
            mediacheck1 = True
            # print('mediainfo start tag')
        if '[/mediainfo]' in line:
            mediacheck2 = True
            # print('mediainfo end tag')
        if mediacheck1 and mediacheck2:
            # found opening and closing mediainfo tags... probably valid info...
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
    #print(type(result))
    return nfo_data


def extract_mediainfo_tags(file):
    tags = None
    nfo_data = None
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
            #line = line.strip()
            if ':' in line:
                tag, value = line.split(':', maxsplit=1)
                tag = part_tag + ' ' + tag.strip()
                value = value.strip()
                tag_list[tag] = value
                #print(f'{part_tag} tag: {tag}  ---- {value}')
    #tags = sorted(set(tag_list))
    return tag_list


if __name__ == '__main__':
    #file = 'd:/movies/Twelve.Monkeys.1995.1080p.BluRay.H264.AAC-RARBG/Twelve.Monkeys.1995.1080p.BluRay.H264.AAC-RARBG.nfo'
    # file = 'd:/movies/[AnimeRG] Laputa Castle in the Sky (1986) [MULTI-AUDIO] [1080p] [x265] [pseudo]/torrent.nfo'
    #file = 'd:/movies/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG/The.Shining.1980.US.1080p.BluRay.H264.AAC-RARBG.nfo'
    files = (
        'o:/Movies/Movies/Barbie The Pearl Princess (2013)/Barbie The Pearl Princess (2014).orig.nfo', # parsable
        'd:/movies/[AnimeRG] Laputa Castle in the Sky (1986) [MULTI-AUDIO] [1080p] [x265] [pseudo]/torrent.nfo', # not parsable
        'o:/Movies/Movies/Beauty and the Beast (1991)/Beauty and the Beast cd1.orig.nfo', # parsable
        'o:/Movies/Movies/Dirty Grandpa (2015)/Dirty Grandpa cd1.orig.nfo', # parsable
    )
    for file in files:
        print(file)
        res = get_nfo_data(file)
        print(type(res))
        print(res)
    #print(extract_mediainfo_tags(file))
    # get_nfo_data(file)
