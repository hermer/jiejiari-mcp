# 1. 基础镜像：使用Python 3.10+（FastMCP要求）
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统依赖（避免requests等库因缺少依赖报错）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 复制主程序代码
COPY mcp_holiday.py .

# 6. 暴露服务端口
EXPOSE 18061

# 7. 启动命令（指定SSE传输，确保与客户端适配）
CMD ["python", "mcp_holiday.py"]