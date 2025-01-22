import logging
import time


class AppLogger:
    def __init__(self, moduleName, logfile):
        self._logger = logging.getLogger(moduleName)
        self._logger.handlers.clear()
        handler = logging.FileHandler(logfile, encoding='utf-8')
        fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(message)s"
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        self._logger.addHandler(console)
        self._logger.setLevel(logging.INFO)
        self.warnning = self._logger.warning
        self.error = self._logger.error
        self.info = self._logger.info
        self.debug = self._logger.debug


logfile = "./logs/" + time.strftime("%Y%m%d") + '.log'
logger = AppLogger("tg2m", logfile)
logger.info("log service started")
