import logging
from app.config import settings


class Logger:
    logger = None

    @classmethod
    def get_logger(cls):
        if cls.logger is None:
            log_level = settings.log_level.upper()
            logging.basicConfig(
                level=getattr(logging, log_level),
                format="[%(asctime)s] [%(levelname)s] %(message)s"
            )
            cls.logger = logging.getLogger(__name__)
        return cls.logger
