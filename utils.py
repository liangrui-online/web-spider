import sys
import urllib.parse
from hashlib import md5

import loguru

logger = loguru.logger
logger.remove()
handler_id = logger.add(sys.stdout, level="INFO")


# 计算字符串的哈希值
def get_md5(string: str):
    m = md5()
    m.update(string.encode())
    return m.hexdigest()


# 移除字符串后缀
def remove_suffix(string: str, suffix: str = "医院列表"):
    return string.rstrip(suffix)


# 解码URL中的中文
def url_decode(string: str):
    return urllib.parse.unquote(string)
