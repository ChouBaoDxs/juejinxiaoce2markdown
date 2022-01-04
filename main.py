import logging
import os
import re
import traceback
from urllib.request import urlretrieve
import yaml

import html2text
import requests

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)7s: %(message)s')
logger = logging.getLogger(__name__)


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def clear_slash(s: str) -> str:
    return s.replace('\\', '').replace('/', '').replace('|', '')


class Juejinxiaoce2Markdown:
    img_pattern = re.compile(r'!\[.*?\]\((.*?)\)', re.S)

    def __init__(self, config: dict):
        logger.info(config)
        pwd = os.path.dirname(os.path.abspath(__file__))
        default_save_dir = os.path.join(pwd, 'book')
        sessionid: str = config['sessionid']
        self.book_ids: list = config['book_ids']
        self.save_dir: str = config.get('save_dir', default_save_dir)
        self.request_headers = {
            'cookie': f'sessionid={sessionid};',
        }
        makedirs(self.save_dir)

    def get_section_res(self, section_id):
        url = f'https://api.juejin.cn/booklet_api/v1/section/get'
        data = {
            'section_id': str(section_id)
        }
        res = requests.post(url, headers=self.request_headers, json=data)
        # logger.info(res.text)
        return res

    def get_book_info_res(self, book_id) -> requests.Response:
        url = f'https://api.juejin.cn/booklet_api/v1/booklet/get'
        data = {
            'booklet_id': str(book_id)
        }
        res = requests.post(url, headers=self.request_headers, json=data)
        # logger.info(res.text)
        return res

    @classmethod
    def save_markdown(cls, markdown_file_path, section_img_dir, markdown_relative_img_dir, markdown_str):
        img_urls = re.findall(cls.img_pattern, markdown_str)
        for img_index, img_url in enumerate(img_urls):
            new_img_url: str = img_url.replace('\n', '')
            if new_img_url.startswith('//'):
                new_img_url = f'https:{new_img_url}'
            try:
                suffix = os.path.splitext(new_img_url)[-1]
                img_file_name = f'{img_index + 1}{suffix}'.replace('?', '')
                md_relative_img_path = os.path.join(markdown_relative_img_dir, img_file_name)
                img_save_path = os.path.join(section_img_dir, img_file_name)
                urlretrieve(new_img_url, img_save_path)
                markdown_str = markdown_str.replace(img_url, md_relative_img_path)
            except Exception as e:
                logger.error({
                    'msg': '处理图片失败',
                    'img_url': new_img_url,
                    'e': repr(e),
                    'traceback': traceback.format_exc(),
                    'markdown_relative_img_dir': markdown_relative_img_dir
                })
        with open(markdown_file_path, 'w', encoding='utf8') as f:
            f.write(markdown_str)

    def deal_a_book(self, book_id):
        log_data = {
            'book_id': book_id,
            'msg': '开始处理小册'
        }
        logger.info(log_data)

        res = self.get_book_info_res(book_id)
        res_json = res.json()
        book_title = res_json['data']['booklet']['base_info']['title']
        section_list = res_json['data']['sections']
        book_title = clear_slash(book_title)
        logger.info({'book_title': book_title})
        book_save_path = os.path.join(self.save_dir, book_title)
        img_dir = os.path.join(book_save_path, 'img')
        makedirs(img_dir)

        section_id_list = [e['section_id'] for e in section_list]

        section_count = len(section_id_list)
        for index, section_id in enumerate(section_id_list):
            section_order = index + 1
            logger.info({
                '进度': f'{section_order}/{section_count}',
                'msg': '处理 section',
                'section_id': section_id
            })
            res = self.get_section_res(section_id)
            res_json = res.json()
            section_title = res_json['data']['section']['title']
            section_title = clear_slash(section_title)
            markdown_html_str = res_json['data']['section']['content']
            markdown_str = html2text.html2text(markdown_html_str)
            # markdown_str = res_json['data']['section']['markdown_show']
            markdown_file_path = os.path.join(book_save_path, f'{section_order}-{section_title}.md')
            section_img_dir = os.path.join(img_dir, f'{section_order}')
            makedirs(section_img_dir)
            markdown_relative_img_dir = os.path.join('img', f'{section_order}')
            self.save_markdown(markdown_file_path, section_img_dir, markdown_relative_img_dir, markdown_str)

        log_data['msg'] = '处理完成'
        logger.info(log_data)

    def main(self):
        for book_id in self.book_ids:
            try:
                self.deal_a_book(book_id)
            except Exception as e:
                log_data = {
                    'book_id': book_id,
                    'e': repr(e),
                    'traceback': traceback.format_exc(),
                    'msg': '处理小册出错'
                }
                logger.error(log_data)


if __name__ == '__main__':
    with open('config.yml', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    helper = Juejinxiaoce2Markdown(config)
    helper.main()
