# moviething
# todo
# rename files to match movie title
# check subtitles, dl missing
# gather information about video codec / quality
# delete samples files
# extract movie info from nfo/xml files
# in case of multiple nfo/xml merge into one
import argparse
# import codecs
# import hashlib
import os
import shutil
import glob
# import platform
# import re
# import string
# import sys
import time
# import xml.etree.ElementTree as ET
# from pathlib import Path

# import requests
import unidecode
from threading import Thread
from multiprocessing import Process, Queue, JoinableQueue

from nfoparser import (
    get_nfo_data, get_xml_data, is_valid_nfo,
    is_valid_txt, is_valid_xml, merge_xml_files, sanatized_string,
    get_xml_movie_title, nfo_extractor, check_nfo_files, valid_nfo_files)
from utils import scan_path
from scrapers import imdb_scrape
vid_extensions = (
    'mp4', 'mpeg', 'mpg', 'mp2', 'mpe', 'mvpv', 'mp4', 'm4p', 'm4v', 'mov', 'qt', 'avi', 'ts', 'mkv', 'wmv', 'ogv', 'webm', 'ogg'
)

min_filesize = 40000000


# unwanted files / subdirs
# will be deleted automatically
unwanted_files = dict(
    subdirs=("sample", "samples"),
    txtfiles=("readme.txt", "torrent downloaded from.txt", "rarbg.com.txt", "torrent-downloaded-from-extratorrent.cc.txt",
              "ahashare.com.txt"),
    images=("www.yify-torrents.com.jpg", "screenshot", "www.yts.am.jpg"),
    videos=("rarbg.com.mp4", "sample")
)


class MainThread(Thread):
    def __init__ (self, name, base_path='d:/movies', verbose=True, dry_run=True):
        Thread.__init__(self)
        self.name = name
        self.verbose = verbose
        self.dry_run = dry_run
        self.base_path = base_path
        self.folder_list = None
        self.kill = False
    def run(self):
        if self.verbose:
            print(f'MainThread: {self.name} starting bp: {self.base_path}')
        if self.folder_list is None:
            self.folder_list = get_folders(self.base_path)
        if self.verbose:
            print(f'First scan {len(self.folder_list)}')
        while True:
            if self.kill:
                return
            if self.verbose:
                print(f'MainThread: {self.name} running v:{self.verbose} dr:{self.dry_run}')
            time.sleep(1)
    def join(self):
        self.kill = True
        super().join()
    def get_folders(self):
        self.folder_list = get_folders(self.base_path)
    def dump_folders(self):
        if self.folder_list:
            for f in self.folder_list:
                print(f'{f}')




class MovieClass(object):
    def __init__(self, filename):
        self.filename = filename
        self.basename, self.extension = os.path.splitext(filename)
        self.path = os.path.dirname(filename)
        self.xml_data = None


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
        for entry in scan_path(start_dir, vid_extensions, min_size=min_filesize):
            file_list.append(entry)
    return file_list


def fix_foldernames(start_dir, file_list):
    # rename files and folders with non-ASCII characters
    # todo cleanup foldername, remove scene tags from foldername. Example:
    # Before "Bone.Tomahawk.2015.720p.WEB-DL.DD5.1.H264-RARBG"
    # After  "Bone Tomahawk (2015)"
    # smae format as for filenames
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
        for entry in scan_path(start_dir, vid_extensions, min_size=min_filesize):
            file_list.append(entry)
    return file_list


def fix_filenames(start_dir, file_list):
    # rename files and folders with non-ASCII characters
    # todo cleanup filesname, remove scene tags from filename. Example:
    # Before "Bone.Tomahawk.2015.720p.WEB-DL.DD5.1.H264-RARBG.mkv"
    # After  "Bone Tomahawk (2015).mkv"
    # Correct filenames should be extracted from nfo/xml
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
        for entry in scan_path(start_dir, vid_extensions, min_size=min_filesize):
            file_list.append(entry)
    return file_list


def fix_names(folder):
    # check if folder and files are named correctly, rename with info from xml
    found_xml = False
    # xml_files = []
    xml_files = glob.glob(folder.path + '/*.xml')
    if len(xml_files) > 1:
        print(f'found more than 1 xml {folder.path} - Calling xml combiner...')
        xml_files = merge_xml_files(xml_files, dry_run)
        # exit(-1)
    if len(xml_files) == 1:
        if verbose:
            pass
            # print(f'Found xml {len(xml_files)}, reading {xml_files[0].path}')
        data = get_xml_data(xml_files[0])
        # todo move this stuff to get_xml_data....
        xmldata = data.get('movie', None)
        xmldata2 = data.get('Title', None)
        if xmldata is not None:
            if verbose:
                pass
                # print(f'xml type 1')
            title = xmldata.get('title')
            year = xmldata.get('year')
            imdb_id = xmldata.get('id', None)
            if title is None and year is None and imdb_id is not None:
                if verbose:
                    print(f'Need to scrape for imdb id: {imdb_id} {xml_files[0]}')
                imdb_data = imdb_scrape(imdb_id)
                return False
            elif title is None and year is None and imdb_id is None:
                if verbose:
                    print(f'No data found {xml_files[0]}')
                return False
        elif xmldata2 is not None:
            if verbose:
                pass
                # print('xml type 2')
            title = xmldata2.get('OriginalTitle')
            year = xmldata2.get('ProductionYear')
            imdb_id = xmldata2.get('IMDbId', None)
            if title is None and year is None and imdb_id is not None:
                if verbose:
                    print(f'Need to scrape for imdb id: {imdb_id} {xml_files[0]}')
                imdb_data = imdb_scrape(imdb_id)
                return False
            elif title is None and year is None and imdb_id is None:
                if verbose:
                    print(f'No data found {xml_files[0]}')
                return False
        if verbose:
            print(f't:{title} y: {year} id:{imdb_id} {xml_files[0]}')


def clean_subfolder(base_folder):
    if verbose:
        pass
        # print(f'clean_subfolder start: {base_folder}')
    for d in os.scandir(base_folder):
        if os.path.isdir(d):
            if verbose:
                pass
                # print(f'Checking folder: {d.name}')
            if d.name.lower() in unwanted_files['subdirs']:
                print(f'{d.path} is unwanted, delete!')
                if not dry_run:
                    try:
                        shutil.rmtree(d.path, ignore_errors=True)
                        # os.removedirs(d.path)
                        # os.rename(src=d.path, dst=d.path+'.deleted')
                    except Exception as e:
                        print(f'Delete subfolder {d.path} failed {e}')
                        # exit(-1)
        else:
            if d.name.lower() in unwanted_files['txtfiles'] or d.name.lower() in unwanted_files['videos'] or d.name.lower() in unwanted_files['images']:
                if verbose:
                    print(f'Unwanted file: {d.path}')
                if not dry_run:
                    try:
                        os.remove(d.path)
                    except Exception as e:
                        print(f'Could not delete {d.path} {e}')



def populate_movielist(file_list):
    print('populate_movielist')
    movie_list = []
    for file in file_list:
        movie = MovieClass(filename=file)
        movie.scan_nfo(movie.path)
        movie.populate_info()
        movie_list.append(movie)
    return movie_list


def get_folders(base_path):
    folders = []
    for d in os.scandir(base_path):
        if os.path.isdir(d):
            folders.append(d)
            # print(f'{d} is folder')
    return folders


def normalscan(start_dir):
    file_list = []
    # populate movie list from base folder...
    for entry in scan_path(start_dir, vid_extensions, min_size=min_filesize):
        file_list.append(entry)
    # move movies in base folder to subfolders...
    # todo check if file exists in basefolder before calling fix_base_folder
    # file_list = fix_base_folder(start_dir, file_list)
    # fix non-ascii foldernames
    # file_list = fix_foldernames(start_dir, file_list)
    # fix non-ascii filenames
    # file_list = fix_filenames(start_dir, file_list)
    # clean subfolders of unwanted extra files
    folder_list = get_folders(start_dir)
    for folder in folder_list:
        clean_subfolder(folder)
        # todo scan and merge nfo/xml first
        fix_names(folder)
    exit(-1)
    # clean_subfolders(start_dir)
    # check for multiple nfo/xml and merge into one file
    # todo change this..... check only one movie folder at a time, then check folder/file naming
    # check_nfo_files(file_list, dry_run, verbose)
    # rescan .... todo fix
    file_list = []
    # populate movie list from base folder...
    for entry in scan_path(start_dir, vid_extensions, min_size=min_filesize):
        file_list.append(entry)

    return file_list

def check_main_thread(thread):
    return thread.isAlive()

def stop_main(thread):
    thread.join()
    exit(0)

def main_program(args):
    thread = list()
    main_thread = MainThread('MainThread', base_path = args.path, verbose = args.verbose, dry_run=args.dryrun)
    main_thread.setDaemon = True
    main_thread.start()
    while check_main_thread(main_thread):
        try:
            cmd = input('>')
            if cmd[:1] == 'q':
                stop_main(main_thread)
            if cmd[:1] == 'd':
                main_thread.dump_folders()
            if cmd[:1] == 'f':
                main_thread.get_folders()
        except KeyboardInterrupt:
            stop_main(main_thread)

def get_args():
    parser = argparse.ArgumentParser(description="moviething")
    parser.add_argument("--path", nargs="?", default="d:/movies",
                        help="Base movie folder", required=True, action="store",)
    parser.add_argument("--import_path", action="store",
                        help="Import movie files from folder and move them to Base movie folder")
    parser.add_argument("--dryrun", action="store_true",
                        help="Dry run - no changes to filesystem")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()
    if args.path:
        print(f'Basedir: {args.path}')
        basemovie_dir = args.path
    if args.import_path:
        print(f'Importing from: {args.import_path}')
        import_path = args.import_path
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
    return parser.parse_args()

if __name__ == '__main__':
    t1 = time.time()
    args = get_args()
    verbose = args.verbose
    dry_run = args.dryrun
    main_program(args)
    # base movie folder
    # each movie should reside in it's own subfolder - not in basemovie_dir
    # structure <drive>:/<movie base dir>/<movie title>
#    file_list = normalscan(basemovie_dir)
    # populate movie list and gather info from existing  nfo/xml files
    # movie_list = populate_movielist(file_list)
    # imdb_links = 0
    # imdb_missing = 0
    # for movie in movie_list:
    #     if movie.imdb_link is None:
    #         imdb_missing += 1
    #     else:
    #         imdb_links += 1
    # print(f'moviecount: {len(movie_list)} time {time.time() - t1}')
    # print(f'valid links {imdb_links} missing {imdb_missing}')
