# juejinxiaoce2markdown
Python3 + Selenium 将掘金小册保存为本地 markdown （会处理图片）

## 使用指南
### 下载chromedriver
- chromedriver下载地址：http://npm.taobao.org/mirrors/chromedriver/
- 注意：请根据你的chrome版本和操作系统版本下载对应的chromedriver

### 安装Python依赖
- 建议使用pipenv或virtualenvwrapper之类的虚拟环境管理工具创建一个干净的Python3环境

- 安装依赖：
  ```
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  ```

### 根据实际情况修改config.yml
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

### 开始爬取
```python
python main.py
```

### 爬取结果预览
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