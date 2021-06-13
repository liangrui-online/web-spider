import os
import json
from typing import List, Dict

import xlwt

from config import *
from utils import logger, get_md5


# 缓存已下载的网页，减少网络请求数
def cache(func):
    if not os.path.exists(HTML_CACHE_DIR):
        os.mkdir(HTML_CACHE_DIR)
        logger.debug(f"创建缓存文件夹{HTML_CACHE_DIR}成功")

    if not os.path.exists(HTML_CACHE_INDEX):
        with open(HTML_CACHE_INDEX, "w") as f:
            json.dump({}, f)
            logger.debug(f"创建缓存目录{HTML_CACHE_INDEX}成功")

    def wrapper(url):
        # 加载缓存目录
        with open(HTML_CACHE_INDEX, "r") as fp:
            local_data = json.load(fp)

        # 生成缓存文件名
        obj_name = get_md5(url)
        obj_path = f"{HTML_CACHE_DIR}/{obj_name}.html"

        if obj_name in local_data:
            logger.debug("url已下载，从缓存文件获取")
            with open(obj_path, "r") as f:
                file_content = f.read()
        else:
            logger.debug("url未下载，从网络请求获取")
            file_content = func(url)
            local_data[obj_name] = obj_path
            with open(obj_path, "w") as f:
                f.write(file_content)
                logger.debug("url已缓存")

            with open(HTML_CACHE_INDEX, "w") as fp:
                json.dump(local_data, fp)
                logger.debug("缓存文件已更新")

        return file_content

    return wrapper


# 存储函数运行结果
def dump_data(func, filename=DEFAULT_HOSPITAL_FILENAME):
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data

    return wrapper


# 获取所有医院属性的并集
def get_data_keys(data: List[Dict[str, str]]) -> List[str]:
    """

    :param data:
    :return: {
                '电子邮箱', '经营方式', '医院网站', '乘车路线', '传真号码', '省级行政区', '医院等级',
                '医院网址', '重点科室', '地级行政区', '医院名称', '县级行政区', '医院主页', '医院地址', '联系电话'
            }
    """
    keys = set()
    for item in data:
        keys.update(set(list(item.keys())))

    return list(keys)


# 医院数据写入Excel表格
def save2excel(data, excel_file_name="全国医院汇总.xls"):
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet("Worksheet1")

    # 写表头
    keys = (
        "医院名称",
        "省级行政区",
        "地级行政区",
        "县级行政区",
        "医院等级",
        "经营方式",
        "重点科室",
        "医院地址",
        "联系电话",
        "电子邮箱",
        "传真号码",
        "医院网站",
        "医院网址",
        "医院主页",
        "乘车路线",
    )
    for index, key in enumerate(keys):
        # 行, 列, 值
        worksheet.write(0, index, label=key)

    # 填表
    for l_index, item in enumerate(data):
        for k_index, k in enumerate(keys):
            worksheet.write(l_index + 1, k_index, label=item.get(k))

    # 保存
    workbook.save(excel_file_name)
    logger.info(f"{excel_file_name} 写入完成")
