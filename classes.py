# classes
import json
import time
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from threading import Thread, active_count
from typing import List, Optional

from importmovie import (
    import_check_path, import_movie, import_process_files, import_process_path)
from movieclass import Movie
from nfoparser import check_xml, get_xml, get_xml_data, get_xml_moviedata
# from scraper_imdb import scrape_by_id, scrape_movie
from scraper_tmdb import TmdbScraper
from utils import get_folders, get_folders_non_empty, get_video_filelist


class MainThread(Thread):
    # noinspection PySameParameterValue
    def __init__(self, name='', monitor_q=Queue(), base_path='', verbose=True, dry_run=True):
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
                # print(f'q items put {self.monitor_q.qsize()}')
                q_item = self.monitor_q.get_nowait()
                # new_movie = self.monitor_q.get_nowait()
                if q_item[0] == 'f':
                    new_movie = q_item[1]
                    # print(f'new_movie found: {new_movie}')
                    self.import_from_path(new_movie)
                    # self.grab_folder(new_movie)
                    # q_item.update
                    self.monitor_q.task_done()
                    # self.update()
                    # print(f'q items task done {self.monitor_q.qsize()}')
                if q_item[0] == 's':
                    pass
            except Empty:
                # print(f'q empty')
                # time.sleep(0.5)
                pass
            if self.kill:
                return
            if self.verbose:
                # self.get_status()
                pass
            # time.sleep(1)

    def join(self, timeout=None):
        print(f'Stopping.....')
        self.kill = True
        # self.monitor_q.join()
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
        # self.movie_list = [MovieClass(movie_data=get_xml_data(file), movie_path=file.parent, movie_xml=file) for file in self.xml_list]
        # self.movie_list = [MovieClass(movie_data=get_xml_moviedata(file), movie_path=file.parent) for file in self.xml_list]
        if self.verbose:
            print(f'Found {len(self.movie_list)} movies ')

    def update_xml_list(self):
        # refresh xml list
        # todo check/repair/convert xml if needed.... ?
        _ = [check_xml(movie_path) for movie_path in self.folder_list]
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
        # self.update_xml_list()
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
            _ = [print(f'Title: {movie.title} Year: {movie.release_date} imdb: {movie.imdb_id}') for movie in self.movie_list]
        except Exception as e:
            print(f'dump_movie_list: error {e}')

    def import_from_path(self, import_path):
        if import_check_path(import_path):
            if self.verbose:
                print(f'Importing from path: {import_path}')
            # todo fix : attemt to get base movie name from import_path
            movie_data = import_movie(self.base_path, import_path, self.verbose, self.dry_run)
            if movie_data:
                movie = MovieClass(movie_data=movie_data, movie_path=import_path)
            else:
                print(f'import_from_path: got no movie_data from {import_path}')

    def scrape(self, imdbid):
        pass
        # check if we have imdbid in our list, scrape
        # tt0066921
        # print(f'Manual scrape {imdbid}')
        # movie_path = [movie.moviepath for movie in self.movie_list if movie.imdb_id == imdbid]
        # if len(movie_path) >= 1:
        #     scrape_by_id(imdbid, movie_path[0])


class Monitor(Thread):
    def __init__(self, name='', monitor_q=Queue(), monitor_path=''):
        Thread.__init__(self)
        self.name = name
        self.monitor_q = monitor_q
        self.monitor_path = monitor_path
        self.kill = False
        self.folders = None

    # watch monitor_path for new items/movies, if folder contains video (extension and min size), check for write access (can move?)
    # put on monitor_q for processing
    def run(self):
        while True:
            self.folders = get_folders_non_empty(self.monitor_path)
            # print(f'monitor: {self.folders}')
            # time.sleep(1)
            # print(f'monitor: {self.folders}')
            for f in self.folders:
                # print(f'monitor sending to q: {f} {self.folders}')
                self.monitor_q.put_nowait(('f', f))
                self.folders.pop(self.folders.index(f))
                # print(f'monitor popped: {f} {self.folders}')
                # time.sleep(1)
            if self.kill:
                return

    def join(self, timeout=None):
        self.kill = True
        super().join()


class MovieClass(Movie):
    def __init__(self, movie_data, movie_path):
        super().__init__(**movie_data)
        # self.movie_data = movie_data
        self.moviepath = movie_path

    def do_update(self):
        pass

    def get_path(self):
        # return str path to movie
        return self.moviepath

    def get_videofile(self):
        pass
        # return str full path of videofile
        # return self.moviefile

    def get_video(self):
        pass
        # return direntry of movie
        # return self.moviefile

    def dump_info(self):
        pass


if __name__ == '__main__':
    print('classes')
    # f = 'test.xml'
    # d = get_xml_moviedata(f)
    # m = MovieClass(movie_data=d, movie_path=f)
    # print(m.title)
