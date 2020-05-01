# classes
from threading import Thread, active_count
from queue import Queue, Empty
import time
import os
import sys


from utils import get_folders, get_folders_non_empty, get_video_filelist
from nfoparser import get_xml_data, get_xml, get_xml_score, check_xml
from importmovie import import_movie, import_check_path, import_process_path
from scrapers import scrape_movie, scrape_by_id
import shutil
from shutil import Error
from pathlib import Path
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
        self.folder_list = get_folders(self.base_path)
        if self.folder_list is not None:
            self.update()
        while True:
            try:
                # [0] f: new movie
                # [0] s: scrape
                q_item = self.monitor_q.get_nowait()
                # new_movie = self.monitor_q.get_nowait()
                if q_item[0] == 'f':
                    new_movie = q_item[1]
                    print(f'new_movie found: {new_movie}')
                    self.import_from_path(new_movie)
                    # self.grab_folder(new_movie)
                    self.monitor_q.task_done()
                if q_item[0] == 's':
                    pass
                    # self.scrape_threads = list()
                    # self.scrape_threads = q_item[1]
                    # for t in self.scrape_threads:
                    #     t.start()
                    # scrape_t.daemon = False
                    # scrape_t.start()
                    # self.scrape_threads.append(scrape_t)
                    # scrape_t.start()
                    # self.monitor_q.task_done()
                    # pass
            except Empty:
                pass
            if self.kill:
                return
            if self.verbose:
                # self.get_status()
                pass
            time.sleep(1)

    def join(self, **kwargs):
        self.kill = True
        super().join()

    def set_base_path(self, base_path):
        if base_path.exists():
            self.base_path = base_path
            if self.verbose:
                print(f'Set base_path to {self.base_path}')
            self.folder_list = get_folders(self.base_path)
            if self.verbose:
                print(f'Update folder_list from {self.base_path}')
        else:
            print(f'set_base_path {base_path} not found')

    def populate_movies(self):
        # make the movie list from our movie folders and xml's found within
        # get new xml's
        # self.update_xml_list()
        # self.scrape_threads = list()
        if self.verbose:
            print(f'populate_movies from {self.base_path} folders: {len(self.folder_list)} xml: {len(self.xml_list)}')
        # start fresh
        self.movie_list = [MovieClass(movie_data=get_xml_data(file), movie_path=file.parent, movie_xml=file) for file in
                           self.xml_list]
        if self.verbose:
            print(f'Found {len(self.movie_list)} movies ')

    def update_xml_list(self):
        # refresh xml list
        # todo check/repair/convert xml if needed.... ?
        [check_xml(movie_path) for movie_path in self.folder_list]
        self.xml_list = [get_xml(movie_path) for movie_path in self.folder_list if get_xml(movie_path) is not None]

    def get_status(self):
        self.folder_list = get_folders(self.base_path)
        if self.folder_list is not None:
            fsize = len(self.folder_list)
        else:
            fsize = 0
        # print(f'MainThread: {self.name} running v:{self.verbose} dr:{self.dry_run} f:{fsize} bp:{self.base_path}')
        print(f'MainThread: {self.name} running v:{self.verbose} dr:{self.dry_run} f:{fsize} bp:{self.base_path} active threads: {active_count()}')

    def update(self):
        # full refresh
        self.update_folders()
        self.update_xml_list()
        self.populate_movies()

    def update_folders(self):
        # scan base folder for movie folders
        self.folder_list = get_folders(self.base_path)

    def dump_folders(self):
        # dumo our list of movie folders
        _ = [print(f'{f}') for f in self.folder_list]
#        if self.folder_list:
#            for f in self.folder_list:
#                print(f'{f.path}')

    def dump_movies(self):
        # dump movie list
        # print('dumping movies')
        # self.populate_movies()
        for movie in self.movie_list:
            try:
                movie.dump_info()
            except Exception as e:
                print(f'dump_movies: error {e}')

    def dump_movie_list(self):
        try:
            _ = [print(f'Title: {movie.movie_title} Year: {movie.movie_year} imdb: {movie.imdb_id} x: {movie.xml_score}') for movie in self.movie_list]
        except Exception as e:
            print(f'dump_movie_list: error {e}')

    def import_from_path(self, import_path):
        if import_check_path(import_path):
            if self.verbose:
                print(f'Importing from path: {import_path}')
            # todo fix : attemt to get base movie name from import_path
            import_name = import_path.parts[-1]
            dest_path = Path.joinpath(self.base_path, import_name)
            if dest_path.exists(): 
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
    
    def scrape(self, imdbid):
        # check if we have imdbid in our list, scrape 
        # tt0066921
        print(f'Manual scrape {imdbid}')
        movie_path = [movie.moviepath for movie in self.movie_list if movie.imdb_id == imdbid]
        if len(movie_path) >= 1:
            scrape_by_id(imdbid, movie_path[0])

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
                dest_name = Path.joinpath(self.base_path, f.parts[-1]) 
                # print(f'monitor: dest: {dest_name}')
                # print(f'monitor: base: {self.base_path}')
                if not Path(dest_name).exists():
                    # todo file_object = open(entry.path, 'a', 8)
                    # todo check if we can move files before putting into q
                    print(f'monitor: put {f} {f} base: {self.base_path} dest: {dest_name} ')
                    self.monitor_q.put(('f',f))
                        
            if self.kill:
                return
            if self.verbose:
                pass
                # print(f'monitor: {self.name} running v:{self.verbose} dr:{self.dry_run} {len(self.folders)}')
            time.sleep(3)

    def join(self, **kwargs):
        self.kill = True
        super().join()

class MovieClass(object):
    def __init__(self, movie_data, movie_path, movie_xml):
        # self.movie_data = movie_data
        self.moviepath = movie_path 
        self.moviefile = get_video_filelist(self.moviepath)
        self.movie_xml = movie_xml
        self.xml_score = get_xml_score(self.movie_xml)
        if movie_data is not None:
            self.movie_data = movie_data
            self.do_update()
        else:
            self.movie_data = None
            self.movie_title = None
            self.movie_year = None
            self.imdb_id = None

    def do_update(self):
        # update fields from movie_data
        # print('doing update')
        self.movie_title = self.movie_data.get('title') or self.movie_data.get('OriginalTitle') or self.movie_data.get('originaltitle')
        self.movie_year = self.movie_data.get('year') or self.movie_data.get('ProductionYear')  or self.movie_data.get('productionyear')
        self.imdb_id = self.movie_data.get('imdb') or self.movie_data.get('id') or self.movie_data.get('IMDBiD') or self.movie_data.get('IMdbId')


    def get_path(self):
        # return str path to movie
        return self.moviepath

    def get_videofile(self):
        # return str full path of videofile
        return self.moviefile

    def get_video(self):
        # return direntry of movie
        return self.moviefile
   
    def dump_info(self):
        for tag in self.movie_data:
            try:
                if tag:
                    print(f'\t\t{tag} : {self.movie_data[tag]}')
            except Exception as e:
                print(f'dump_info: error {e}')
        #pass

if __name__ == '__main__':
    pass
