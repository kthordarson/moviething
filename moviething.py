# moviething
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

from pathlib import Path

vid_extensions = (
    'mp4', 'mpeg', 'mpg', 'mp2', 'mpe', 'mvpv', 'mp4', 'm4p', 'm4v', 'mov', 'qt', 'avi', 'ts', 'mkv', 'wmv', 'ogv', 'webm', 'ogg'
)

min_filesize = 40000000

# unwanted files / subdirs
# will be deleted automatically
unwanted_files = dict(
    subdirs = ("sample", "samples"),
    txtfiles = ("readme.txt", "torrent downloaded from extratorrent.cc.txt", "rarbg.com.txt", "torrent-downloaded-from-extratorrent.cc.txt", "ahashare.com.txt", "torrent downloaded from demonoid.com - copy.txt", "torrent downloaded from demonoid.com.txt"),
    images = ("www.yify-torrents.com.jpg", "screenshot", "www.yts.am.jpg"),
    videos = ("rarbg.com.mp4", "sample.mkv")
)

valid_nfo_files = ('nfo', 'xml')

class MovieClass(object):
    def __init__ (self, filename):
        self.filename = filename
        self.path = os.path.dirname(filename)
        self.imdb_link = None
    def scan_nfo(self, path):
        # scan folder containing this movie for valid nfo files
        tstart = time.time()
        nfofiles = scan_nfo_files(path)
        for nfo in nfofiles:
            # print(f'nfo {nfo.name}')
            if nfo.name.endswith(valid_nfo_files):
                try:
                    nfo_file = open(nfo, encoding='utf8', errors='ignore')
                    nfo_data = nfo_file.readlines()
                    nfo_file.close()
                except Exception as e:
                    print(f'Error reading nfo {nfo_file.name} {e}')
                    nfo_file = None
            else:
                print(f'Invalid nfo {nfo.path}')
                nfo_file = None
                
            
            # print(f'Parsing {nfo.name} size {len(nfo_data)}')
            if nfo_file is not None:
                imdbfound = False
                if nfo_file.name.endswith('nfo'):
                    regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")
                elif nfo_file.name.endswith('xml'):
                    # regex for kodi/xbmc/xml (?:<IMDB>)(tt\d{7})(?:<\/IMDB>)
                    regex = re.compile(r"(?:<IMDB>)(tt\d{7})(?:<\/IMDB>)")
                else:
                    regex = re.compile(r"http(?:s)?:\/\/(?:www\.)?imdb\.com\/title\/tt\d{7}")

                for line in nfo_data:
                    match = re.search(regex, line)
                    if match:
                        if nfo_file.name.endswith('nfo'):
                            result = match[0]
                        elif nfo_file.name.endswith('xml'):
                            result = 'https://www.imdb.com/title/' + match[1]
                        if verbose:
                            print(f'Found imdb link: {result} in {nfo_file.name}')
                        self.imdb_link = result
                        imdbfound = True
                if not imdbfound:
                    pass
            tend = time.time() - tstart
            if tend >= 3:
                print(f'time {tend} {nfo_file.name}')
                    # print(f'No imdb link found in {nfo_file.name}')
            # print(f'Parsed {linenum} lines')
        # pass

def scan_nfo_files(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            if entry.name.endswith(valid_nfo_files):
                yield entry

def scantree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            if entry.name.endswith(vid_extensions) and entry.stat().st_size > min_filesize:
                yield entry

def scan_subdir(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry

def fix_base_folder(start_dir, file_list):
    # move files from base folder to subdir
    print(f'fix_base_folder')
    need_rescan = False
    for file in file_list:
        if os.path.dirname(file) == start_dir:
            basefilename, extension = os.path.splitext(file)
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
        print(f'Rescan {need_rescan}')
        file_list = []
        for entry in scantree(start_dir):
            file_list.append(entry)
    return file_list

def fix_foldernames(start_dir, file_list):
    # rename files and folders with non-ASCII characters
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
                    print(f'Error renaming FOLDER {old_name} to {unicode_path}')
            need_rescan = True
    if need_rescan:
        print(f'Rescan FOLDERS {need_rescan}')
        file_list = []
        for entry in scantree(start_dir):
            file_list.append(entry)
    return file_list

def fix_filenames(start_dir, file_list):
    # rename files and folders with non-ASCII characters
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
                    # need path
                    os.rename(src=old_name, dst=unicode_path)
                except Exception as e:
                    print(f'Error renaming FILE {old_name} to {unicode_path}')
            need_rescan = True
    if need_rescan:
        print(f'Rescan FILELIST {need_rescan}')
        file_list = []
        for entry in scantree(start_dir):
            file_list.append(entry)
    return file_list

def clean_subfolders(folder_list):
    # clean unwanted files from movie folders
    print('clean_subfolders')
    for subdir in folder_list:
        #are we in a subdir
        search_dir = os.path.dirname(subdir.path)
        if os.path.isdir(search_dir):
            file_list = []
            for entry in scan_subdir(search_dir):
                file_list.append(entry)
        for file in file_list:
            filename = file.name.lower()
            if filename in unwanted_files['txtfiles']:
                print(f'\t{filename} in unwanted txtfiles in subdir {search_dir}')
                if not dry_run:
                    os.remove(file)
            if filename in unwanted_files['images']:
                print(f'\t{filename} in unwanted images in subdir {search_dir}')
                if not dry_run:
                    os.remove(file)
            if filename in unwanted_files['videos']:
                print(f'\t{filename} in unwanted videos in subdir {search_dir}')
                if not dry_run:
                    os.remove(file)

def populate_movielist(file_list):
    print('populate_movielist')
    movie_list = []
    for file in file_list:
        movie = MovieClass(filename = file)
        movie.scan_nfo(movie.path)
        movie_list.append(movie)
    return movie_list

def normalscan(start_dir):
    file_list = []
    #populate movie list from base folder...
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
    parser.add_argument("--path",nargs="?",default="d:/movies",help="Base movie folder",required=True,action="store",)
    parser.add_argument("--dryrun", action="store_true", help="Dry run - no changes to filesystem")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args =  parser.parse_args()
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
    imdbcounter = 0
    for movie in movie_list:
        if movie.imdb_link is not None:
            imdbcounter += 1
    print(f'moviecount: {len(movie_list)} imdblinks {imdbcounter} time {time.time() - t1}')
