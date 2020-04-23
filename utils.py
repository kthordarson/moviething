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

def sanatize_foldernames(movie_folder, verbose, dry_run):
    # remove [] from folder names
    folder_base = os.path.basename(movie_folder)
    
    bracket_regex = re.compile(r'/[(.*?)/]')
    clean_name = sanatized_string(re.sub(bracket_regex, '', folder_base).strip())
    if folder_base != clean_name:
        # print(f'sanatize_foldernames:{folder_base}')
        # print(f'Clean name        :{clean_name}')
        new_name = os.path.dirname(movie_folder.path) + '/' + clean_name
        print(f'Renaming {movie_folder.path} to {new_name}')
        if not dry_run:
            os.rename(src=movie_folder.path, dst=new_name)

def sanatize_filenames(filename, verbose=True, dry_run=True):
    # remove [] from filenames within each movie folder
    base_filename = os.path.basename(os.path.dirname(filename.path))
    bracket_regex = re.compile(r'/[(.*?)/]')
    clean_name = sanatized_string(re.sub(bracket_regex, '', base_filename).strip())
    if base_filename != clean_name:
        print(f'old filename      :{base_filename}')
        print(f'Clean name        :{clean_name}')

def get_folders(base_path):
    folders = []
    try:
        for d in os.scandir(base_path):
            if os.path.isdir(d):
                folders.append(d)
                # print(f'{d} is folder')
    except Exception as e:
        print(f'get_folders: {e}')
        exit(-1)
    return folders

def get_video_filelist_old(movie_path):
    # scan given move_path for valid video files, return first found
    # todo handle multiple valid video files in movie_path
    filelist = []
    for root,dirs,files in os.walk(movie_path):
        for file in files:
            if file.endswith(vid_extensions)  and os.path.getsize(os.path.join(root,file)) > min_filesize:
                filelist.append(os.path.join(root,file))
    if len(filelist) > 1:
        print(f'Mutiple vid files in {movie_path.path} skipping')
        return None
    if len(filelist) == 1:
        return filelist[0]
    else:
        print(f'No videos in {movie_path.path}')
        return None

def get_video_filelist(movie_path):
    # scan given move_path for valid video files, return first found
    # todo handle multiple valid video files in movie_path
    filelist = []
    for file in scan_path(movie_path, vid_extensions, min_size=min_filesize):
        filelist.append(file)
    if len(filelist) > 1:
        print(f'Mutiple vid files in {movie_path.path} skipping')
        return None
    if len(filelist) == 1:
        return filelist[0]
    else:
        print(f'No videos in {movie_path.path}')
        return None

# def get_video_filelist(movie_path):
#     file_list = []
#     for entry in scan_path(movie_path, vid_extensions, min_size=min_filesize):
#         file_list.append(entry)
#     return file_list

def sanatized_string(input_string, whitelist=valid_input_string_chars, replace=''):
    # replace spaces
    for r in replace:
        input_string = input_string.replace(r, '_')

    # keep only valid ascii chars
    cleaned_input_string = unicodedata.normalize(
        'NFKD', input_string).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_input_string = ''.join(
        c for c in cleaned_input_string if c in whitelist)
    # if len(cleaned_input_string) > char_limit:
    #    print("Warning, input_string truncated because it was over {}. input_strings may no longer be unique".format(char_limit))
    return cleaned_input_string[:char_limit]

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
                print(f'Movie folder name is correct {os.path.dirname(xml)}')
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
                vidname, ext = os.path.splitext(video_file)
                correct_filename = movie_title + ext
                org_name = os.path.basename(video_file)
                if org_name == correct_filename and verbose:
                    print(f'Video filename correct: org={org_name} cor={correct_filename}')
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

if __name__ == '__main__':
    test_fix_filenames()