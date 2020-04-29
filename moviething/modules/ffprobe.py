# grab technical details from vidfiles with ffprobe
import subprocess
import re
import sys
import os
import platform
from lxml import etree as et
from pathlib import Path
from etree import etree_to_dict

class FFProbe():
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        if str(platform.system() == 'Windows'):
            cmd=["ffprobe", "-show_streams",'-print_format', 'xml','-show_format','-pretty','-v', 'quiet', self.filename]
        else:
            cmd=["ffprobe -show_streams,-print_format, xml,-show_format,-pretty,-v, quiet", self.filename]
        out, err =  subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        # print(f'o {len(out)}')
        # print(f'e {len(err)}')
        root = et.ElementTree(et.fromstring(out)).getroot()
        # root = tree.getroot()

def get_ffprobe(filename):
        if str(platform.system() == 'Windows'):
            cmd=["ffprobe", "-show_streams",'-print_format', 'xml','-show_format','-pretty','-v', 'quiet', str(filename)]
        else:
            cmd=["ffprobe -show_streams,-print_format, xml,-show_format,-pretty,-v, quiet", str(filename)]
        out, err =  subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        return etree_to_dict(et.ElementTree(et.fromstring(out)).getroot())

if __name__ == '__main__':
    pass
    # d = Path('/mnt/d/movies')
    # testlist = [k for k in list(d.glob('**/*.mkv'))]
    # print(testlist[1])
    # print(get_ffprobe(testlist[1]))
#    m = FFProbe(
#        "d:/movies/Whiskey Tango Foxtrot (2016)/Whiskey Tango Foxtrot (2016).mkv")
#    m.parse()
