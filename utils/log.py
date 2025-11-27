import loguru
import os

def get_logger(name: str = "app"):
    logger = loguru.logger.bind(name=name)
    # 确保logs目录存在
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # 保存到logs目录下的文件，按天分割
    logger.add(f"logs/{name}_.log", rotation="00:00", retention="7 days", encoding="utf-8", enqueue=True)
    return logger