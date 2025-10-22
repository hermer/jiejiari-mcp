from fastmcp import FastMCP
import requests
from datetime import datetime, timedelta
from typing import List, Annotated
from pydantic import Field

# 1. 初始化FastMCP应用（指定HTTP SSE传输，适配客户端需求）
mcp = FastMCP(
    name="MCP",
    instructions="我的N8N工具集",
)

def get_date_list(start_date: str, end_date: str) -> List[str]:
    date_list = []
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("日期格式错误，请使用YYYY-MM-DD（如2025-10-22）")
    
    if start > end:
        raise ValueError("开始日期不能晚于结束日期")
    
    current = start
    while current <= end:
        date_list.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return date_list

@mcp.tool(
    name="workday_list",
    description="根据开始日期和结束日期，查询该范围内的工作日列表"
)
def workday_list(start_date: Annotated[str, Field(description="开始日期，格式YYYY-MM-DD")], end_date: Annotated[str, Field(description="结束日期，格式YYYY-MM-DD")]) -> dict:
    try:
        # 生成日期列表
        date_list = get_date_list(start_date, end_date)
        if not date_list:
            return {"message": "无有效日期范围", "workday_list": []}
        
        # 构建批量查询接口参数（d=日期1&d=日期2...）
        params = {
            "d": date_list,
            "type": "Y"
        }
        # 调用节假日接口
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }
        response = requests.get("https://timor.tech/api/holiday/batch", params=params, timeout=100, headers=headers)
        response.raise_for_status()  # 捕获HTTP请求错误（如404、500）
        api_data = response.json()
        
        # 处理接口返回，统计工作日（type=0）
        if api_data.get("code") != 0:
            return {"message": f"接口返回错误：{api_data.get('message', '未知错误')}", "workday_list": []}
        
        type_data = api_data.get("type", {})
        workday_list = []
        date_details = {}
        for date in date_list:
            date_info = type_data.get(date, {})
            date_type = date_info.get("type", -1)  # -1表示未获取到类型
            if date_type == 0:
                workday_list.append(date)
        
        # 返回结果（包含统计数和明细）
        return {
            "message": f"查询成功，一共{len(workday_list)}天工作日",
            "workday_list": workday_list
        }
    
    except requests.exceptions.RequestException as e:
        return {"message": f"接口调用失败：{str(e)}", "workday_list": []}
    except ValueError as e:
        return {"message": f"参数错误：{str(e)}", "workday_list": []}
    except Exception as e:
        return {"message": f"系统内部错误：{str(e)}", "workday_list": []}

if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="0.0.0.0", 
        port=18061      
    )