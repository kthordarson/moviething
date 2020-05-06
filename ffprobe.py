# grab technical details from vidfiles with ffprobe
import platform
import subprocess
from xml.dom import minidom

# from lxml import etree as et

def get_ffprobe(filename):
    if str(platform.system() == 'Windows'):
        cmd = ["ffprobe", "-show_streams", '-print_format', 'xml', '-pretty', '-v', 'quiet', str(filename)]
    else:
        cmd = ["ffprobe -show_streams -print_format xml -pretty -v quiet", filename]
    out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).communicate()
    # out = out.decode('utf-8')
    out = str(out).replace('\n', '')
    res = minidom.parseString(out)
    return res  # et.ElementTree(et.fromstring(out)).getroot()


if __name__ == '__main__':
    print(get_ffprobe("d:/movies/Whiskey Tango Foxtrot (2016)/Whiskey Tango Foxtrot (2016).mkv"))
    # testfile = 'd:/movies_incoming/Alien (1979)/Alien.1979.Directors.Cut.1080p.BluRay.H264.AAC-RARBG.mp4'
    # ff = get_ffprobe(testfile)
    # print(type)
    # pass
    # d = Path('/mnt/d/movies')
    # testlist = [k for k in list(d.glob('**/*.mkv'))]
    # print(testlist[1])
    # print(get_ffprobe(testlist[1]))
#    m = FFProbe(
#        "d:/movies/Whiskey Tango Foxtrot (2016)/Whiskey Tango Foxtrot (2016).mkv")
#    m.parse()
