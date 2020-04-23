# classes
from threading import Thread
import time
from utils import *
from nfoparser import *
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
        # get new xml's
        self.update_xml_list()
        # start fresh
        self.movie_list = []
        for file in self.xml_list:
            # create movie list from data found in xml files
            moviepath = os.path.dirname(file)
            videofile = get_video_filelist(moviepath)
            movie = MovieClass(get_xml_data(file), moviepath, videofile)            
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
            #print(f"{movie.movie_data['movie']['id']}")
            try:
                print(f'p: {movie.get_path()} t: {movie.get_title()} y: {movie.get_year()} imdb: {movie.get_imdb_id()}')
            except TypeError as e:
                print(f'dump_movies TypeError {movie.get_path()} {e}')
            except Exception as e:
                print(f'dump_movies other exception {movie.get_path()} {e}')
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
                sanatize_foldernames(movie_folder, verbose=self.verbose, dry_run=self.verbose)
        else:
            sanatize_foldernames(input_folder, verbose=self.verbose, dry_run=self.verbose)
        # refresh again incase of renames...
        self.update_folders()

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
            self.update_folders()
            for movie_folder in self.folder_list:
                fix_filenames_files(movie_folder, self.base_path, self.verbose, self.dry_run)
        else:
            fix_filenames_files(input_folder, self.base_path, self.verbose, self.dry_run)

    def clean_path(self, movie_path):
        # scan movie_path for unwanted files, move to junkignore subfolder if found
        if self.verbose:
            print(f'clean_path: {movie_path}')

    def import_from_path(self, import_path):
        if self.verbose:
            print(f'Importing from path: {import_path}')
        check_import_path(import_path)

class MovieClass(object):
    def __init__(self, movie_data, moviepath, moviefile):
        self.movie_data = movie_data
        self.moviepath = moviepath
        self.moviefile = moviefile

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
        title = None
        try:
            title = self.movie_data.get('movie')['title'] or None
            return title
        except TypeError:
            title = self.movie_data.get('movie')['OriginalTitle'] or None
            return title
        except Exception as e:
            print(f'get_title err {self.moviepath}  {e}')
            return None

    def get_year(self):
        year = None
        try:
            year = self.movie_data.get('movie')['year'] or None
            return year
        except TypeError:
            year = self.movie_data.get('movie')['ProductionYear'] or None
            return year
        except Exception as e:
            print(f'get_year {self.moviepath} err {e}')
        
    def get_imdb_id(self):
        id = None
        try:
            id = self.movie_data.get('movie')['id'] or None
            return id
        except TypeError:
            id = self.movie_data.get('movie')['IMDbId'] or None
            return id
        except Exception as e:
            print(f'get_imdb_id {self.moviepath}  ERR {e}')
            return None
