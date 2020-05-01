# misc functions
import os
import re
from pathlib import Path, PurePath
import inspect
import psutil
import sys

from defs import vid_extensions, min_filesize
from stringutils import sanatized_string


# noinspection PyUnusedFunction
def who_called_func():
    return inspect.stack()[2][3]


def can_open_file(file):
    try:
        dest = Path(str(file) + '.tmp')
        Path.rename(file, dest)
        Path.rename(dest, file)
        return True
    except Exception as e:
        print(f'file in use {e}')
        return False


def xcan_open_file(file):
    # check if we can get handle
    print(f'can_open_file: {file}')
    try:
        file_object = open(file, 'a', 8)
        if file_object:
            return True
        else:
            return False
    except IOError as e:
        print(f'scan_path: IOERROR {e} on {file}')
        return False
    except Exception as e:
        print(f'scan_path: EXCEPTION {e} on {file}')
        return False


def scan_path(path, extensions, min_size=0):
    # scan given path for movies with valid extensions and larger than min_size
    for entry in path.glob('*'):
        if entry.is_dir():
            yield from scan_path(entry, extensions, min_size)
        else:
            if entry.suffix in extensions and entry.stat().st_size > min_size:
                yield entry


def scan_path_open(path, extensions, min_size=0):
    # scan given path for movies with valid extensions and larger than min_size
    # checks if file is open
    # print(f'scanpathopen....')
    for entry in path.glob('*'):
        if entry.is_dir():
            yield from scan_path_open(entry, extensions, min_size)
        else:
            if entry.suffix in extensions and entry.stat().st_size > min_size and can_open_file(entry):
                yield entry


def get_folders(base_path):
    # returns a list of folders in base_path
    # folders = []
    try:
        return [d for d in base_path.glob('*') if d.is_dir()]
    except Exception as e:
        print(f'get_folders: {e}')
        # exit(-1)
        return None


def get_folders_non_empty(base_path):
    try:
        folders = [d for d in base_path.glob('*') if d.is_dir()]
        result = []
        for path in folders:
            if len([file for file in scan_path_open(path, vid_extensions, min_size=min_filesize)]) >= 1:
                result.append(path)
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
