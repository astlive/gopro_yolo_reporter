import sys
from types import SimpleNamespace
import os
import pathlib

def getpoints(filepath, skip=False):
    if(not chk()):return None
    import gpmf
    from gopro2gpx import BuildGPSPoints
    config = mkconfig(filepath)
    parser = gpmf.Parser(config)
    data = parser.readFromMP4()
    points = BuildGPSPoints(data, skip)
    return points

def mkgpspoint(latitude, longitude, time):
    pass

def fixpoints(points):
    fixed_points = []
    for i in range(len(points) - 1):
        print("checking " + str(i))
        p = points[i]
        p_n = points[i + 1]
        if((p_n.time - p.time).total_seconds() > 1):
            print(p.__dict__)
            print(p_n.__dict__)
    return fixed_points

def gettimediff(points):
    point_a = points[0]
    point_b = points[len(points) -1]
    return point_b.time - point_a.time

def mkconfig(file):
    return SimpleNamespace(ffmpeg_cmd='.\\3rdlib\\ffmpeg\\bin\\ffmpeg.exe', ffprobe_cmd='.\\3rdlib\\ffmpeg\\bin\\ffprobe.exe', verbose=0, file=file, outputfile=file)

def test(config):
    import gpmf
    from gopro2gpx import BuildGPSPoints
    parser = gpmf.Parser(config)
    data = parser.readFromMP4()
    points = BuildGPSPoints(data)
    if(len(points) == 0):
        print("Errrr not a gopro7 file or GPS data missing\r\n Exit......")
        sys.exit(0)
    for point in points:
        print(point.__dict__)
    print(gettimediff(points))
    print("find " + str(len(points)) + " GPS points in file")
    fixpoints(points)
    
def chk():
    curdir = pathlib.Path(__file__).parent.absolute()
    # print(curdir)
    gpxdir = os.path.join(curdir, "gopro2gpx")
    # print(gpxdir)
    if curdir not in sys.path:
        sys.path.append(curdir)
    if gpxdir not in sys.path:
        sys.path.append(gpxdir)
    from gopro2gpx import BuildGPSPoints
    return True

if __name__ == "__main__":
    config = mkconfig('.\\gopro2gpx\\gopro7.MP4')
    print(config.__dict__)
    if(chk()):
        print("start test")
        test(config)
    else:
        print("Errrr")
    