import os
import shutil
from pathlib import Path
from moviething.modules.nfoparser import get_xml, get_xml_movie_title
from moviething.modules.utils import get_video_filelist


def import_check_path(import_path, verbose=True, dry_run=True):
    if verbose:
        print(f'Checking path {import_path} {dry_run}')
    if not import_path.exists():
        if verbose:
            print(f'Import path: {import_path} not found')
        return False
    else:
        # scan all files in import_path
        # - check for videos, nfo/xml, unwanted files, subtitles, etc
        # - check if movie already exists in base_movies
        if get_video_filelist(import_path) is None:
            return False
        else:
            return True

def import_movie(base_path, import_path, import_name, verbose=True, dry_run=True):
    # import_path must only contain one movie
    # example: c:\incoming\new_movie_name\
    if verbose:
        print(f'Starting import process: from {import_path} to {base_path}')
    # make destination path
    dest_path = Path.joinpath(base_path, import_name)
#    try:
#        os.makedirs(dest_path)
#    except Exception as e:
#        print(f'Could not create {dest_path} {e}')
    # if dry, only copy from import
    if dry_run:
        try:
            shutil.copytree(src=import_path, dst=dest_path)
            # source_files = os.listdir(import_path)
            # for source_file in source_files:
            #    shutil.copyfile(src=source_file, dst=dest_path)
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
    if verbose:
        print(f'import_process_path: {base_path} {movie_path} {verbose} {dry_run}')
    xml = get_xml(movie_path)
    movie_title = get_xml_movie_title(xml)
    import_name = movie_path.parts[-1]
    if movie_title == None:
        movie_title = import_name
    if str(movie_path) != str(import_name):
        os.rename(src=movie_path, dst=Path.joinpath(base_path, movie_title))


if __name__ == '__main__':
    pass
