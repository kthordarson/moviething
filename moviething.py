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
from nfoparser import *
from utils import *
from scrapers import imdb_scrape
from defs import *
from classes import *

def check_main_thread(thread):
    return thread.isAlive()


def stop_main(thread):
    thread.join()
    exit(0)


def main_program(args):
    # thread = list()
    main_thread = MainThread('MainThread', base_path = args.path, verbose = args.verbose, dry_run=args.dryrun)
    main_thread.setDaemon = False
    main_thread.start()
    while check_main_thread(main_thread):
        try:
            cmd = input('>')
            if cmd[:1] == 'i':
                main_thread.get_status()
            if cmd[:4] == 'quit' or cmd[:1] == 'q':
                stop_main(main_thread)
            if cmd[:4] == 'dump':
                main_thread.dump_folders()
            if cmd[:6] == 'movies':
                main_thread.dump_movies()
            if cmd[:2] == 'uf':
                main_thread.update_folders()
            if cmd[:7] == 'fixpath':
                main_thread.fix_path_names()
            if cmd[:7] == 'fixfile':
                main_thread.fix_file_names()
        except KeyboardInterrupt:
            stop_main(main_thread)
        except Exception as e:
            print(f'Exception in main_program {e}')

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
        # basemovie_dir = args.path
    if args.import_path:
        print(f'Importing from: {args.import_path}')
        # import_path = args.import_path
    else:
        print(f'Dry run: {args.dryrun}')
        # dry_run = True
#    else:
#        print(f'Dry run: {args.dryrun}')
        # dry_run = False
    # if args.verbose:
    #     verbose = True
    # else:
    #     verbose = False
    return parser.parse_args()

if __name__ == '__main__':
    t1 = time.time()
    args = get_args()
    verbose = args.verbose
    dry_run = args.dryrun
    main_program(args)
