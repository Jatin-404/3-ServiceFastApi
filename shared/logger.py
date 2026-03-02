import logging
import os ,sys
from pythonjsonlogger import jsonlogger

def setup_logger(service_name: str) -> logging.Logger:

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger
    
    log_format = (
        "%(asctime)s %(levelname)s %(name)s "
        "service=%(service)s %(message)s"
    )

#    formatter = logging.Formatter(log_format)               this is for non json logs
    formatter = jsonlogger.JsonFormatter(log_format)       # this is for json logs

    if os.getenv("LOCAL_ENV" , "local") == "local":
        file_handler = logging.FileHandler(f"{service_name}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


    return logging.LoggerAdapter(logger, {"service": service_name})