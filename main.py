# moviething
"""
rename files to match movie title
check subtitles, dl missing
gather information about video codec / quality
delete samples files and other extra files
extract movie info from nfo/xml files
scrape missing info from imdb/other sources
in case of multiple nfo/xml merge into one
 """
import argparse
import configparser

from queue import Queue
# from .moviething.modules.classes import MainThread, Monitor  # , MovieClass
from classes import MainThread, Monitor
from pathlib import Path


# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput

# def check_main_thread(thread):
#    return thread.isAlive()


def check_threads(threads):
    return True in [t.isAlive() for t in threads]


def stop_all_threads(threads):
    for t in threads:
        t.kill = True
        t.join()


# def stop_main(thread):
#    thread.kill = True
#    thread.join()
#    exit(0)


def main_program():
    args = get_args()
    # verbose = args.verbose
    # dry_run = args.dryrun
    threads = list()
    monitor_q = Queue()
    main_thread = MainThread('MainThread', monitor_q, base_path=Path(base_path), verbose=args.verbose,
                             dry_run=args.dryrun)
    threads.append(main_thread)
    monitor_thread = Monitor('Monitor', monitor_q, monitor_path=Path(monitor_path), base_path=Path(base_path),
                             verbose=args.verbose, dry_run=args.dryrun)
    threads.append(monitor_thread)
    for t in threads:
        t.setDaemon = False
        t.start()
    #    main_thread.setDaemon = False
    #    main_thread.start()
    #    monitor_thread.setDaemon = False
    #    monitor_thread.start()
    while check_threads(threads):
        try:
            cmd = input('>')
            if cmd[:1] == 'i':
                main_thread.get_status()
            if cmd[:4] == 'quit' or cmd[:1] == 'q':
                stop_all_threads(threads)
            if cmd[:4] == 'dump':
                main_thread.dump_folders()
            if cmd[:6] == 'movies':
                main_thread.dump_movies()
            if cmd[:2] == 'uf':
                main_thread.update_folders()
            if cmd[:6] == 'update':
                main_thread.update()
            if cmd[:6] == 'import':
                main_thread.import_from_path(Path(cmd[7:]))
            if cmd[:7] == 'setbase':
                main_thread.set_base_path(cmd[8:])
            if cmd[:4] == 'list':
                main_thread.dump_movie_list()
            if cmd[:6] == 'scrape':
                main_thread.scrape(cmd[7:16])
        except KeyboardInterrupt:
            stop_all_threads(threads)
        except Exception as e:
            print(f'Exception in main_program {e}')


def get_args():
    parser = argparse.ArgumentParser(description="moviething")
    parser.add_argument("--dryrun", action="store_true",
                        help="Dry run - no changes to filesystem")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output")

    return parser.parse_args()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    base_path = config['moviethingsettings']['path']
    monitor_path = config['moviethingsettings']['monitor_path']
    themoviedbapikey = config['moviethingsettings']['themoviedbapikey']
    main_program()
