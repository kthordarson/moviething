# misc functions
import inspect
import time
from pathlib import Path

from defs import MIN_FILESIZE, VID_EXTENSIONS


# noinspection PyUnusedFunction
def who_called_func():
    return inspect.stack()[2][3]


def can_open_file(file):
    try:
        # dest = Path(str(file) + '.tmp')
        # Path.rename(file, dest)
        Path.rename(file, file)
        return True
    except Exception as e:
        print(f'can_open_file: file in use {e}')
        # time.sleep(1)
        return False


def can_open_path(path):
    try:
        for file in path.glob('*'):
            if file.suffix in VID_EXTENSIONS:
                try:
                    # dest = Path(str(file) + '.tmp')
                    # Path.rename(file, dest)
                    # Path.rename(dest, file)
                    Path.rename(file, file)
                    return True
                except Exception as e:
                    # print(f'can_open_path: file in use {e}')
                    time.sleep(1)
                    return False
        return True
    except:
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
    folders = [d for d in base_path.glob('*') if d.is_dir()]
    result = [path for path in folders if can_open_path(path)]
    # result = [path for path in scan_path_open(folders, VID_EXTENSIONS, min_size=MIN_FILESIZE)]
    # for path in folders:
    #     if len([file for file in scan_path_open(path, VID_EXTENSIONS, min_size=MIN_FILESIZE)]) >= 1:
    #         result.append(path)
    return result


def get_video_filelist(movie_path, verbose=True):
    # scan given move_path for valid video files, return first found
    # todo handle multiple valid video files in movie_path
    # filelist = []
    filelist = [file for file in scan_path(movie_path, VID_EXTENSIONS, min_size=MIN_FILESIZE)]
    if len(filelist) > 1:
        print(f'Mutiple vid files in {movie_path} skipping')
        return None
    if len(filelist) == 1:
        return filelist[0]
    else:
        return None

if __name__ == '__main__':
    print('utils')
    # test_fix_filenames()
