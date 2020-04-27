# classes
from threading import Thread
from queue import Queue, Empty
import time
from utils import get_folders, get_folders_non_empty, get_video_filelist, sanatize_filenames, sanatize_foldernames, fix_filenames_files, \
    fix_filenames_path
from nfoparser import get_xml_data, get_xml, get_xml_score
from importmovie import import_movie, import_check_path, import_process_path
import os
import shutil
from shutil import Error

class MainThread(Thread):
    # noinspection PySameParameterValue
    def __init__(self, name, monitor_q=Queue(), base_path='',  verbose=True, dry_run=True):
        Thread.__init__(self)
        self.name = name
        self.monitor_q = monitor_q
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
            try:
                new_movie = self.monitor_q.get_nowait()
                print(f'new_movie found: {new_movie}')
                self.import_from_path(new_movie)
                # self.grab_folder(new_movie)
                self.monitor_q.task_done()
            except Empty:
                pass
            if self.kill:
                return
            if self.verbose:
                pass
                # print(f'MainThread: {self.name} running v:{self.verbose} dr:{self.dry_run}')
            time.sleep(1)

    def join(self, **kwargs):
        self.kill = True
        super().join()

    def grab_folder(self, item):
        print(f'q_process: {item}')
        try:
            # os.rename(src=i.path, dst='d:/moviestest')
            shutil.move(src=str(item), dst=self.base_path)
            # self.import_from_path(item):
        except Error as e:
            print(f'grab_folder: {e}')
        except Exception as e:
            print(f'grab_folder: EXCEPTION {e}')
            # exit(-1)

    def set_base_path(self, base_path):
        if os.path.exists(base_path):
            self.base_path = base_path
            if self.verbose:
                print(f'Set base_path to {self.base_path}')
            self.folder_list = get_folders(self.base_path)
            if self.verbose:
                print(f'Update folder_list from {self.base_path}')
        else:
            print(f'set_base_path {base_path} not found')

    def populate_movies(self):
        # get new xml's
        self.update_xml_list()
        if self.verbose:
            print(f'populate_movies from {self.base_path} {len(self.folder_list)} {len(self.xml_list)}')
        # start fresh
        self.movie_list = [MovieClass(movie_data=get_xml_data(file), movie_path=os.path.dirname(file), movie_xml=file) for file in
                           self.xml_list]
        if self.verbose:
            print(f'Found {len(self.movie_list)} movies ')

    def update_xml_list(self):
        self.update_folders()
        self.xml_list = [get_xml(movie_path) for movie_path in self.folder_list if get_xml(movie_path) is not None]

    def get_status(self):
        self.folder_list = get_folders(self.base_path)
        if self.folder_list is not None:
            fsize = len(self.folder_list)
        else:
            fsize = 0
        print(f'MainThread: {self.name} running v:{self.verbose} dr:{self.dry_run} f:{fsize} bp:{self.base_path}')

    def update(self):
        # full refresh
        self.update_folders()
        self.populate_movies()

    def update_folders(self):
        # scan base folder for movie folders
        if self.folder_list is not None:
            fsize = len(self.folder_list)
        else:
            fsize = 0
        self.folder_list = get_folders(self.base_path)
        if self.verbose:
            print(f'Update_folders {fsize} {len(self.folder_list)}')

    def dump_folders(self):
        # dumo our list of movie folders
        if self.folder_list:
            for f in self.folder_list:
                print(f'{f.path}')

    def dump_movies(self):
        # dump movie list
        print('dumping movies')
        self.populate_movies()
        for movie in self.movie_list:
            # print(f"{movie.movie_data['movie']['id']}")
            try:
                print(f'p: {movie.get_path()} t: {movie.get_title()} y: {movie.get_year()} imdb: {movie.get_imdb_id()} xml_score: {movie.get_xml_score()}')
            except TypeError as e:
                print(f'dump_movies TypeError {movie.moviepath} {e}')
            except Exception as e:
                print(f'dump_movies other exception {movie.moviepath} {e}')

    def fix_path_names(self, input_folder=None):
        # for movie folder names only
        # extract info from xml and rename paths and folder in self.folder_list or input_folder
        # do nothing if no valid xml info was found

        if input_folder is None:
            self.update_folders()
            for movie_folder in self.folder_list:
                fix_filenames_path(movie_folder, self.base_path, self.verbose, self.dry_run)
        else:
            fix_filenames_path(input_folder, self.base_path, self.verbose, self.dry_run)

    def fix_file_names(self, input_folder=None):
        # for video filenames only within movie folder
        # extract info from xml and rename paths and folder in self.folder_list or input_folder
        # do nothing if no valid xml info was found
        if input_folder is None:
            if self.verbose:
                print(f'fix_file_names: ALL')
            self.update_folders()
            for movie_folder in self.folder_list:
                fix_filenames_files(movie_folder, self.base_path, self.verbose, self.dry_run)
        else:
            if self.verbose:
                print(f'fix_file_names: {input_folder}')
            fix_filenames_files(input_folder, self.base_path, self.verbose, self.dry_run)

    def clean_path(self, movie_path):
        # scan movie_path for unwanted files, move to junkignore subfolder if found
        if self.verbose:
            print(f'clean_path: {movie_path}')

    def import_from_path(self, import_path):
        if import_check_path(import_path):
            if self.verbose:
                print(f'Importing from path: {import_path}')
            # todo fix : attemt to get base movie name from import_path
            import_name = import_path.parts[-1] # os.path.dirname(import_path).split('\\')[-1]
            if os.path.exists(self.base_path + '\\' + import_name):
                if self.verbose:
                    print(f'{import_name} already exists, not importing.')
            else:
                imported_movie_path = import_movie(self.base_path, import_path, import_name, self.verbose, self.dry_run)
                if imported_movie_path is not None:
                    print(f'Import successful to {imported_movie_path}')
                    import_process_path(self.base_path, imported_movie_path, self.verbose, self.dry_run)
                else:
                    print(f'Import error')
        else:
            if self.verbose:
                print(f'Nothing to import from path: {import_path}')

class Monitor(Thread):
    def __init__(self, name, monitor_q=Queue(), monitor_path='', base_path='', verbose=True, dry_run=True):
        Thread.__init__(self)
        self.name = name
        self.monitor_q = monitor_q
        self.verbose = verbose
        self.dry_run = dry_run
        self.monitor_path = monitor_path
        self.base_path = base_path
        self.kill = False

    def run(self):
        if self.verbose:
            print(f'monitor: monitoring folder {self.monitor_path} destination base:{self.base_path}')
        while True:
            self.folders = get_folders_non_empty(self.monitor_path)
#            if len(self.folders) >= 1:
            for f in self.folders:
                dest_name = os.path.join(self.base_path, f.parts[-1]) # self.base_path + '/' + os.path.basename(f.path)
                # print(f'monitor: dest: {dest_name}')
                # print(f'monitor: base: {self.base_path}')
                if not os.path.exists(dest_name):
                    # todo file_object = open(entry.path, 'a', 8)
                    # todo check if we can move files before putting into q
                    print(f'monitor: put {f} {f} base: {self.base_path} dest: {dest_name} ')
                    self.monitor_q.put(f)
                else:
                    print(f'monitor: {dest_name} exists')
                        
            if self.kill:
                return
            if self.verbose:
                #pass
                if not self.monitor_q.empty():
                    print(f'monitor: {self.name} running v:{self.verbose} dr:{self.dry_run} {len(self.folders)}')
            time.sleep(1)

    def join(self, **kwargs):
        self.kill = True
        super().join()

class MovieClass(object):
    def __init__(self, movie_data, movie_path, movie_xml):
        self.movie_data = movie_data
        self.moviepath = movie_path  # os.path.dirname(file)
        self.moviefile = get_video_filelist(self.moviepath)
        self.movie_xml = movie_xml
        self.xml_score = get_xml_score(self.movie_xml)

    def get_path(self):
        # return str path to movie
        return str(self.moviepath)

    def get_videofile(self):
        # return str full path of videofile
        return str(self.moviefile.name)

    def get_video(self):
        # return direntry of movie
        return self.moviefile

    def get_title(self):
        return self.movie_data.get('title') or self.movie_data.get('OriginalTitle') or None

    def get_year(self):
        return self.movie_data.get('year') or self.movie_data.get('ProductionYear') or None

    def get_imdb_id(self):
        if type(self.movie_data.get('id')) == list:
            return self.movie_data.get('id')[0]
        else:
            return self.movie_data.get('id') or self.movie_data.get('IMDbId') or None

    def get_xml_score(self):
        return self.xml_score

if __name__ == '__main__':
    pass
