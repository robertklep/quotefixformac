from Foundation import NSLog

class Logger:
    DEBUG       = 1
    INFO        = 2
    WARNING     = 3
    ERROR       = 4
    CRITICAL    = 5

    def __init__(self, level = INFO):
        self.setLevel(level)

    def setLevel(self, level):
        self.level = level

    def debug(self, fmt, **args):
        self.log(self.DEBUG, fmt, **args)

    def info(self, fmt, **args):
        self.log(self.INFO, fmt, **args)

    def warning(self, fmt, **args):
        self.log(self.WARNING, fmt, **args)

    def error(self, fmt, **args):
        self.log(self.ERROR, fmt, **args)

    def critical(self, fmt, **args):
        self.log(self.CRITICAL, fmt, **args)

    def log(self, minlevel, fmt, **args):
        if minlevel >= self.level:
            NSLog(fmt, **args)

logger = Logger()

if __name__ == '__main__':
    logger.debug('this is a debug message');
    logger.info('this is a info message');
    logger.warning('this is a warning message');
    logger.error('this is a error message');
    logger.critical('this is a critical message');
