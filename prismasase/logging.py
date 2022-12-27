"""Logger"""
import logging
import logging.handlers
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

LOGVALUE = {
    'NOTSET': 0,
    'DEBUG': 10,
    'INFO': 20,
    'WARN': 30,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50,
    'FATAL': 50
}


class LogValue(Enum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARN = 30
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    FATAL = 50


@dataclass
class Logger:
    name: str
    logDir: str = ''
    logName: str = 'sample.log'
    maxBytes: int = 5242990
    backupCount: int = 5
    mode: str = 'a'
    level: str = 'INFO'
    stream: bool = True
    level_set: dict = field(default_factory=lambda: {})
    propegate: bool = False


def set_logdir():
    return Path.home()


def with_suffix(logName):
    return str(Path(logName).with_suffix('.log'))


class RotatingLog:
    def __init__(self, name: str, logName='sample.log', logDir=None,
                 maxBytes=5242990, backupCount=5, mode='a', level='INFO', stream=True):
        """ Creates an instance for each new Rotating Logger"""
        logDir = logDir if logDir else set_logdir()
        logName = with_suffix(logName)
        # ensure logDir exists create it if it does not
        self.createLogDir(logDir=Path(logDir))
        self.stream = stream
        self.settings = Logger(
            name=name, logDir=logDir, logName=logName, maxBytes=maxBytes, backupCount=backupCount,
            mode=mode, level=level, level_set=LOGVALUE)
        self.formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        self.file_handler = logging.handlers.RotatingFileHandler(
            Path.joinpath(Path(self.settings.logDir) / self.settings.logName),
            mode=self.settings.mode, maxBytes=self.settings.maxBytes,
            backupCount=self.settings.backupCount)
        self.file_handler.setFormatter(self.formatter)

        if self.stream:
            self.stream_formatter = logging.Formatter('%(levelname)-8s: %(message)s')
            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setFormatter(self.stream_formatter)

        self.logger = logging.getLogger(self.settings.name).setLevel(self.settings.level)
        self.logger = logging.getLogger(self.settings.name).addHandler(self.file_handler)
        self.logger = logging.getLogger(self.settings.name).propagate = False
        if self.stream:
            self.logger = logging.getLogger(self.settings.name).addHandler(self.stream_handler)

    def getLogger(self, name=None):
        return logging.getLogger(self.settings.name) if not name else self.addLogger(name)

    def addLogger(self, name):
        self.logger = logging.getLogger(name).setLevel(self.settings.level)
        self.logger = logging.getLogger(name).addHandler(self.file_handler)
        self.logger = logging.getLogger(name).propagate = False
        if self.stream:
            self.logger = logging.getLogger(name).addHandler(self.stream_handler)
        return logging.getLogger(name)

    def createLogDir(self, logDir: Path) -> None:
        if not Path.exists(logDir):
            Path(logDir).mkdir(parents=True, exist_ok=True)
