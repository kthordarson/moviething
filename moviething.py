# moviething
''' 
rename files to match movie title
check subtitles, dl missing
gather information about video codec / quality
delete samples files and other extra files
extract movie info from nfo/xml files
scrape missing info from imdb/other sources
in case of multiple nfo/xml merge into one
 '''
import argparse
import os
import shutil
import glob
import time
import unidecode
from threading import Thread
from multiprocessing import Process, Queue, JoinableQueue
from nfoparser import (
    get_nfo_data, get_xml_data, is_valid_nfo,
    is_valid_txt, is_valid_xml, merge_xml_files, sanatized_string,
    get_xml_movie_title, nfo_extractor, check_nfo_files, valid_nfo_files)
from utils import scan_path, get_folders, fix_names, clean_subfolder
from scrapers import imdb_scrape
from defs import *

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
        # scan base folder for movie folders
        self.folder_list = get_folders(self.base_path)
    def dump_folders(self):
        # dumo our list of movie folders
        if self.folder_list:
            for f in self.folder_list:
                print(f'{f}')


class MovieClass(object):
    def __init__(self, filename):
        self.filename = filename
        self.basename, self.extension = os.path.splitext(filename)
        self.path = os.path.dirname(filename)
        self.xml_data = None





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
    # folder_list contains a list of subfolders from start_dir, one movie per subfolder    
    folder_list = get_folders(start_dir)
    for folder in folder_list:
        # clean subfolders of unwanted extra files
        clean_subfolder(folder)
        # fix folder/file names from xml info
        fix_names(folder)
    # exit(-1)
    return

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
