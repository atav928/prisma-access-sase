# pylint: disable=invalid-name,too-many-arguments
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


def set_logdir() -> str:
    """Sets default log dir to users home dir

    Returns:
        _type_: _description_
    """
    return str(Path.home())


def with_suffix(logName):
    """ensures that the logName passed has .log at the end

    Args:
        logName (str): name of log

    Returns:
        str: formated log name ensures .log attached
    """
    return str(Path(logName).with_suffix('.log'))


class RotatingLog:
    """Rotating Logger"""

    def __init__(self, name: str,
                 logName: str = 'sample.log',
                 logDir: (str | None) = None,
                 maxBytes: int = 5242990,
                 backupCount: int = 5,
                 mode: str = 'a',
                 level: str = 'INFO',
                 stream: bool = True):
        """ Creates an instance for each new Rotating Logger"""
        logDir = logDir if logDir else set_logdir()
        logName = with_suffix(logName)
        # ensure logDir exists create it if it does not
        self.createLogDir(logDir=Path(logDir))
        self.stream = stream
        # Set up settings for logger
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
        """Gets Logger or adds a new one if name doesnot already exist

        Args:
            name (str, optional): Returns root logger or the specifc named logger. Defaults to None.

        Returns:
            Logger: Rotate Logger
        """
        return logging.getLogger(self.settings.name) if not name else self.addLogger(name)

    def addLogger(self, name):
        """Adds a new Logger to the Rotating logger that attaches to the Root

        Args:
            name (str): Name of new logger

        Returns:
            Logger: instance of Rotating Logger
        """
        self.logger = logging.getLogger(name).setLevel(self.settings.level)
        self.logger = logging.getLogger(name).addHandler(self.file_handler)
        self.logger = logging.getLogger(name).propagate = False
        if self.stream:
            self.logger = logging.getLogger(name).addHandler(self.stream_handler)
        return logging.getLogger(name)

    def createLogDir(self, logDir: Path) -> None:
        """Creates log dir if it doesnot exist

        Args:
            logDir (Path): _description_
        """
        if not Path.exists(logDir):
            Path(logDir).mkdir(parents=True, exist_ok=True)
