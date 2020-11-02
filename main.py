import yaml
# update at: 2020-01-13
# python: 3.6.3

import os
import platform
import random
import re
import time
import traceback

import html2text
from PIL import Image
import requests
from selenium import webdriver
from tqdm import tqdm


def random_sleep(min=1, max=3):
    time.sleep(random.random() * (max - min) + min)


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def webp_to_jpg(input_name, output_name):
    im = Image.open(input_name)
    if im.mode == "RGBA":
        im.load()
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[3])
        im = background
    im.save('{}.jpg'.format(output_name), 'JPEG')
    os.remove(input_name)


class Helper:
    JUEJIN_HOST = 'https://juejin.im/'
    JUEJIN_BOOK_URL_FORMAT = 'https://juejin.im/book/{book_id}'

    multiple_blank_lines_pattern = re.compile('\n+', re.S)
    image_src_pattern = re.compile(r'data-src="(.*?)"', re.S)
    download_image_headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
    }

    def __init__(self, juejin_account, juejin_password, book_ids, save_dir, chromedriver_path):
        self.juejin_account = juejin_account
        self.juejin_password = juejin_password
        self.book_ids = [book_ids] if isinstance(book_ids, str) else book_ids
        self.save_dir = save_dir
        self.chromedriver_path = chromedriver_path

    def init_chrome_options(self, proxy=None):
        """
        初始化启动参数
        """
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')   # 设置成无界面
        # chrome_options.add_argument('--no-sandbox')   # 禁用沙盒 解决linux下root用户无法运行的问题

        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')

        # 设置成不加载图片
        # prefs = {'profile.managed_default_content_settings.images': 2}
        # chrome_options.add_experimental_option('prefs', prefs)

        self.chrome_options = chrome_options

    def init_driver(self):
        self.driver = webdriver.Chrome(
            executable_path=self.chromedriver_path,
            chrome_options=self.chrome_options
        )
        self.driver.implicitly_wait(10)  # 设置隐式等待时间为10秒

    def login_juejin(self):
        """
        打开浏览器并登陆掘金
        """
        self.driver.get(self.JUEJIN_HOST)
        self.driver.find_element_by_class_name('login-button').click()
        if all([self.juejin_account, self.juejin_password]):
            # 点击其他登录方式
            self.driver.find_element_by_css_selector('.prompt-box .clickable').click()
            random_sleep()

            self.driver.find_element_by_name('loginPhoneOrEmail').send_keys(self.juejin_account)
            random_sleep()
            self.driver.find_element_by_name('loginPassword').send_keys(self.juejin_password)
            random_sleep()
            self.driver.find_element_by_css_selector('.panel .btn').click()
            random_sleep()

            # 这里需要滑动验证码
            print('请滑动验证码...')
            time.sleep(20)
        else:
            print('你未设置账号密码，请手动输入进行登陆...')
            time.sleep(20)

    def close_useless_panel(self):
        try:
            [_.click() for _ in self.driver.find_elements_by_css_selector('.ion-close')]
        except:
            pass

    def deal_book(self, book_id):
        """
        处理书籍
        """
        book_url = self.JUEJIN_BOOK_URL_FORMAT.format(book_id=book_id)
        random_sleep()
        self.driver.get(book_url)
        random_sleep()
        book_name = self.driver.find_element_by_css_selector('.title-line .title').text
        save_book_dir = os.path.join(self.save_dir, book_name)
        makedirs(save_book_dir)

        img_dir = os.path.join(save_book_dir, 'img')
        makedirs(img_dir)

        sections = self.driver.find_elements_by_css_selector('.section.section-link')
        sections_pbar = tqdm(range(len(sections)))
        self.close_useless_panel()
        for i in sections_pbar:
            sections = self.driver.find_elements_by_css_selector('.section.section-link')

            current_section = sections[i]
            while True:
                try:
                    section_title = current_section.find_element_by_class_name('title').text
                except:
                    random_sleep()
                else:
                    break
            while True:
                try:
                    current_section.click()
                except:
                    random_sleep()
                    self.close_useless_panel()
                    self.driver.execute_script('window.scrollBy(0, 244)')
                else:
                    break
            sections_pbar.set_description(f'正在处理第{i+1}章-{section_title}')
            section_order = i + 1
            section_markdown_save_path = os.path.join(save_book_dir, f'{section_order}-{section_title}.md')
            if os.path.exists(section_markdown_save_path):
                print(f'{section_markdown_save_path}已经存在，跳过处理...')
                continue
            section_img_save_dir = os.path.join(img_dir, str(section_order))
            makedirs(section_img_save_dir)
            section_content_html = self.driver.find_element_by_css_selector('.article-content').get_attribute('innerHTML')
            try:
                self.covert_html_to_markdown(section_order, section_markdown_save_path, section_img_save_dir, section_content_html)
            except Exception as e:
                print(f'转换markdown出错，请手动处理...:{section_title}-{e}')
                traceback.print_exc()

    def covert_html_to_markdown(self, section_order, section_markdown_save_path, section_img_save_dir, section_content_html):
        """
        将html转为markdown，并且下载图片
        """
        img_urls = re.findall(self.image_src_pattern, section_content_html)
        imgs_pbar = tqdm(img_urls)
        for img_url in imgs_pbar:
            imgs_pbar.set_description(f'正在处理{img_url}')
            try:
                section_content_html = self.download_img(img_url, section_order, section_img_save_dir, section_content_html)
            except Exception as e:
                print(f'下载图片出错，请手动处理...:{img_url}-{e}')
                traceback.print_exc()

        markdown = html2text.html2text(section_content_html)
        markdown = re.sub(self.multiple_blank_lines_pattern, '\n', markdown)
        with open(section_markdown_save_path, 'w', encoding='utf8') as f:
            f.write(markdown)

    def download_img(self, url, section_order, section_img_save_dir, section_content_html):
        """
        下载图片并转化(普通图片是webp，要转jpg，还有可能是gif)，还要替换html中的图片链接
        """
        filename = f'{int(time.time() * 1000)}'
        pattern = re.compile('data-src="{img_url}.*?</svg>'.format(img_url=url.replace('.', '\.').replace('?', '\?')), re.S)
        file_save_path = os.path.join(section_img_save_dir, filename)
        res = requests.get(url, headers=self.download_image_headers)
        with open(file_save_path, 'wb') as f:
            f.write(res.content)
        if res.headers.get('content-type') == 'image/webp':
            webp_to_jpg(file_save_path, file_save_path)
            re_sub_str = f'img/{section_order}/{filename}.jpg'
        elif res.headers.get('content-type') == 'image/gif':
            os.rename(file_save_path, f'{file_save_path}.gif')
            re_sub_str = f'img/{section_order}/{filename}.gif'
        else:
            re_sub_str = f'img/{section_order}/{filename}'
            print(f'未知的图片类型，请手动处理:{url}')
        section_content_html = re.sub(pattern, 'src="' + re_sub_str, section_content_html)
        return section_content_html

    def main(self):
        self.init_chrome_options()
        self.init_driver()

        self.login_juejin()

        books_pbar = tqdm(self.book_ids)
        for i, book_id in enumerate(books_pbar):
            books_pbar.set_description(f'正在处理第{i+1}本书-{book_id}')
            self.deal_book(book_id)

        input('处理完成，按任意键退出!')
        self.driver.quit()


if __name__ == '__main__':
    with open('config.yml', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    config['save_dir'] = config['save_dir'] or os.path.dirname(os.path.abspath(__file__))
    helper = Helper(**config)
    helper.main()
