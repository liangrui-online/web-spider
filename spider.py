import re

import requests
from lxml import etree
from faker import Factory

from dump_and_load import *
from utils import *

fc = Factory.create()
base_url = "http://www.a-hospital.com"


def load_html_with_lxml(func):
    def wrapper(*args, **kwargs):
        html_text = func(*args, **kwargs)
        return etree.HTML(html_text)

    return wrapper


# 下载网页
@load_html_with_lxml
@cache
def download_page(url) -> str:
    if "index.php" in url:
        raise requests.exceptions.HTTPError()
    headers = {"User-Agent": fc.user_agent()}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text


# 获取省份列表
def get_province_list(home_page_url="http://www.a-hospital.com/w/全国医院列表") -> dict:
    try:
        page = download_page(home_page_url)
    except requests.exceptions.HTTPError as e:
        logger.warning(f"页面无法访问：{url_decode(home_page_url)}")
        return {}

    pvc = page.xpath('//*[@id="bodyContent"]/h3/span/text()') + page.xpath(
        '//*[@id="bodyContent"]/h3/span/a/text()'
    )
    links = page.xpath('//*[@id="bodyContent"]/p/b/a') + page.xpath(
        '//*[@id="bodyContent"]/h3/span/a'
    )
    province_name_list = list(filter(lambda x: x, map(remove_suffix, pvc)))
    province_link_list = [base_url + p.get("href") for p in links]
    return dict(zip(province_name_list, province_link_list))


# 获取市级列表
def get_city_list(province_detail_page_url) -> dict:
    try:
        page = download_page(province_detail_page_url)
    except requests.exceptions.HTTPError as e:
        logger.warning(f"页面无法访问：{url_decode(province_detail_page_url)}")
        return {}

    city_link = page.xpath('//*[@id="bodyContent"]/p[2]/a')
    return {i.text: base_url + i.get("href") for i in city_link}


# 获取县级列表
def get_county_list(city_detail_page_url) -> dict:
    try:
        page = download_page(city_detail_page_url)
    except requests.exceptions.HTTPError as e:
        logger.warning(f"页面无法访问：{url_decode(city_detail_page_url)}")
        return {}

    city_link = page.xpath('//*[@id="bodyContent"]/ul[1]/li/a')
    return {
        remove_suffix(i.text, "医院").replace(" ", ""): base_url + i.get("href")
        for i in city_link
    }


# 从县级别详情页获取医院信息
def parse_hospitals_from_county_page(county_page_url) -> list:
    hospitals = []

    try:
        county_page = download_page(county_page_url)
    except requests.exceptions.HTTPError as e:
        logger.warning(f"页面无法访问：{url_decode(county_page_url)}")
        return hospitals

    province_name = county_page.xpath('//*[@class="nav"][1]//a[3]/text()')[0]
    province_name = re.sub(r"(医院列表)", "", province_name, count=1)

    try:
        city_name = county_page.xpath('//*[@class="nav"][1]//a[4]/text()')[0]
        city_name = re.sub(r"(医院列表)", "", city_name, count=1)
    except IndexError:
        city_name = county_page.xpath('//*[@class="nav"][1]//td/text()[last()]')[0]
        city_name = re.sub(f"[(医院列表)({province_name}) >]", "", city_name)

    try:
        county_name = county_page.xpath('//*[@class="nav"][1]//td/text()[last()]')[0]
        county_name = re.sub(
            f"[(医院列表)({province_name})({city_name}) >]", "", county_name
        )
    except IndexError:
        county_name = ""

    for item in county_page.xpath('//*[@id="bodyContent"]/ul[last()-1]/li'):
        # print(url_decode(etree.tostring(item, encoding="unicode", pretty_print=True)))
        hospital_title_with_link = item.xpath("./b/a")
        if hospital_title_with_link:
            hospital_name = hospital_title_with_link[0].text + "".join(
                item.xpath("./b/text()")
            )
            hospital_url = url_decode(hospital_title_with_link[0].get("href"))
        else:
            # 无锡市滨湖区荣巷医院?无锡和平骨科医院
            hospital_name = "".join(item.xpath("./b/text()"))
            hospital_url = ""

        hospital_info = {
            "医院名称": hospital_name,
            "医院主页": base_url + hospital_url,
            "省级行政区": province_name,
            "地级行政区": city_name,
            "县级行政区": county_name,
        }
        for attr in item.xpath("./ul[1]/li"):
            attr_name = attr.xpath("./b/text()")[0]
            attr_value = "、".join(
                list(
                    filter(
                        lambda x: x and x not in ("：", "、"),
                        map(
                            lambda s: s.replace(" ", "")
                            .replace("：", "")
                            .replace("、", ""),
                            attr.xpath("./text()") + attr.xpath("./a/text()"),
                        ),
                    )
                )
            )
            hospital_info[attr_name] = attr_value
        # hospital_info_words = list(filter(lambda x: x and x != "：", map(lambda s: s.strip().strip("："), (
        #         item.xpath("./ul[1]/li/b/text()") +
        #         item.xpath("./ul[1]/li/text()") +
        #         item.xpath("./ul[1]/li/a[1]/text()")
        # ))))
        #
        # key_num = int(len(hospital_info_words) / 2)
        # for i in range(key_num):
        #     hospital_info[hospital_info_words[i]] = hospital_info_words[i + key_num]
        hospitals.append(hospital_info)
    return hospitals


@logger.catch
@dump_data
def get_hospital_list():
    hospitals = []
    for p_name, p_link in get_province_list().items():
        logger.info(f"【{p_name}】 开始下载 ⚡️⚡️⚡️")
        for c_name, c_link in get_city_list(province_detail_page_url=p_link).items():
            if p_name in (  # 直辖市的片区没有"县"
                "北京市",
                "上海市",
                "重庆市",
                "天津市",
            ) or c_name in (  # 地级行政区没有下属辖区
                "天门市",
                "仙桃市",
                "济源市",
                "神农架林区",
                "潜江市",
            ):
                new_hospitals = parse_hospitals_from_county_page(county_page_url=c_link)
                logger.info(f"【{p_name}】【{c_name}】 解析到{len(new_hospitals)}家医院")
                hospitals.extend(new_hospitals)
            else:  # 正常的 省、市、县 三级结构
                county = get_county_list(city_detail_page_url=c_link)
                for x_name, x_link in county.items():
                    new_hospitals = parse_hospitals_from_county_page(
                        county_page_url=x_link
                    )
                    hospitals.extend(new_hospitals)
                    logger.info(f"【{p_name}】【{c_name}】【{x_name}】 解析到{len(new_hospitals)}家医院")
        logger.info(f"【{p_name}】 下载完毕 🍺🍺🍺")
    logger.info(f"医院信息获取完成，共解析到{len(hospitals)}家医院信息。")
    return hospitals
