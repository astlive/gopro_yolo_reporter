from datetime import datetime
from logger import logger
from kmlhandler import getkmpoints, kmplush
from gopro7gpshandler import getpoints, gettimediff
from types import SimpleNamespace
import multiprocessing as mp
import time
import darknet
import logging
import sys
import cv2
import os

# {'latitude': 24.3414826, 'longitude': 120.6253246, 'elevation': 72.024, 'time': datetime.datetime(2020, 3, 19, 17, 7, 27), 'speed': 7.411}

def main(file):
    #designer for fps=60 and goPro7 mp4 Video
    imgs = mp.Manager().Queue()
    detector_ready = mp.Manager().Value('i', False)
    mpdarknet = mp.Process(target=detector, args=(imgs, detector_ready,))
    mpdarknet.start()
    while detector_ready.value == False:
        logging.info("Waiting for detector ready...re-check in 10s")
        time.sleep(10)
    logging.debug("now checking the module")
    kmpoints = getkmpoints()
    logging.info("loaded " + str(len(kmpoints)) + " of HMP(百公尺樁)")
    if(len(kmpoints) < 2):
        logging.warning("not enough HMP for count\r\nExit.....")
        sys.exit(1)
    points = getpoints(file, skip=False)
    logging.info("find " + str(len(points)) + " GPS points in file")
    logging.info("Record time taken " + str(gettimediff(points)))
    if(len(points) < 2):
        logging.warning("not enout GPS point\r\nExit.....")
        sys.exit(1)

    cap = cv2.VideoCapture(file)
    if(not cap.isOpened()):
        logging.warning("could not open :", file)
        sys.exit(1)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logging.info(str(total_frames) + " frames in file")

    count = 0
    cur_frame = 0

    for p in points :
        count = count + 1
        logging.info("Start to processing point " + str(count))
        cur_point = SimpleNamespace(lat= p.latitude, lon=p.longitude, time=p.time)
        logging.debug(cur_point.__dict__)

        for frame_in_second in range(15):
            if(count == 1 and frame_in_second == 8):
                break
            logging.debug("processing frame " + str(cur_frame))
            cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)
            job = cur_point
            job.frame = cap.read()
            cur_frame = cur_frame + 4
        
        if(cur_frame >= total_frames or count == len(points)):
            logging.info("Process done")
            break
    
def detector(jobs, flag):
    logger(nameprefix="darknet")
    logging.info("detector start")
    thresh = 0.5
    cfgpath = ".\\darknet_data\\yolov4-tra_320.cfg"
    weipath = ".\\darknet_data\\yolov4-tra_320_best.weights"
    metpath = ".\\darknet_data\\obj.data"
    darknet.performDetect(thresh=thresh, configPath=cfgpath, 
                        weightPath=weipath, metaPath=metpath, initOnly=True)
    flag.value = True
    while True:
        time.sleep(1)
        logging.debug("detector wait jobs")
        


if __name__ == "__main__":
    logger(nameprefix="Main")
    file = '.\\gopro2gpx\\gopro7.MP4'
    main(file=file)