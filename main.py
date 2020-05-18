from datetime import datetime
from logger import logger
from kmlhandler import getkmpoints, kmplush
from gopro7gpshandler import getpoints
import logging
import sys

def main():
    logging.debug("now checking the module")
    kmpoints = getkmpoints()
    logging.info("loaded " + str(len(kmpoints)) + " of HMP(百公尺樁)")
    if(len(kmpoints) < 2):
        logging.warning("not enough HMP for count\r\nExit.....")
        sys.exit(1)
    points = getpoints('.\\gopro2gpx\\gopro7.MP4')
    logging.info("find " + str(len(points)) + " GPS points in file")

if __name__ == "__main__":
    logger()
    main()