# misc functions
import os
import shutil
import glob
from nfoparser import *
from scrapers import imdb_scrape
from defs import *


def scan_path(path, extensions, min_size=0):
    # scan given path for movies with valid extensions and larger than min_size
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_path(entry.path, extensions, min_size)
        else:
            if entry.name.endswith(extensions) and entry.stat().st_size > min_size:
                yield entry

def fix_base_folder(start_dir, file_list, verbose, dry_run, vid_extensions, min_filesize):
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
        for entry in scan_path(start_dir, vid_extensions, min_size=min_filesize):
            file_list.append(entry)
    return file_list



def get_folders(base_path):
    folders = []
    for d in os.scandir(base_path):
        if os.path.isdir(d):
            folders.append(d)
            # print(f'{d} is folder')
    return folders

def get_video_filelist(movie_path):
    # scan given move_path for valid video files, return first found
    # todo handle multiple valid video files in movie_path
    filelist = []
    for root,dirs,files in os.walk(movie_path):
        for file in files:
            if file.endswith(vid_extensions)  and os.path.getsize(os.path.join(root,file)) > min_filesize:
                filelist.append(os.path.join(root,file))
    if len(filelist) > 0:
        return filelist[0]
    else:
        return None

# def get_video_filelist(movie_path):
#     file_list = []
#     for entry in scan_path(movie_path, vid_extensions, min_size=min_filesize):
#         file_list.append(entry)
#     return file_list

def fix_names(folder, verbose, dry_run):
    # check if folder and files are named correctly, rename with info from xml
    found_xml = False
    # xml_files = []
    xml_files = glob.glob(folder.path + '/*.xml')
    if len(xml_files) == 0:
        print(f'No xml/nfo in {folder}')
        return
    if len(xml_files) > 1:
        print(f'found more than 1 xml {folder.path} - Calling xml combiner...')
        xml_files = merge_xml_files(xml_files, dry_run)
        # exit(-1)
    if len(xml_files) == 1:
        if verbose:
            pass
            # print(f'Found xml {len(xml_files)}, reading {xml_files[0].path}')
        data = get_xml_data(xml_files[0])
        # todo move this stuff to get_xml_data....
        xmldata = data.get('movie', None)
        xmldata2 = data.get('Title', None)
        if xmldata is not None:
            if verbose:
                pass
                # print(f'xml type 1')
            title = xmldata.get('title')
            year = xmldata.get('year')
            imdb_id = xmldata.get('id', None)
            if title is None and year is None and imdb_id is not None:
                if verbose:
                    print(f'Need to scrape for imdb id: {imdb_id} {xml_files[0]}')
                imdb_data = imdb_scrape(imdb_id)
                return False
            elif title is None and year is None and imdb_id is None:
                if verbose:
                    print(f'No data found {xml_files[0]}')
                return False
        elif xmldata2 is not None:
            if verbose:
                pass
                # print('xml type 2')
            title = xmldata2.get('OriginalTitle')
            year = xmldata2.get('ProductionYear')
            imdb_id = xmldata2.get('IMDbId', None)
            if title is None and year is None and imdb_id is not None:
                if verbose:
                    print(f'Need to scrape for imdb id: {imdb_id} {xml_files[0]}')
                imdb_data = imdb_scrape(imdb_id)
                return False
            elif title is None and year is None and imdb_id is None:
                if verbose:
                    print(f'No data found {xml_files[0]}')
                return False
        if verbose:
            print(f't:{title} y: {year} id:{imdb_id} {xml_files[0]}')

def clean_subfolder(movie_folder, verbose, dry_run):
    # remove unwanted, samples and extra files from movie_folder
    if verbose:
        pass
        # print(f'clean_subfolder start: {movie_folder}')
    for d in os.scandir(movie_folder):
        if os.path.isdir(d):
            if verbose:
                pass
                # print(f'Checking folder: {d.name}')
            if d.name.lower() in unwanted_files['subdirs']:
                print(f'{d.path} is unwanted, delete!')
                if not dry_run:
                    try:
                        os.makedirs(d.path+'/'+junkpathname, exist_ok=True)
                        shutil.move(src=d.path, dst=d.path + '/' + junkpathname)
                        # shutil.rmtree(d.path, ignore_errors=True)
                        # os.removedirs(d.path)
                        # os.rename(src=d.path, dst=d.path+'.deleted')
                    except Exception as e:
                        print(f'Delete subfolder {d.path} failed {e}')
                        # exit(-1)
        else:
            if d.name.lower() in unwanted_files['txtfiles'] or d.name.lower() in unwanted_files['videos'] or d.name.lower() in unwanted_files['images']:
                if verbose:
                    print(f'Unwanted file: {d.path}')
                if not dry_run:
                    try:
                        os.makedirs(d.path+'/'+junkpathname, exist_ok=True)
                        shutil.move(src=d.path, dst=d.path + '/' + junkpathname)
                        # os.remove(d.path)
                    except Exception as e:
                        print(f'Could not delete {d.path} {e}')

# def populate_movielist(file_list):
#     print('populate_movielist')
#     movie_list = []
#     for file in file_list:
#         movie = MovieClass(filename=file)
#         movie.scan_nfo(movie.path)
#         movie.populate_info()
#         movie_list.append(movie)
#     return movie_list


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
