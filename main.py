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
import numpy as np
import os
import signal

# {'latitude': 24.3414826, 'longitude': 120.6253246, 'elevation': 72.024, 'time': datetime.datetime(2020, 3, 19, 17, 7, 27), 'speed': 7.411}

def signal_handler(sig, frame):
    logging.info(str(os.getpid() + " terminate..."))
    sys.exit(0)

def main(file):
    #designer for fps=60 and goPro7 mp4 Video
    signal.signal(signal.SIGINT, signal_handler)
    logging.info("{0} System Start at {1}".format(str(os.getpid()), datetime.now().strftime('%Y%m%d_%H%M%S')))
    imgs = mp.Manager().Queue()
    detector_ready = mp.Manager().Value('i', False)
    dn_width = mp.Manager().Value('i', 416)
    dn_height = mp.Manager().Value('i', 416)
    mpdarknet = mp.Process(target=detector, args=(imgs, detector_ready, dn_width, dn_height,))
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
        while(imgs.qsize() > 1000):
            logging.warning("Pause for waiting detector processing 60s")
            time.sleep(60)
        if(count % 10 == 0):logging.info("{0} imgs in the Queue".format(str(imgs.qsize())))
        count = count + 1
        logging.info("Start to processing point " + str(count))
        cur_point = SimpleNamespace(lat= p.latitude, lon=p.longitude, time=p.time)
        logging.debug(cur_point.__dict__)

        for frame_in_second in range(15):
            if(count == 1 and frame_in_second == 8):
                break
            logging.debug("processing frame " + str(cur_frame))
            cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)
            success, frame = cap.read()
            if(not success):
                logging.warning("frame {0} read fail skip.....".format(str(cur_frame)))
            else:
                job = cur_point
                job.frame = cv2.cvtColor(np.float32(cv2.resize(frame, (dn_width.value,dn_height.value), 
                                        interpolation=cv2.INTER_AREA)), cv2.COLOR_BGR2RGB)
                job.frame_count = cur_frame
                imgs.put(job)
            cur_frame = cur_frame + 4
        
        if(cur_frame >= total_frames or count == len(points)):
            logging.info("Process done")
            break
    
def detector(jobs, flag, dn_width, dn_height):
    signal.signal(signal.SIGINT, signal_handler)
    logger(nameprefix="darknet")
    logging.info(str(os.getpid()) + " detector start")
    thresh = 0.5
    cfgpath = ".\\darknet_data\\yolov4-tra_416.cfg"
    weipath = ".\\darknet_data\\yolov4-tra_320_best.weights"
    metpath = ".\\darknet_data\\obj.data"
    darknet.performDetect(thresh=thresh, configPath=cfgpath, 
                        weightPath=weipath, metaPath=metpath, initOnly=True)
    darknet_image = darknet.make_image(darknet.network_width(darknet.netMain),
                                    darknet.network_height(darknet.netMain),3)
    dn_width.value = darknet.network_width(darknet.netMain)
    dn_height.value = darknet.network_height(darknet.netMain)
    flag.value = True
    while True:
        if(jobs.qsize() == 0):
            time.sleep(1)
            logging.debug("jobs = {0} sleep(1)".format(str(jobs.qsize())))
        else:
            #job.lat, job.lon, job.time, job.frame, job.frame_count
            job = jobs.get()
            logging.debug("job.lat = {0} job.lon = {1} job.time = {2} job.frame.type = {3} job.frame_count = {4}"
                        .format(job.lat, job.lon, job.time, type(job.frame), job.frame_count))
            darknet.copy_image_from_bytes(darknet_image, job.frame.tobytes())
            detections = darknet.detect_image(darknet.netMain, darknet.metaMain, darknet_image, thresh=thresh)
            job.detections = detections
            mp.Process(target=savedata, args=(job,)).start()

def savedata(job, debug = True):
    logger(nameprefix="savedata")
    savesdir = os.path.join(os.path.dirname(__file__), "saves")
    if(job.detections != []):
        logging.info("on frame {0} detected object".format(str(job.frame_count)))
        filename = os.path.join(os.path.dirname(__file__), "saves", str(job.frame_count) + ".jpg")
    elif(debug and job.detections == []):
        filename = os.path.join(os.path.dirname(__file__), "saves", "debug", str(job.frame_count) + ".jpg")
    logging.debug("frame_count {0}.detections = {1}".format(str(job.frame_count), str(job.detections)))
    cv2.imwrite(filename, cv2.cvtColor(job.frame, cv2.COLOR_RGB2BGR))
    pass

if __name__ == "__main__":
    logger(nameprefix="Main")
    file = '.\\gopro2gpx\\gopro7.MP4'
    main(file=file)