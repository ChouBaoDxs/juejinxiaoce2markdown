# juejinxiaoce2markdown
Python3 将掘金小册保存为本地 markdown （会处理图片）

# 分支一：master
Python3 将掘金小册保存为本地 markdown

## 使用指南
1. 安装依赖
    ```shell
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    ```
2. 根据实际情况修改 config.yml
    ```yaml
    sessionid: "{这里填写自己的sessionid}" # 填写 cookie 里的 sessionid
    book_ids: # 要爬取的小册id(在url里可以找到)，必须是上面账号已购的小册
    #  - 6844733722936377351 # 深入理解 RPC : 基于 Python 自建分布式高并发 RPC 服务
    #  - 6844733712102326279 # 大厂 H5 开发实战手册
    #  - 6844733730678898702 # 基于 Go 语言构建企业级的 RESTful API 服务
    #  - 6844733718335062030 # 基于 Python 轻松自建 App 服务器
      - 6844733813021491207 # 深入浅出TypeScript：从基础知识到类型编程
      - 6844733800300150797 # 前端算法与数据结构面试：底层逻辑解读与大厂真题训练
      - 6897616008173846543 # 从 0 到 1 实现一套 CI/CD 流程
    save_dir: "book" # 保存小册的目录，默认会在当前目录下新建一个 book 目录
    ```
3. 运行主程序：`python3 main.py`
4. 爬取结果预览：
```
├── book
│   └── 深入浅出TypeScript：从基础知识到类型编程
│       ├── 1-小册食用指南.md
│       ├── 2-到底为什么要学习 TypeScript？.md
│       └── img
│           ├── 1
│           │   └── 1
│           └── 2
│               ├── 1
│               ├── 2
│               ├── 3
│               ├── 4
│               └── 5
├── config.yml
├── main.py
└── requirements.txt
```
# 分支二：crawl_by_chromedriver
Python3 + Selenium 将掘金小册保存为本地 markdown （会处理图片）

注意：该分支使用到了 Selenium + Chromedriver，配置起来比较繁琐，不推荐使用也不再维护

## 使用指南
1. 下载chromedriver
- chromedriver下载地址：http://npm.taobao.org/mirrors/chromedriver/
- 注意：请根据你的chrome版本和操作系统版本下载对应的chromedriver

2. 安装Python依赖
- 建议使用pipenv或virtualenvwrapper之类的虚拟环境管理工具创建一个干净的Python3环境

- 安装依赖：
  ```
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  ```

3. 根据实际情况修改config.yml
```yaml
juejin_account: "juejin_account" # 掘金登录账号
juejin_password: "juejin_password" # 掘金登录密码
book_ids: # 要爬取的小册id(在url里可以找到)，必须是上面账号已购的小册
  - 5af56a3c518825426642e004 # 深入理解 RPC : 基于 Python 自建分布式高并发 RPC 服务
  - 5a7bfe595188257a7349b52a # 大厂 H5 开发实战手册
  - 5b0778756fb9a07aa632301e # 基于 Go 语言构建企业级的 RESTful API 服务
chromedriver_path: "chromedriver_mac" # chromedriver可执行文件的绝对路径
save_dir: "./book" # 保存小册的目录，默认为当前目录
```

4. 开始爬取
```
python main.py
```

5. 爬取结果预览
```
├── LICENSE
├── README.md
├── book
│   └── 大厂 H5 开发实战手册
│       ├── 1-大厂 H5 开发概述.md
│       ├── 2-动效开发 1：让它动起来.md
│       └── img
│           ├── 1
│           │   ├── 1579078752898.jpg
│           │   ├── 1579078753089.jpg
│           │   └── 1579078753211.jpg
│           └── 2
│               ├── 1579078753661.gif
│               ├── 1579078753805.gif
│               ├── 1579078754651.jpg
│               └── 1579078754741.gif
├── config.yml
├── main.py
└── requirements.txt
```

## 后续问题
**20210120**
发现输入账号密码+拖动验证码无法登录，建议采用微信扫码登录