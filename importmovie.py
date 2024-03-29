import datetime
import shutil
from pathlib import Path
from random import randint

from lxml import etree as et
from xml.dom import minidom

from etree import element
# from ffprobe import get_ffprobe
from nfoparser import (get_xml, get_xml_imdb_id, get_xml_movie_title,
                       get_xml_moviedata, nfo_process_path)
from scraper_tmdb import TmdbScraper
from stringutils import sanatized_string
from utils import get_video_filelist


def import_check_path(import_path, verbose=True, dry_run=True):
    #    if verbose:
    #        print(f'Checking path {import_path}')
    if not import_path.exists():
        # if verbose:
        #     print(f'Import path: {import_path} not found')
        return False
    else:
        # scan all files in import_path
        # - check for videos, nfo/xml, unwanted files, subtitles, etc
        # - check if movie already exists in base_movies
        if get_video_filelist(import_path) is None:
            return False
        else:
            # todo fix this
            # if len(get_nfo_list(import_path)) == 0 and len(get_xml_list(import_path)) == 0:
            #     # no nfo/xml found, make some
            #     print(f'import_check_path: make xml')
            #     data = get_ffprobe(get_video_filelist(import_path))
            #     # root = et.Element('movie')
            #     tree = et.ElementTree(element=data)
            #     xml_name = import_path.parts[-1] + '.xml'
            #     result_file = Path.joinpath(import_path, xml_name)
            #     try:
            #         tree.write(str(result_file))
            #     except Exception as e:
            #         print(f'import_check_path: error saving ffprobe xml {e}')
            return True


# todo import_move return movie_data if successful else None
# 1. copy/move folder to base
# 2. look for imdb id in existing xml/nfo, if imdb id found scrape and write new xml
# 3. process file/path name if scrape success
def import_movie(base_path, import_path, verbose=True, dry_run=True):
    movie_data = None
    dest_path = Path.joinpath(base_path, import_path.parts[-1])
    shutil.move(src=import_path, dst=dest_path)
    # scan all nfo/xml for imdb_id
    xml = get_xml(dest_path)
    if xml is None:
        xml = nfo_process_path(dest_path)
    if xml is None:
        # nothing found
        return None
    else:
        # grab imdbid from xml and scrape from tmdb
        movie_imdb_id = get_xml_imdb_id(xml)
        if movie_imdb_id is None:
            # nothing found in xml....
            movie = dict({'title': import_path.parts[-1]})
            # movie.title = import_path.parts[-1]
            return movie
        else:
            movie_scraper = TmdbScraper()
            movie_scraper.fetch_id(movie_imdb_id)
            movie_year = ' (' + str(
                datetime.datetime.strptime(movie_scraper.movie_data['release_date'], '%Y-%m-%d').year) + ')'
            movie_title = sanatized_string(movie_scraper.movie_data['title'] + movie_year)
            # tree_element = element('movie', movie_scraper.movie_data)
            # tree_root = et.ElementTree(element=tree_element)
            # tree = minidom.Document()
            dataelement = element('movie', movie_scraper.movie_data)
            dd_element = minidom.parseString(et.tostring(dataelement))
            # ddd = minidom.parseString(dd_element)
            pretty_data = dd_element.toprettyxml(indent=' ', encoding='utf-8')
            # jsondata = json.loads(dd_element)
            xml_filename = Path.joinpath(dest_path, movie_title + '.xml')
            if xml_filename.exists():
                target_xml = str(xml_filename) + '.' + str(randint(100, 999)) + '.olddata'
                xml_filename.rename(target_xml)
                # xml_filename = Path(str(target_xml))
            with open(str(xml_filename), mode='wb') as f:
                f.write(pretty_data)
            movie_data = get_xml_moviedata(xml_filename)
            return movie_scraper.movie_data


def import_movie_old(base_path, import_path, import_name, verbose=True, dry_run=True):
    # import_path must only contain one movie
    # example: c:\incoming\new_movie_name\
    if verbose:
        print(f'Starting import process: from {import_path} to {base_path}')
    # make destination path
    dest_path = Path.joinpath(base_path, import_name)
    # if dry, only copy from import
    if dry_run:
        try:
            shutil.copytree(src=import_path, dst=dest_path)
            return dest_path
        except Exception as e:
            print(f'Could not copy from {import_path} to {dest_path} {e}')
            return None
    else:
        try:
            shutil.move(src=import_path, dst=dest_path)
            return dest_path
        except Exception as e:
            print(f'Could not move from {import_path} to {dest_path} {e}')
            return None


def import_process_path(base_path, movie_path, verbose=True, dry_run=True):
    # scan imported path for nfo/xml, convert nfo to xml if needed.
    # clean unwanted files/samples
    # rename path and video file if needed
    import_name = movie_path.parts[-1]
    movie_title = None
    movie_imdb_id = None
    jsondata = None
    if verbose:
        print(f'import_process_path: {base_path} {movie_path}')
    xml = get_xml(movie_path)
    if xml is None:
        # if no xml found, check for nfo files and process....
        xml = nfo_process_path(movie_path)
        # xml = get_xml(movie_path)
        # get_nfo(movie_path)
    if xml is not None:
        # movie_title = get_xml_movie_title(xml)
        movie_imdb_id = get_xml_imdb_id(xml)
        if movie_imdb_id is not None:
            # print(f'import_process_path: scraping tmdb for {movie_imdb_id}')
            movie_scraper = TmdbScraper()
            movie_scraper.fetch_id(movie_imdb_id)
            movie_year = ' (' + str(
                datetime.datetime.strptime(movie_scraper.movie_data['release_date'], '%Y-%m-%d').year) + ')'
            movie_title = sanatized_string(movie_scraper.movie_data['title'] + movie_year)
            # tree_element = element('movie', movie_scraper.movie_data)
            # tree_root = et.ElementTree(element=tree_element)
            # tree = minidom.Document()
            dataelement = element('movie', movie_scraper.movie_data)
            dd_element = minidom.parseString(et.tostring(dataelement))
            # ddd = minidom.parseString(dd_element)
            pretty_data = dd_element.toprettyxml(indent=' ', encoding='utf-8')
            # jsondata = json.loads(dd_element)
            xml_filename = Path.joinpath(movie_path, movie_title + '.xml')
            if xml_filename.exists():
                target_xml = str(xml_filename) + '.' + str(randint(100, 999)) + '.olddata'
                xml_filename.rename(target_xml)
            with open(str(xml_filename), mode='wb') as f:
                f.write(pretty_data)

            # tree_root.write(xml_filename)
            # print(tree_element)
    if movie_title is None:
        # movie_title not found or no xml/nfo, use the original folder name instead
        movie_title = import_name
    if str(movie_path) != str(import_name):
        target_name = Path.joinpath(base_path, movie_title)
        print(f'import_process_path: rename {movie_path} to {target_name}')
        movie_path.rename(target_name)
    # return jsondata


def import_process_files(base_path, imported_movie_path, verbose=True, dry_run=True):
    # clean unwanted files/samples
    # rename video file if needed
    # if verbose:
    #    print(f'import_process_path: {base_path} {imported_movie_path}')
    xml = get_xml(imported_movie_path)
    movie_title = get_xml_movie_title(xml)
    if movie_title is not None:
        # todo check and do stuff
        # print(f'import_process_files: title: {movie_title} in path: {imported_movie_path}')
        vidfile = Path(get_video_filelist(imported_movie_path).parts[-1])
        _vidfile = Path(get_video_filelist(imported_movie_path))
        vid_ext = vidfile.suffix
        if movie_title + vid_ext != str(vidfile):
            target = Path.joinpath(imported_movie_path, Path(movie_title + vid_ext))
            try:
                _vidfile.rename(target)
                # print(f'import_process_path: renamed {str(_vidfile)} to {str(target)}')
            except Exception as e:
                print(f'import_process_files: rename error {e}')

        # v.suffix
    # else:
    #    print(f'import_process_files: error in get movie_title path: {imported_movie_path}')


if __name__ == '__main__':
    pass

# d:/movies/A Clockwork Orange (1971)/
