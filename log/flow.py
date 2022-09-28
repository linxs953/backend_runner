from loguru import logger


def flow_logger(key):
    def wrapped(func):
        def log(*args,**kwargs):
            logger.debug(f"开始执行  <{key}>")
            res = func(*args,**kwargs)
            logger.debug(f"执行 <{key}> 成功")
            return res
        return log
    return wrapped