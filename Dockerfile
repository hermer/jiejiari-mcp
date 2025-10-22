FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制主程序代码
COPY mcp_holiday.py .

# 6. 暴露服务端口
EXPOSE 18061

# 7. 启动命令
CMD ["python", "mcp_holiday.py"]