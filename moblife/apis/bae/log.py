import logging

_path = '/home/bae/log/%s.log'

def getLogger(name = None, fh = None):
    if name is None:
        logger = logging.getLogger()
        handler = logging.FileHandler(_path % 'log')
    else:
        logger = logging.getLogger(name)
        if fh is None:
            fh = name
        handler = logging.FileHandler(_path % fh)
    logger.addHandler(handler)
    return logger