# moviething
# todo
# rename files to match movie title
# check subtitles, dl missing
# gather information about video codec / quality
# delete samples files
# extract movie info from nfo/xml files

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
from xmlparser import get_xml_dict
import difflib
vid_extensions = (
    'mp4', 'mpeg', 'mpg', 'mp2', 'mpe', 'mvpv', 'mp4', 'm4p', 'm4v', 'mov', 'qt', 'avi', 'ts', 'mkv', 'wmv', 'ogv', 'webm', 'ogg'
)

min_filesize = 40000000

# unwanted files / subdirs
# will be deleted automatically
unwanted_files = dict(
    subdirs=("sample", "samples"),
    txtfiles=("readme.txt", "torrent downloaded from extratorrent.cc.txt", "rarbg.com.txt", "torrent-downloaded-from-extratorrent.cc.txt",
              "ahashare.com.txt", "torrent downloaded from demonoid.com - copy.txt", "torrent downloaded from demonoid.com.txt"),
    images=("www.yify-torrents.com.jpg", "screenshot", "www.yts.am.jpg"),
    videos=("rarbg.com.mp4", "sample.mkv")
)

valid_nfo_files = ('nfo', 'xml')


class MovieClass(object):
    def __init__(self, filename):
        self.filename = filename
        self.basename, self.extension = os.path.splitext(filename)
        self.path = os.path.dirname(filename)
        self.imdb_link = None
        self.nfo_file_count = 0
        self.nfo_files = []

    def scan_nfo(self, path):
        # scan folder containing this movie for valid nfo files
        tstart = time.time()
        nfofiles = scan_nfo_files(path)
        for nfo in nfofiles:
            if nfo.name.endswith('xml'):
                try:
                    xml_data = get_xml_dict(nfo)
                    self.xml_data = xml_data
                    self.nfo_file_count += 1
                    self.nfo_files.append(nfo)
                except Exception as e:
                    print(f'Error parsing XML {nfo.name} {e}')
                    xml_data = None
            
    def populate_info(self):
        # gather info to ensure correct folder/filenames
        if self.xml_data is not None:
            print(f'self populate from xml data {self.nfo_files}')
            self.imdb_id = self.xml_data.get('id', None) #self.xml_data['id']
            if self.imdb_id is not None:
                try:
                    self.imdb_link = 'https://www.imdb.com/title/' + self.imdb_id
                except Exception as e:
                    print(f'xml err {self.filename.name} {self.nfo_files} {self.imdb_id} {e}')
                    exit(-1)
            self.title = self.xml_data.get('title', None) # self.xml_data['title']
            self.year =self.xml_data.get('year', None) # self.xml_data['year']
            if self.title is not None and self.year is not None:
                self.correct_pathname = self.title + ' (' + self.year + ')'
                self.correct_filename = self.correct_pathname + self.extension
                self.rename_required = False
                if self.correct_pathname != os.path.basename(self.path):
                    self.rename_required = True
                    if verbose:
                        print(show_diff(self.correct_pathname, os.path.basename(self.path)))
                if self.correct_filename != self.filename.name:
                    self.rename_required = True
                    if verbose:
                        print(show_diff(self.correct_filename, self.filename.name))
                # todo check if actual path/filename matches correct names gathered from nfo/xml and correct if needed
        else:
            print('got no data')
                
def show_diff(text, n_text):
    """
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("^" + seqm.b[b0:b1] + "")
        elif opcode == 'delete':
            output.append("^" + seqm.a[a0:a1] + "")
        elif opcode == 'replace':
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append("^" + seqm.b[b0:b1] + "")
        else:
            pass
            # raise RuntimeError, "unexpected opcode"
    return ''.join(output)

def scan_nfo_files(path):
    # scan given path for valid nfo/xml files containing movie info
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            if entry.name.endswith(valid_nfo_files):
                yield entry


def scantree(path):
    # scan given path for movies with valid extensions and larger than min_filesize
    # todo validate video files
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            if entry.name.endswith(vid_extensions) and entry.stat().st_size > min_filesize:
                yield entry


def scan_subdir(path):
    # return all files from given path
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def fix_base_folder(start_dir, file_list):
    # move files from base folder to subdir named like the movie files without extension
    # todo subfolder naming format <movietitle (year)>. Example "Goodfellas (1990)"
    print(f'fix_base_folder')
    need_rescan = False
    for file in file_list:
        if os.path.dirname(file) == start_dir:
            basefilename, extension = os.path.splitext(file)
            if verbose:
                print(
                    f'# Move {file.name} ext {extension} to subfolder {basefilename}')
            if not os.path.isdir(basefilename):
                if not dry_run:
                    os.makedirs(basefilename)
            need_rescan = True
            if not dry_run:
                os.rename(src=file, dst=basefilename + '/' + file.name)

    # after moving from base folder, rescan and return new list....
    if need_rescan:
        if verbose:
            print(f'Rescan {need_rescan}')
        file_list = []
        for entry in scantree(start_dir):
            file_list.append(entry)
    return file_list


def fix_foldernames(start_dir, file_list):
    # rename files and folders with non-ASCII characters
    # todo cleanup foldername, remove scene tags from foldername. Example:
    # Before "Bone.Tomahawk.2015.720p.WEB-DL.DD5.1.H264-RARBG"
    # After  "Bone Tomahawk (2015)"
    print(f'fix_foldernames')
    need_rescan = False
    for file in file_list:
        # get a clean ASCII name
        unicode_path = unidecode.unidecode(os.path.dirname(file.path))
        old_name = os.path.dirname(file.path)
        if old_name != unicode_path:
            if verbose:
                print(f'Rename FOLDER {old_name} to {unicode_path}')
            if not dry_run:
                try:
                    os.rename(src=old_name, dst=unicode_path)
                except Exception as e:
                    print(
                        f'Error renaming FOLDER {old_name} to {unicode_path} {e}')
            need_rescan = True
    if need_rescan:
        if verbose:
            print(f'Rescan FOLDERS {need_rescan}')
        file_list = []
        for entry in scantree(start_dir):
            file_list.append(entry)
    return file_list


def fix_filenames(start_dir, file_list):
    # rename files and folders with non-ASCII characters
    # todo cleanup filesname, remove scene tags from filename. Example:
    # Before "Bone.Tomahawk.2015.720p.WEB-DL.DD5.1.H264-RARBG.mkv"
    # After  "Bone Tomahawk (2015).mkv"
    print(f'fix_filenames')
    need_rescan = False
    for file in file_list:
        # get a clean ASCII name
        unicode_path = unidecode.unidecode(file.path)
        old_name = file.path
        if old_name != unicode_path:
            if verbose:
                print(f'Rename FILE {old_name} to {unicode_path}')
            if not dry_run:
                try:
                    os.rename(src=old_name, dst=unicode_path)
                except Exception as e:
                    print(
                        f'Error renaming FILE {old_name} to {unicode_path} {e}')
            need_rescan = True
    if need_rescan:
        if verbose:
            print(f'Rescan FILELIST {need_rescan}')
        file_list = []
        for entry in scantree(start_dir):
            file_list.append(entry)
    return file_list


def clean_subfolders(folder_list):
    # clean unwanted files from movie folders
    print('clean_subfolders')
    for subdir in folder_list:
        # are we in a subdir
        search_dir = os.path.dirname(subdir.path)
        if os.path.isdir(search_dir):
            file_list = []
            for entry in scan_subdir(search_dir):
                file_list.append(entry)
        for file in file_list:
            filename = file.name.lower()
            if filename in unwanted_files['txtfiles']:
                if verbose:
                    print(
                        f'\t{filename} in unwanted txtfiles in subdir {search_dir}')
                if not dry_run:
                    os.remove(file)
            if filename in unwanted_files['images']:
                if verbose:
                    print(
                        f'\t{filename} in unwanted images in subdir {search_dir}')
                if not dry_run:
                    os.remove(file)
            if filename in unwanted_files['videos']:
                if verbose:
                    print(
                        f'\t{filename} in unwanted videos in subdir {search_dir}')
                if not dry_run:
                    os.remove(file)
            if file.path.lower() in unwanted_files['subdirs']:
                # if verbose:
                print(f'\t{filename} in unwanted {search_dir}')
                if not dry_run:
                    print(f'TODO Removing subdir {filename}')
                    # os.remove(file)


def populate_movielist(file_list):
    print('populate_movielist')
    movie_list = []
    for file in file_list:
        movie = MovieClass(filename=file)
        movie.scan_nfo(movie.path)
        movie.populate_info()
        movie_list.append(movie)
    return movie_list


def normalscan(start_dir):
    file_list = []
    # populate movie list from base folder...
    for entry in scantree(start_dir):
        file_list.append(entry)
    # move movies in base folder to subfolders...
    file_list = fix_base_folder(start_dir, file_list)
    # fix non-ascii foldernames
    file_list = fix_foldernames(start_dir, file_list)
    # fix non-ascii filenames
    file_list = fix_filenames(start_dir, file_list)
    # clean subfolders of unwanted extra files
    clean_subfolders(file_list)
    return file_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="moviething")
    parser.add_argument("--path", nargs="?", default="d:/movies",
                        help="Base movie folder", required=True, action="store",)
    parser.add_argument("--dryrun", action="store_true",
                        help="Dry run - no changes to filesystem")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()
    if args.path:
        print(f'Basedir: {args.path}')
        basemovie_dir = args.path
    if args.dryrun:
        print(f'Dry run: {args.dryrun}')
        dry_run = True
    else:
        print(f'Dry run: {args.dryrun}')
        dry_run = False
    if args.verbose:
        verbose = True
    else:
        verbose = False
    t1 = time.time()
    # base movie folder
    # each movie should reside in it's own subfolder - not in basemovie_dir
    # structure <drive>:/<movie base dir>/<movie title>

    file_list = normalscan(basemovie_dir)
    # populate movie list and gather info from existing  nfo/xml files
    movie_list = populate_movielist(file_list)
#    for movie in movie_list:
#        print(f'{movie.filename.name} {movie.imdb_link}')
#        if movie.nfo_file_count > 1:
#            print(f'{movie.filename.path} has multiple {movie.nfo_file_count} nfo/xml files')
    print(
        f'moviecount: {len(movie_list)} time {time.time() - t1}')
