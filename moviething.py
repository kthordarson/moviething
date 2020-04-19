# moviething
# todo
# rename files to match movie title
# check subtitles, dl missing
# gather information about video codec / quality
# delete samples files
# extract movie info from nfo/xml files
# in case of multiple nfo/xml merge into one
import argparse
import codecs
import hashlib
import os
import platform
import re
import string
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
import time
import requests
import unidecode

from nfoparser import get_nfo_data, is_valid_nfo, get_xml_dict, etree_to_dict, get_xml_data, is_valid_xml, is_valid_txt, merge_nfo_files

vid_extensions = (
    'mp4', 'mpeg', 'mpg', 'mp2', 'mpe', 'mvpv', 'mp4', 'm4p', 'm4v', 'mov', 'qt', 'avi', 'ts', 'mkv', 'wmv', 'ogv', 'webm', 'ogg'
)

min_filesize = 40000000

valid_input_string_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

# unwanted files / subdirs
# will be deleted automatically
unwanted_files = dict(
    subdirs=("sample", "samples"),
    txtfiles=("readme.txt", "torrent downloaded from extratorrent.cc.txt", "rarbg.com.txt", "torrent-downloaded-from-extratorrent.cc.txt",
              "ahashare.com.txt", "torrent downloaded from demonoid.com - copy.txt", "torrent downloaded from demonoid.com.txt"),
    images=("www.yify-torrents.com.jpg", "screenshot", "www.yts.am.jpg"),
    videos=("rarbg.com.mp4", "sample.mkv")
)

valid_nfo_files = ('nfo', 'xml', 'txt')

def sanatized_string(input_string, whitelist=valid_input_string_chars, replace=''):
    # replace spaces
    for r in replace:
        input_string = input_string.replace(r,'_')
    
    # keep only valid ascii chars
    cleaned_input_string = unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode()
    
    # keep only whitelisted chars
    cleaned_input_string = ''.join(c for c in cleaned_input_string if c in whitelist)
    if len(cleaned_input_string)>char_limit:
        print("Warning, input_string truncated because it was over {}. input_strings may no longer be unique".format(char_limit))
    return cleaned_input_string[:char_limit]

class MovieClass(object):
    def __init__(self, filename):
        self.filename = filename
        self.basename, self.extension = os.path.splitext(filename)
        self.path = os.path.dirname(filename)
        self.imdb_link = None
        self.nfo_file_count = 0
        self.nfo_files = []
        self.xml_data = None
        self.nfo_data = None
        self.rename_file_required = False
        self.rename_path_required = False


    def scan_nfo(self, path):
        # scan folder containing this movie for valid nfo files
        tstart = time.time()
        nfofiles = scan_nfo_files(path)
        for nfo in nfofiles:
            if nfo.name.endswith('xml'):
                try:
                    xml_data = get_xml_data(nfo)
                    movie_data = xml_data.get('movie') or xml_data.get('Title', None)
                    #xml_data = etree_to_dict(nfo)
                    self.xml_data = movie_data
                    # self.nfo_file_count += 1
                    self.nfo_files.append(nfo)
                except Exception as e:
                    print(f'Error parsing XML {nfo.path} {e}')
                    exit(-1)
                    #xml_data = None
            if nfo.name.endswith('nfo'):
                try:
                    nfo_data = get_nfo_data(nfo)
                    if verbose and nfo_data is not None:
                        pass
                        # print(f'Got nfo {type(nfo_data)} {len(nfo_data)}')
                    if nfo_data is not None:
                        self.nfo_data = nfo_data
                        # self.nfo_file_count += 1
                        self.nfo_files.append(nfo)
                    if nfo_data is None:
                        print(f'No NFO data extracted from {nfo.path}')
                        if not dry_run:
                            # todo remove useless nfo file
                            pass
                except Exception as e:
                    print(f'Error parsing NFO {nfo.path} {e}')
                    exit(-1)

            
    def populate_info(self):
        # gather info to ensure correct folder/filenames
        if self.xml_data is not None:
            if verbose:
                pass
                #print(f'Gathering xml data {self.filename.name} {self.nfo_files}')
            self.imdb_id = self.xml_data.get('id', None) #self.xml_data['id']
            if self.imdb_id is None:
                self.imdb_id = self.xml_data.get('IMDbId', None)
            if type(self.imdb_id) == list:
                self.imdb_id = self.imdb_id[0]
            if self.imdb_id is not None:
                if verbose:
                    print(f'IMDB found {self.imdb_id} for {self.filename.name}')
                self.imdb_link = 'https://www.imdb.com/title/' + self.imdb_id
            self.title = self.xml_data.get('title', None) # self.xml_data['title']
            self.year =self.xml_data.get('year', None) # self.xml_data['year']
            self.rename_file_required = False
            self.rename_path_required = False
            if self.title is not None and self.year is not None: # and self.imdb_id is not None:
                sanatized_title = sanatized_string(self.title)
                self.correct_pathname = sanatized_title + ' (' + self.year + ')'
                self.correct_filename = self.correct_pathname + self.extension
                if self.correct_filename != self.filename.name:
                    self.rename_file_required = True
                    self.rename_movie_file()
                if self.correct_pathname != os.path.basename(self.path):
                    self.rename_path_required = True
                    self.rename_movie_path()
                # todo check if actual path/filename matches correct names gathered from nfo/xml and correct if needed
        elif self.nfo_data is not None:
            if verbose:
                print(f'Gathering nfo data {self.filename.name} {self.nfo_files}')
            self.imdb_link = self.nfo_data['imdb_link']
            if verbose:
                print(f'imdb link from nfo: {self.imdb_link}')

        else:
            pass
            #print(f'No nfo/xml data for {self.filename.name}')
    def rename_movie_path(self):
        if verbose:
            print(f'Folder old: {os.path.basename(self.path)} corr: {self.correct_pathname}')
        if not dry_run and self.rename_path_required:
            try:
                src_path = os.path.dirname(self.filename.path)
                dst_path = os.path.dirname(self.path) + '/' + self.correct_pathname
                os.rename(src=src_path, dst=dst_path)
                self.rename_path_required = False
                #self.filename.path = dst_path
            except Exception as e:
                print(f'Rename path failed {e}')
                
                #exit(-1)
        #pass
    def rename_movie_file(self):
        if verbose:
            print(f'Filename old: {self.filename.name} corr: {self.correct_filename} ')
        if not dry_run and self.rename_file_required:
            try:
                src_file = os.path.dirname(self.basename) + '/' + self.filename.name
                dst_file = os.path.dirname(self.basename) + '/' + self.correct_filename
                os.rename(src=src_file, dst=dst_file)
                #self.filename.name = dst_file
                self.rename_file_required = False
            except AttributeError:
                print(f'Rename err {e}')
                
            except Exception as e:
                print(f'Rename file failed {e}')
                
                #exit(-1)
        #pass
                
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

def check_nfo_files(file_list):
    # todo
    # scan path for multiple / invalid nfo / xml files
    # merge into one valid xml
    # delete remaining nfo / xml
    invalid_file_counter = 0
    invalid_files = []
    for file in file_list:
        print(f'Scanning NFO/XML/TXT for {file.path}')
        nfolist = scan_nfo_files(os.path.dirname(file.path))
        nfocounter = 0
        merge_needed = False
        files_to_merge = []
        for nfo in nfolist:
            nfocounter += 1
            if nfo.name.endswith('nfo'):
                if not is_valid_nfo(nfo):
                    # not valid files, delete
                    # todo delete, rename for now...
                    invalid_file_counter += 1
                    invalid_files.append(nfo)
                    if verbose:
                        print(f'Found invalid NFO {nfo.path}')
                    new_name = nfo.path + '.invalid'
                    if not dry_run:
                        os.rename(src=nfo, dst=new_name)
                    #pass
                else:
                    files_to_merge.append(nfo)
            if nfo.name.endswith('xml'):
                if not is_valid_xml(nfo):
                    # not valid xml, delete
                    invalid_file_counter += 1
                    invalid_files.append(nfo)
                    if verbose:
                        print(f'Found invalid NFO {nfo.path}')
                    new_name = nfo.path + '.invalid'
                    if not dry_run:
                        os.rename(src=nfo, dst=new_name)
                else:
                    files_to_merge.append(nfo)
                    
            if nfo.name.endswith('txt'):
                if not is_valid_txt(nfo):
                    invalid_file_counter += 1
                    invalid_files.append(nfo)
                    if verbose:
                        print(f'Found invalid txt {nfo.path}')
                    new_name = nfo.path + '.invalid'
                    if not dry_run:
                        os.rename(src=nfo, dst=new_name)
                    # no imdb link/id found in txt, discard...
                else:
                    files_to_merge.append(nfo)
        if nfocounter > 1:
            #print(f'multiple nfo  {nfocounter} {len(files_to_merge)} founds merge needed {os.path.dirname(nfo)}')
            #print(f'Merging files ... {files_to_merge}')
            merge_needed = True
            merge_nfo_files(files_to_merge)
    exit(-1)

def normalscan(start_dir):
    file_list = []
    # populate movie list from base folder...
    for entry in scantree(start_dir):
        file_list.append(entry)
    # move movies in base folder to subfolders...
    # todo check if file exists in basefolder before calling fix_base_folder
    file_list = fix_base_folder(start_dir, file_list)
    # fix non-ascii foldernames
    file_list = fix_foldernames(start_dir, file_list)
    # fix non-ascii filenames
    file_list = fix_filenames(start_dir, file_list)
    # clean subfolders of unwanted extra files
    clean_subfolders(file_list)
    # check for multiple nfo/xml and merge into one file
    check_nfo_files(file_list)
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
    filerename, folderrename = 0,0
    for movie in movie_list:
        if movie.rename_file_required:
            filerename += 1
        if movie.rename_path_required:
            folderrename += 1
#    for movie in movie_list:
#        print(f'{movie.filename.name} {movie.imdb_link}')
#        if movie.nfo_file_count > 1:
#            print(f'{movie.filename.path} has multiple {movie.nfo_file_count} nfo/xml files')
    print(
        f'moviecount: {len(movie_list)} time {time.time() - t1}')
    print(f'rename files {filerename} folders {folderrename}')
