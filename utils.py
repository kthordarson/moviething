# misc functions
from nfoparser import get_xml_movie_title, get_xml
from defs import vid_extensions, min_filesize
from stringutils import sanatized_string
import os
import re
import shutil
from pathlib import Path, PurePosixPath, PurePath, PureWindowsPath

import psutil

def has_handle(fpath):
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if fpath == item.path:
                    return True
        except Exception:
            pass
    return False

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
    # print(f'scanpathopen....')
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_path_open(entry.path, extensions, min_size)
        else:
            if entry.name.endswith(extensions) and entry.stat().st_size > min_size and can_open_file(entry):
                yield entry

def sanatize_foldernames(movie_folder, verbose, dry_run):
    # remove [] from folder names
    folder_base = os.path.basename(movie_folder)
    bracket_regex = re.compile(r'/[(.*?)/]')
    clean_name = sanatized_string(re.sub(bracket_regex, '', folder_base).strip())
    if folder_base != clean_name:
        # print(f'sanatize_foldernames:{folder_base}')
        # print(f'Clean name        :{clean_name}')
        new_name = os.path.dirname(movie_folder.path) + '/' + clean_name
        if verbose:
            print(f'sanatize_foldernames: {movie_folder} {folder_base} {clean_name} {verbose} {dry_run}')
            print(f'Renaming {movie_folder.path} to {new_name}')
        if not dry_run:
            try:
                os.rename(src=movie_folder.path, dst=new_name)
            except Exception as e:
                print(f'sanatize_foldername ERROR {movie_folder.path} to {new_name} {e}')


def sanatize_filenames(filename, verbose=True, dry_run=True):
    # remove [] from filenames within each movie folder
    base_filename = os.path.basename(os.path.dirname(filename.path))
    bracket_regex = re.compile(r'/[(.*?)/]')
    clean_name = sanatized_string(re.sub(bracket_regex, '', base_filename).strip())
    if base_filename != clean_name:
        print(f'old filename      :{base_filename}')
        print(f'Clean name        :{clean_name}')
    if verbose:
        print(f'sanatize_filenames: {filename} {base_filename} {clean_name} {verbose} {dry_run}')


def get_folders(base_path):
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
    filelist = []
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


def fix_filenames_path(movie_path, base_path, verbose, dry_run):
    # scan movie_path for valid xml, extract title and year, compare folder and filename, rename if needed
    # first iteration check and correct movie folder name
    # xml_list = []
    xml = get_xml(movie_path)
    if xml is None:
        print(f'No xml found in {movie_path} nothing we can do here....')
    else:
        movie_title = get_xml_movie_title(xml)
        # xml_list.append(xml)
        if movie_title is not None:
            if os.path.basename(os.path.dirname(xml)) == movie_title:
                # pass
                # print(f'Movie folder name is correct {os.path.dirname(xml)}')
                return movie_path
            else:
                dest = base_path + '/' + movie_title
                if verbose:
                    print(f'Movie folder name is incorrect {os.path.dirname(xml)}')
                    print(f'Renaming from: {os.path.dirname(xml)}')
                    print(f'Renaming to  : {dest}')
                if not dry_run:
                    try:
                        os.rename(src=os.path.dirname(xml), dst=dest)
                    except Exception as e:
                        print(f'fix_names rename failed {e}')
                # return renamed folder name
                return dest


def fix_filenames_files(movie_path, base_path, verbose, dry_run):
    # second iteration check and rename movie filenames in movie_path / dest
    # populate list of video files in each movie folder, files with valid video extension only from each subfolder
    xml = get_xml(movie_path)
    if xml is None:
        print(f'No xml found in {movie_path} nothing we can do here....')
    else:
        movie_title = get_xml_movie_title(xml)
        # xml_list.append(xml)
        if movie_title is not None:
            video_file = get_video_filelist(movie_path)
            if video_file is not None:
                ext = os.path.splitext(video_file)[1]
                correct_filename = movie_title + ext
                org_name = os.path.basename(video_file)
                if org_name == correct_filename and verbose:
                    pass
                    # print(f'Video filename correct: org={org_name} cor={correct_filename}')
                else:
                    dest = os.path.dirname(video_file) + '/' + correct_filename
                    if verbose:
                        print(f'Movie filename name is incorrect old: {org_name} correct: {correct_filename}')
                        print(f'Renamed {video_file.path} to {dest}')
                    if not dry_run:
                        try:
                            os.rename(src=video_file, dst=dest)
                        except Exception as e:
                            print(f'fix_names rename failed {e}')


def test_sanatize_filenames():
    folders = get_folders('d:/movies')
    for f in folders:
        vidfile = get_video_filelist(f)
        if vidfile:
            # print(type(vidfile))
            sanatize_filenames(vidfile, verbose=True, dry_run=True)


def test_fix_filenames():
    # xml1 = 'd:/movies/Reservoir Dogs (1992)/Reservoir Dogs (1992).xml'
    # movie_path = 'o:/Movies/import/Event Horizon.1997.1080p.BluRay.H264.AAC-RARBG/'
    movie_path = 'o:/Movies/import/Pirates Of The Caribbean 2 - Dead Mans Chest/'
    # movie_path = 'd:/movies/Reservoir Dogs (1992)/'
    base_path = 'd:/movies'
    verbose = True
    dry_run = True
    # input_folder = xml1
    fix_filenames_path(movie_path, base_path, verbose, dry_run)
    fix_filenames_files(movie_path, base_path, verbose, dry_run)


def sanatize_filenames_MainThread(input_folder=None, folder_list=None, verbose=True, dry_run=True):
    # remove [xxx] from all filenames
    # refresh movie_folder
    # update_folders()
    if input_folder is None:
        for movie_folder in folder_list:
            sanatize_filenames(movie_folder, verbose=verbose, dry_run=dry_run)
    else:
        sanatize_filenames(input_folder, verbose=verbose, dry_run=dry_run)
    # refresh again incase of renames...
    # update_folders()

def sanatize_foldernames_MainThread(input_folder=None, folder_list=None, verbose=True, dry_run=True):
    # remove [xxx] from all foldernames
    # refresh movie_folder
    # update_folders()
    if input_folder is None:
        for movie_folder in folder_list:
            sanatize_foldernames(movie_folder, verbose=verbose, dry_run=verbose)
    else:
        sanatize_foldernames(input_folder, verbose=verbose, dry_run=verbose)
    # refresh again incase of renames...
    # update_folders()


if __name__ == '__main__':
    pass
    # test_fix_filenames()
