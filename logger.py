from datetime import datetime
import logging

class logger():
    def __init__(self, logdir = "./logs", nameprefix="", debug = False):
        super().__init__()
        self.logdir = logdir
        if(debug):level = logging.DEBUG
        else:level = logging.INFO

        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        rootLogger = logging.getLogger()

        fileHandler = logging.FileHandler("{0}/{1}_{2}.log".format(self.logdir, datetime.now().strftime('%Y%m%d_%H%M%S'), nameprefix))
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)

        rootLogger.setLevel(logging.DEBUG)
        consoleHandler.setLevel(level)

        logging.debug("CREATE LOG FILE " + str(fileHandler.baseFilename))
