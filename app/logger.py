import logging


class Logger:
    logger = None

    @classmethod
    def get_logger(cls):
        if cls.logger is None:
            logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
            logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')
            cls.logger = logging.getLogger(__name__)
