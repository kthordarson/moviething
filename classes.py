# classes
from threading import Thread
import os
import time

from nfoparser import *
from utils import *

class MainThread(Thread):
    def __init__ (self, name, base_path='d:/movies', verbose=True, dry_run=True):
        Thread.__init__(self)
        self.name = name
        self.verbose = verbose
        self.dry_run = dry_run
        self.base_path = base_path
        self.folder_list = None
        self.kill = False
        self.movie_list = []
        self.xml_list = []
    def run(self):
        if self.verbose:
            print(f'MainThread: {self.name} starting bp: {self.base_path}')
        if self.folder_list is None:
            self.folder_list = get_folders(self.base_path)
        if self.verbose:
            print(f'First scan {len(self.folder_list)}')
        if self.folder_list is not None:
            self.populate_movies()
        while True:
            if self.kill:
                return
            if self.verbose:
                pass
                # print(f'MainThread: {self.name} running v:{self.verbose} dr:{self.dry_run}')
            time.sleep(1)

    def join(self):
        self.kill = True
        super().join()

    def populate_movies(self):
        if self.verbose:
            print(f'populate_movies from {self.base_path} {len(self.folder_list)}')
        self.update_xml_list()
        for file in self.xml_list:
            movie = MovieClass(get_xml_data(file))
            self.movie_list.append(movie)
            # print(movie)
        if self.verbose:
            print(f'Found {len(self.movie_list)} movies ')

    def update_xml_list(self):
        self.xml_list = []
        self.update_folders()
        for movie_path in self.folder_list:
            xml = get_xml(movie_path)
            if xml is not None:
                self.xml_list.append(xml)
                # print(xml)

    def get_status(self):
        self.folder_list = get_folders(self.base_path)
        if self.folder_list is not None:
            fsize = len(self.folder_list) or None
        print(f'MainThread: {self.name} running v:{self.verbose} dr:{self.dry_run} f:{fsize}')

    def update_folders(self):
        # scan base folder for movie folders
        if self.folder_list is not None:
            fsize = len(self.folder_list)
        self.folder_list = get_folders(self.base_path)
        if self.verbose:
            print(f'Update_folders {fsize} {len(self.folder_list)}')

    def dump_folders(self):
        # dumo our list of movie folders
        if self.folder_list:
            for f in self.folder_list:
                print(f'{f}')
    
    def dump_movies(self):
        # dump movie list
        print('dumping movies')
        self.populate_movies()
        for movie in self.movie_list:
            print(f"{movie.movie_data['movie']['id']}")

    def sanatize_filenames(self, input_folder=None):
        # remove [xxx] from all filenames
        # refresh movie_folder
        self.update_folders()
        if input_folder is None:
            for movie_folder in self.folder_list:
                sanatize_filenames(movie_folder)
        else:
            sanatize_filenames(input_folder)
        # refresh again incase of renames...
        self.update_folders()
        
    def sanatize_foldernames(self, input_folder=None):
        # remove [xxx] from all foldernames
        # refresh movie_folder
        self.update_folders()
        if input_folder is None:
            for movie_folder in self.folder_list:
                sanatize_foldernames(movie_folder)
        else:
            sanatize_foldernames(input_folder)
        # refresh again incase of renames...
        self.update_folders()

    def fix_names(self):
        # scan self.folder_list for valid xml, extract title and year, compare folder and filename, rename if needed
        # todo possibly move this to MovieClass
        if self.folder_list is None:
            self.update_folders()
        # first iteration check and correct movie folder name
        for movie_path in self.folder_list:
            xml = get_xml(movie_path)
            if xml is not None:
                movie_title = get_xml_movie_title(xml)
                self.xml_list.append(xml)
                if movie_title is not None:
                    
                    if os.path.basename(os.path.dirname(xml)) == movie_title:
                        pass
                        # print(f'Movie folder name is correct {os.path.dirname(xml)}')
                    else:
                        if verbose:
                            print(f'Movie folder name is incorrect {os.path.dirname(xml)}')
                        if not self.dry_run:
                            try:
                                dest = self.base_path + '/' + movie_title
                                os.rename(src=os.path.dirname(xml), dst=dest)
                                print(f'Renamed {os.path.dirname(xml)} to {dest}')
                            except Exception as e:
                                print(f'fix_names rename failed {e}')
        # second iteration check and rename movie filenames in self.folder_list
        self.update_folders() # update if something was renamed in first iteration
        for movie_path in self.folder_list:
            # populate list of video files in each movie folder, files with valid video extension only from each subfolder
            video_file = get_video_filelist(movie_path)
            if video_file is not None:
                vidname, ext = os.path.splitext(video_file)
                # print(f'fix_names file {video_file} {movie_path} {e}')
                # break
            xml = get_xml(movie_path)
            if xml is not None and video_file is not None:
                movie_title = get_xml_movie_title(xml)
                if movie_title is not None:
                    correct_filename = movie_title + ext
                    org_name = os.path.basename(video_file)
                    if org_name == correct_filename:
                        pass
                    else:
                        if self.verbose:
                            print(f'Movie filename name is incorrect old: {org_name} correct: {correct_filename}')
                        if not self.dry_run:
                            try:
                                dest = os.path.dirname(video_file) + '/' + correct_filename
                                os.rename(src=video_file, dst=dest)
                                print(f'Renamed {os.path.dirname(xml)} to {dest}')
                            except Exception as e:
                                print(f'fix_names rename failed {e}')

    
    def clean_path(self, movie_path):
        # scan movie_path for unwanted files, move to junkignore subfolder if found
        if self.verbose:
            print(f'clean_path: {movie_path}')

class MovieClass(object):
    def __init__(self, movie_data):
        self.movie_data = movie_data