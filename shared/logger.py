import logging


def setup_logger(service_name: str) -> logging.Logger:

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger
    
    log_format = (
        "%(asctime)s %(levelname)s %(name)s "
        "service=%(service)s %(message)s"
    )

    formatter = logging.Formatter(log_format)
    file_handler = logging.FileHandler(f"{service_name}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


    return logging.LoggerAdapter(logger, {"service": service_name})