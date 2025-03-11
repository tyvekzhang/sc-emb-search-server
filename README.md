# Sc-emb-search-server
跨物种单细胞 Embedding 检索库，提供基于 Embedding 的快速相似性检索功能，支持跨物种细胞的高效比对。内置丰富的 Metadata 数据，可便捷下载，助力单细胞研究。

## 快速开始

1. 环境准备(以Linux为例)
   - 下载项目到自定义路径, 并进入到sc-emb-search-server
   - 安装[uv](https://github.com/astral-sh/uv)包和项目管理器, 下载依赖
     - uv python install 3.9
     - uv venv --python 3.9
     - source .venv/bin/activate
     - uv sync

2. 启动(cd src/main)

   - 前台启动, 可通过Ctrl + C随时关闭
     - python apiserver.py

   - 后台启动
     - nohup python apiserver.py > server.log 2>&1 &

3. API文档
   - 在浏览器访问: 服务器ip:19007/docs

## 常见问题及解决方案

1. RuntimeError: Unsupported compiler -- at least C++11 support is needed!
   - 请参考教程升级c++

2. 下载依赖非常慢
   - 请为设置国内的镜像源
