# Sc-emb-search-server部署文档

本文档提供了两种部署方式：源码部署和 Docker 部署。

---

## 1. 源码部署

### 1.1 环境准备

在开始部署之前，请确保您的系统已经安装了以下软件：

- **[uv](https://github.com/astral-sh/uv)**（高性能的 Python 包管理工具）
- Git

### 1.2 克隆代码库

将代码库克隆到本地：

```bash
git clone <repository-url>/sc-emb-search-server.git
cd sc-emb-search-server
```

### 1.3 创建虚拟环境

使用 `uv` 创建虚拟环境并激活：

```bash
uv venv --python 3.9
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 1.4 安装依赖

使用 `uv` 安装项目所需的依赖：

```bash
uv sync
```

### 1.5 配置项目

根据项目配置文件（如 `config.yaml`），设置以下关键配置：

#### 服务器配置
- **host**: `0.0.0.0`
- **port**: `19007`
- **workers**: `1`
- **home_dir**: `/data/Container/Repository`
- **model_dir**: `/data/Container/Repository/model_v1.1`

#### 数据库配置
- **dialect**: `pgsql`
- 根据实际情况, 设置自己数据库的链接信息：
  - PostgreSQL: `postgresql+asyncpg://root:My_dev-123@172.21.14.53:5432/sc-emb-search`

### 1.6 启动应用

#### 前台启动

进入 `src/main` 目录，使用以下命令启动应用：

```bash
cd src/main
python apiserver.py
```

应用将在 `http://localhost:19007` 上运行，可通过 `Ctrl + C` 随时关闭。

#### 后台启动

如果需要后台运行，可以使用以下命令：

```bash
nohup python apiserver.py > server.log 2>&1 &
```

日志将输出到 `server.log` 文件中。

### 1.7 访问 API 文档

在浏览器中访问以下地址，查看 API 文档：

```
http://服务器IP:19007/docs
```

---

## 2. Docker 部署

### 2.1 环境准备

在开始 Docker 部署之前，请确保您的系统已经安装了以下软件：

- **Docker**
- **Docker Compose**

### 2.2 创建 Dockerfile

在项目根目录下创建一个名为 `Dockerfile` 的文件，内容如下：

```Dockerfile
# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
RUN uv venv --python 3.9 && \
    . .venv/bin/activate && \
    uv sync

# 暴露端口
EXPOSE 19007

# 启动应用
CMD [".venv/bin/python", "src/main/apiserver.py"]
```

### 2.3 创建 docker-compose.yml 文件

在项目根目录下创建一个名为 `docker-compose.yml` 的文件，内容如下：

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "19007:19007"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./sc-emb-search.db
      - JWT_SECRET_KEY=your-secret-key
    volumes:
      - .:/app
    restart: always
```

### 2.4 构建 Docker 镜像

使用以下命令构建 Docker 镜像：

```bash
docker-compose build
```

### 2.5 启动 Docker 容器

使用以下命令启动 Docker 容器：

```bash
docker-compose up -d
```

### 2.6 访问应用

应用将在 `http://localhost:19007` 上运行。

---

## 3. 其他说明

- 如果需要修改端口号，可以在 `docker-compose.yml` 文件中修改 `ports` 配置。
- 如果需要使用其他数据库（如 MySQL 或 PostgreSQL），请修改 `DATABASE_URL` 环境变量并确保数据库服务已正确配置。

---

## 4. 常见问题及解决方案

### 4.1 编译错误：`RuntimeError: Unsupported compiler -- at least C++11 support is needed!`

- **解决方案**：请升级您的 C++ 编译器以支持 C++11 或更高版本。可以参考以下命令：
  ```bash
  sudo apt update
  sudo apt install build-essential
  ```

### 4.2 下载依赖非常慢

- **解决方案**：为 `uv` 设置国内镜像源。例如：
  ```bash
  uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  ```