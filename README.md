# 获取医院列表

## 数据源
- 网站地址：http://www.a-hospital.com/w/全国医院列表
- 更新时间：2012年左右
- 注意：本项目仅限于学习爬虫技术，请勿用于其他用途！！！

## 技术栈
- 基于python开发
- 使用`requests`发送http请求
- 使用`lxml`解析html数据
- 使用`xlwt`生成Excel文件
- 使用`loguru`输出日志

## 快速开始
1. 创建并进入python虚拟环境
```shell
virtualenv .venv --python=python3
source .venv/bin/activate
```
2. 安装依赖包
```shell
pip install -r requirements.txt -i https://pypi.doubanio.com/simple/
```
3. 启动脚本，耐心等待程序结束
```shell
python main.py
```