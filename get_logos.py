import yaml
import os
import requests
import time
from urllib.parse import urlparse

# 递归函数来处理可能的嵌套结构
def download_logos(data, logo_save_path):
    for item in data:
        if 'links' in item:
            for link in item['links']:
                title = link['title']
                url = link.get('url', '')
                logo = link.get('logo', '')
                ignore = link.get('ignore', False)

                if ignore:
                    continue

                if not url or not logo:  # 检查URL和logo字段是否为空
                    print(f"跳过 {title}，因为URL或logo字段为空")
                    continue

                # 提取网站的域名（去掉http和https）
                parsed_url = urlparse(url)
                scheme = parsed_url.scheme
                domain = parsed_url.hostname
                port = parsed_url.port

                # 构建API下载地址
                if port:
                    api_url = f"{scheme}://{domain}:{port}/favicon.ico"
                else:
                    api_url = f"{scheme}://{domain}/favicon.ico"

                print(f"尝试下载 {domain} 的favicon.ico 图片")

                # 下载logo图片
                response = requests.get(api_url)
                content_type = response.headers.get('Content-Type', '').lower()

                if response.status_code == 200 and ('image' in content_type or 'stream' in content_type):
                    # 检查响应状态码为200，并且响应的Content-Type以'image'开头，以确保响应是一个图像文件
                    logo_file_path = os.path.join(logo_save_path, logo)
                    with open(logo_file_path, 'wb') as img_file:
                        img_file.write(response.content)
                    print(f"已下载 {domain} 的favicon.ico 图片为 {logo_file_path}")
                else:
                    print(f"无法下载 {domain} 的favicon.ico 图片，尝试使用备用接口")

                    # 使用备用iowen接口下载
                    # backup_api_url = f"https://api.iowen.cn/favicon/{domain}.png"
                    backup_api_url = f"https://api.xinac.net/icon/?url={url}"
                    backup_response = requests.get(backup_api_url)
                    content_type = backup_response.headers.get('Content-Type', '').lower()

                    if backup_response.status_code == 200 and ('image' in content_type or 'stream' in content_type):
                        logo_file_path = os.path.join(logo_save_path, logo)
                        with open(logo_file_path, 'wb') as img_file:
                            img_file.write(backup_response.content)
                        print(f"已下载 {domain} 的favicon.png 图片为 {logo_file_path}")
                    else:
                        print(f"无法下载 {domain} 的favicon.png 图片")

        if 'list' in item:
            download_logos(item['list'], logo_save_path)

# 读取YAML文件
yaml_file_path = './data/webstack.yml'
logo_save_path = './logos'

if not os.path.exists(logo_save_path):
    os.makedirs(logo_save_path)
else:
    for file in os.listdir(logo_save_path):
        file_path = os.path.join(logo_save_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f"无法删除 {file_path}: {e}")

with open(yaml_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

# 调用递归函数处理可能的嵌套结构
download_logos(data, logo_save_path)
