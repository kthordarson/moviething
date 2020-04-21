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
    
    def fix_names(self):
        # scan self.folder_list for valid xml, extract title and year, compare folder and filename, rename if needed
        if self.folder_list is None:
            self.update_folders()
        # first iteration check and correct movie folder name
        for movie_path in self.folder_list:
            xml = get_xml(movie_path)
            if xml is not None:
                movie_title = get_xml_movie_title(xml)
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
            # populate list of video files in each movie folder
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
    def __init__(self, filename):
        self.filename = filename
        self.basename, self.extension = os.path.splitext(filename)
        self.path = os.path.dirname(filename)
        self.xml_data = None
