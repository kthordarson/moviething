# misc functions
import os
import re
from pathlib import Path, PurePath
import inspect
import psutil

from moviething.modules.defs import vid_extensions, min_filesize
# from moviething.modules.nfoparser import get_xml_movie_title, get_xml
from moviething.modules.stringutils import sanatized_string

# noinspection PyUnusedFunction
def who_called_func():
    return inspect.stack()[2][3]


def can_open_file(file):
    # check if we can get handle
    print(f'can_open_file: {file.path}')
    try:
        file_object = open(file.path, 'a', 8)
        if file_object:
            return True
        else:
            return False
    except IOError as e:
        print(f'scan_path: IOERROR {e} on {file.path}')
        return False
    except Exception as e:
        print(f'scan_path: EXCEPTION {e} on {file.path}')
        return False
    
def scan_path(path, extensions, min_size=0):
    # scan given path for movies with valid extensions and larger than min_size
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_path(entry.path, extensions, min_size)
        else:
            if entry.name.endswith(extensions) and entry.stat().st_size > min_size:
                yield entry

def scan_path_open(path, extensions, min_size=0):
    # scan given path for movies with valid extensions and larger than min_size
    # checks if file is open
    # print(f'scanpathopen....')
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_path_open(entry.path, extensions, min_size)
        else:
            if entry.name.endswith(extensions) and entry.stat().st_size > min_size and can_open_file(entry):
                yield entry


def get_folders(base_path):
    # returns a list of folders in base_path
    # folders = []
    try:
        return [d for d in os.scandir(base_path) if os.path.isdir(d)]
    except Exception as e:
        print(f'get_folders: {e}')
        # exit(-1)
        return None


def get_folders_non_empty(base_path):
    try:
        # sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
        folders = [d for d in os.scandir(base_path) if os.path.isdir(d)]
        result = []
        for path in folders:
            root_directory = Path(path)
            # file_object = open(f, 'a', 8)
            if len([file for file in scan_path_open(path, vid_extensions, min_size=min_filesize)]) >= 1:
                # print(f'get_folders_non_empty: {file}')
                result.append(PurePath(root_directory))
#            if sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file()) > 1:
#                result.append(PurePath(root_directory))
    except Exception as e:
        print(f'get_folders: {e}')
        return []
        # exit(-1)
    return result


def get_video_filelist(movie_path, verbose=True, dry_run=True):
    # scan given move_path for valid video files, return first found
    # todo handle multiple valid video files in movie_path
    # filelist = []
    filelist = [file for file in scan_path(movie_path, vid_extensions, min_size=min_filesize)]
    if len(filelist) > 1:
        print(f'Mutiple vid files in {movie_path} skipping')
        return None
    if len(filelist) == 1:
        return filelist[0]
    else:
        if verbose:
            print(f'No videos in {movie_path}')
        return None



if __name__ == '__main__':
    pass
    # test_fix_filenames()
