from spider import *


def test_parse_hospitals_from_county_page():
    test_data = {
        "山西省忻州市五台县": "http://www.a-hospital.com/w/%E5%BF%BB%E5%B7%9E%E5%B8%82%E4%BA%94%E5%8F%B0%E5%8E%BF%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8",
        "湖北省宜昌市点军区": "http://www.a-hospital.com/w/%E5%AE%9C%E6%98%8C%E5%B8%82%E7%82%B9%E5%86%9B%E5%8C%BA%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8",
        "湖北省宜昌市宜都市": "http://www.a-hospital.com/w/%E5%AE%9C%E9%83%BD%E5%B8%82%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8",
        "北京市朝阳区": "http://www.a-hospital.com/w/%E5%8C%97%E4%BA%AC%E5%B8%82%E6%9C%9D%E9%98%B3%E5%8C%BA%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8",
        "无锡冰壶": "http://www.a-hospital.com/w/%E6%97%A0%E9%94%A1%E5%B8%82%E6%BB%A8%E6%B9%96%E5%8C%BA%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8",
        "cc": "http://www.a-hospital.com/w/%E5%A8%81%E6%B5%B7%E5%B8%82%E7%8E%AF%E7%BF%A0%E5%8C%BA%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8",
    }

    for county in test_data:
        print(county, ": ", parse_hospitals_from_county_page(test_data[county]))


if __name__ == "__main__":
    test_parse_hospitals_from_county_page()
