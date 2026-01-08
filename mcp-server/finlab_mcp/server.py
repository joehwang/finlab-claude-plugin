#!/usr/bin/env python3
"""
FinLab MCP Server

MCP server providing tools and resources for FinLab quantitative trading package.
Designed for Taiwan stock market (台股) analysis.
"""

import asyncio
import json
import logging
import os
from typing import Any, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from mcp.server.stdio import stdio_server

# Initialize FinLab (will use FINLAB_API_TOKEN from environment)
try:
    from finlab import data
    from finlab.backtest import sim
    import pandas as pd
    FINLAB_AVAILABLE = True
except ImportError:
    FINLAB_AVAILABLE = False
    print("Warning: FinLab not installed. Some features will be unavailable.")

# Get the path to documentation
DOCS_PATH = Path(__file__).parent.parent.parent / "finlab-plugin" / "skills" / "finlab"

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("finlab-mcp-server")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List all available FinLab documentation resources."""
    resources = []
    
    if DOCS_PATH.exists():
        doc_files = [
            ("data-reference.md", "FinLab Data Catalog - Complete reference of 900+ data columns"),
            ("backtesting-reference.md", "Backtesting API Reference - sim() function parameters"),
            ("dataframe-reference.md", "FinLabDataFrame Methods - All DataFrame operations"),
            ("factor-examples.md", "Factor Examples - 60+ complete strategy examples"),
            ("factor-analysis-reference.md", "Factor Analysis Tools - IC, Shapley, centrality"),
            ("best-practices.md", "Best Practices - Coding patterns and anti-patterns"),
            ("machine-learning-reference.md", "Machine Learning Reference - Feature engineering"),
            ("SKILL.md", "Quick Start Guide - Overview and workflow"),
        ]
        
        for filename, description in doc_files:
            file_path = DOCS_PATH / filename
            if file_path.exists():
                resources.append(
                    Resource(
                        uri=f"finlab://docs/{filename}",
                        name=f"FinLab: {filename.replace('.md', '').replace('-', ' ').title()}",
                        mimeType="text/markdown",
                        description=description,
                    )
                )
    
    return resources


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a FinLab documentation resource."""
    # Convert URI to string if it's not already (handles AnyUrl objects)
    uri_str = str(uri)
    logger.debug(f"read_resource called with URI: {uri_str} (type: {type(uri)})")
    
    if not uri_str.startswith("finlab://docs/"):
        logger.error(f"Invalid URI scheme: {uri_str}")
        raise ValueError(f"Unknown resource URI: {uri_str}")

    filename = uri_str.replace("finlab://docs/", "")
    logger.debug(f"Extracted filename: {filename}")

    # 禁止任何路徑操作
    if ".." in filename or "/" in filename or "\\" in filename:
        logger.warning(f"Path traversal attempt detected: {filename}")
        raise ValueError(f"Invalid filename: {filename}")

    # 使用絕對路徑確保安全
    docs_path_absolute = DOCS_PATH.resolve()
    
    logger.debug(f"DOCS_PATH: {DOCS_PATH}")
    logger.debug(f"DOCS_PATH exists: {DOCS_PATH.exists()}")
    logger.debug(f"DOCS_PATH resolved: {docs_path_absolute}")
    
    # 先檢查 DOCS_PATH 是否存在
    if not DOCS_PATH.exists():
        logger.error(f"DOCS_PATH does not exist: {DOCS_PATH}")
        raise FileNotFoundError(
            f"Documentation directory not found: {DOCS_PATH}\n"
            f"Requested file: {filename}"
        )
    
    # 檢查檔案是否存在（先嘗試直接匹配）
    file_path = DOCS_PATH / filename
    logger.debug(f"Requested file path: {file_path}")
    logger.debug(f"File path exists: {file_path.exists()}")
    
    # 如果檔案不存在，嘗試大小寫不敏感匹配
    if not file_path.exists():
        logger.warning(f"File not found (exact match): {file_path}")
        available_files = [f.name for f in DOCS_PATH.iterdir() if f.is_file()]
        logger.debug(f"Available files in DOCS_PATH: {available_files}")
        
        # 嘗試大小寫不敏感匹配
        matching_files = [f for f in available_files if f.lower() == filename.lower()]
        if matching_files:
            logger.info(f"Found case-insensitive match: {matching_files[0]} for {filename}")
            file_path = DOCS_PATH / matching_files[0]
        else:
            logger.error(f"No matching file found. Requested: {filename}, Available: {available_files}")
            raise FileNotFoundError(
                f"Documentation file not found: {filename}\n"
                f"Available files: {', '.join(available_files)}"
            )
    
    # 解析為絕對路徑並確保在允許的目錄內
    file_path_resolved = file_path.resolve()
    logger.debug(f"Resolved file path: {file_path_resolved}")
    
    if not str(file_path_resolved).startswith(str(docs_path_absolute)):
        logger.error(f"Access denied - file outside allowed directory: {filename}")
        logger.error(f"File path: {file_path_resolved}")
        logger.error(f"Allowed path: {docs_path_absolute}")
        raise ValueError(f"Access denied: {filename}")

    if not file_path_resolved.is_file():
        logger.error(f"Path exists but is not a file: {file_path_resolved}")
        raise ValueError(f"Invalid resource: {filename} is not a file")
    
    # 使用解析後的路徑
    file_path = file_path_resolved

    logger.info(f"Reading file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    logger.debug(f"Successfully read {len(content)} characters from {filename}")
    return content


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available FinLab tools."""
    tools = [
        Tool(
            name="get_stock_data",
            description="""獲取台股市場數據。支援價格、財報、月營收、本益比等各類數據。
            
使用範例：
- table="price", column="收盤價" : 獲取收盤價
- table="monthly_revenue", column="當月營收" : 獲取月營收
- table="price_earning_ratio", column="本益比" : 獲取本益比
- table="fundamental_features", column="ROE稅後" : 獲取 ROE

參數：
- table: 數據表名稱
- column: 欄位名稱
- start_date: 起始日期 (可選，格式: YYYY-MM-DD)
- end_date: 結束日期 (可選，格式: YYYY-MM-DD)
- stock_ids: 股票代碼列表 (可選，如 ["2330", "2317"])
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "數據表名稱，如 price, monthly_revenue, fundamental_features 等",
                    },
                    "column": {
                        "type": "string",
                        "description": "欄位名稱，如 收盤價, 當月營收, ROE稅後 等",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "起始日期 (可選，格式: YYYY-MM-DD)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "結束日期 (可選，格式: YYYY-MM-DD)",
                    },
                    "stock_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "股票代碼列表 (可選)",
                    },
                },
                "required": ["table", "column"],
            },
        ),
        Tool(
            name="backtest_strategy",
            description="""執行回測策略。接收 position DataFrame 並回傳回測結果。
            
參數：
- position_data: Position DataFrame (JSON 格式，index 是日期，columns 是股票代碼)
- resample: 再平衡頻率 ("D"=每日, "W"=每週, "M"=每月)
- stop_loss: 停損比例 (如 0.08 代表 8%)
- take_profit:停利比例 (如 0.15 代表 15%)
- fee_ratio: 手續費率 (預設 0.001425/3)
- tax_ratio: 交易稅率 (預設 0.003)

回傳包含年化報酬率、夏普比率、最大回撤等績效指標。
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "position_data": {
                        "type": "string",
                        "description": "Position DataFrame 的 JSON 字串 (orient='split' 格式)",
                    },
                    "resample": {
                        "type": "string",
                        "description": "再平衡頻率: D (每日), W (每週), M (每月)",
                        "enum": ["D", "W", "M"],
                        "default": "M",
                    },
                    "stop_loss": {
                        "type": "number",
                        "description": "停損比例 (0-1)",
                    },
                    "take_profit": {
                        "type": "number",
                        "description": "停利比例 (0-1)",
                    },
                    "fee_ratio": {
                        "type": "number",
                        "description": "手續費率",
                    },
                    "tax_ratio": {
                        "type": "number",
                        "description": "交易稅率",
                    },
                },
                "required": ["position_data"],
            },
        ),
        Tool(
            name="get_technical_indicator",
            description="""計算技術指標。支援 TA-Lib 的所有指標。
            
常用指標：
- RSI: 相對強弱指標
- MACD: 平滑異同移動平均線
- BBANDS: 布林帶
- SMA: 簡單移動平均
- EMA: 指數移動平均

參數：
- indicator_name: 指標名稱 (如 RSI, MACD, BBANDS)
- params: 指標參數 (JSON 格式，如 {"timeperiod": 14})
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "indicator_name": {
                        "type": "string",
                        "description": "技術指標名稱 (如 RSI, MACD, BBANDS)",
                    },
                    "params": {
                        "type": "object",
                        "description": "指標參數 (如 timeperiod, fastperiod 等)",
                    },
                },
                "required": ["indicator_name"],
            },
        ),
        Tool(
            name="check_api_token",
            description="""檢查 FINLAB_API_TOKEN 是否已設置。
            
如果未設置，會提示用戶如何獲取和設置 token。
Token 可從 https://ai.finlab.tw/api_token/ 取得。
""",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]
    
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls."""
    
    if not FINLAB_AVAILABLE and name != "check_api_token":
        return [
            TextContent(
                type="text",
                text="錯誤：FinLab 套件未安裝。請執行: pip install finlab",
            )
        ]
    
    try:
        if name == "check_api_token":
            token = os.getenv("FINLAB_API_TOKEN")
            if token:
                return [
                    TextContent(
                        type="text",
                        text=f"✅ FINLAB_API_TOKEN 已設置 (長度: {len(token)} 字元)",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text="""❌ FINLAB_API_TOKEN 未設置

請按照以下步驟設置：

1. 前往 https://ai.finlab.tw/api_token/ 取得您的 API token
2. 設置環境變數：
   
   # 臨時設置（當前終端）
   export FINLAB_API_TOKEN="your_token_here"
   
   # 永久設置（加入 shell 配置）
   echo 'export FINLAB_API_TOKEN="your_token_here"' >> ~/.zshrc
   source ~/.zshrc

3. 重新啟動 MCP 服務器
""",
                    )
                ]
        
        elif name == "get_stock_data":
            table = arguments["table"]
            column = arguments["column"]
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            stock_ids = arguments.get("stock_ids")
            
            # Get data
            df = data.get(f"{table}:{column}")
            
            # Filter by date range if provided
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            
            # Filter by stock IDs if provided
            if stock_ids:
                df = df[stock_ids]
            
            # Convert to JSON
            result = {
                "shape": df.shape,
                "columns": list(df.columns[:10]),  # First 10 stocks
                "index_sample": [str(x) for x in df.index[:5].tolist()],  # First 5 dates
                "data_sample": df.head(10).to_dict(),
                "summary": {
                    "total_stocks": len(df.columns),
                    "total_dates": len(df.index),
                    "date_range": f"{df.index[0]} to {df.index[-1]}",
                }
            }
            
            return [
                TextContent(
                    type="text",
                    text=f"成功獲取數據: {table}:{column}\n\n"
                         f"📊 資料摘要：\n"
                         f"- 股票數量: {result['summary']['total_stocks']}\n"
                         f"- 日期數量: {result['summary']['total_dates']}\n"
                         f"- 日期範圍: {result['summary']['date_range']}\n\n"
                         f"前 10 筆資料樣本：\n{json.dumps(result['data_sample'], indent=2, ensure_ascii=False)}",
                )
            ]
        
        elif name == "get_technical_indicator":
            indicator_name = arguments["indicator_name"]
            params = arguments.get("params", {})
            
            # Calculate indicator
            result = data.indicator(indicator_name, **params)
            
            # Handle multiple return values (like MACD)
            if isinstance(result, tuple):
                response = f"計算技術指標: {indicator_name}\n\n"
                response += f"回傳 {len(result)} 個數值\n\n"
                for i, r in enumerate(result):
                    response += f"數值 {i+1} 形狀: {r.shape}\n"
                    response += f"最近 5 筆資料:\n{r.tail()}\n\n"
            else:
                response = f"計算技術指標: {indicator_name}\n\n"
                response += f"資料形狀: {result.shape}\n"
                response += f"最近 5 筆資料:\n{result.tail()}"
            
            return [TextContent(type="text", text=response)]
        
        elif name == "backtest_strategy":
            position_json = arguments["position_data"]
            resample = arguments.get("resample", "M")
            stop_loss = arguments.get("stop_loss")
            take_profit = arguments.get("take_profit")
            fee_ratio = arguments.get("fee_ratio")
            tax_ratio = arguments.get("tax_ratio")
            
            # Parse position DataFrame
            position = pd.read_json(position_json, orient="split")
            
            # Build sim parameters
            sim_params = {
                "position": position,
                "resample": resample,
                "upload": False,
            }
            
            if stop_loss is not None:
                sim_params["stop_loss"] = stop_loss
            if take_profit is not None:
                sim_params["take_profit"] = take_profit
            if fee_ratio is not None:
                sim_params["fee_ratio"] = fee_ratio
            if tax_ratio is not None:
                sim_params["tax_ratio"] = tax_ratio
            
            # Run backtest
            report = sim(**sim_params)
            
            # Extract metrics
            stats = report.get_stats()
            
            result = f"""📈 回測結果

績效指標：
- 年化報酬率 (CAGR): {stats.get('cagr', 0):.2%}
- 夏普比率 (Sharpe): {stats.get('monthly_sharpe', 0):.2f}
- 最大回撤 (MDD): {stats.get('max_drawdown', 0):.2%}
- 勝率: {stats.get('win_rate', 0):.2%}
- 總交易次數: {stats.get('n_trades', 0)}

風險指標：
- 年化波動率: {stats.get('annual_volatility', 0):.2%}
- 期末總資產: {stats.get('final_value', 0):,.0f}

完整統計資料：
{json.dumps(stats, indent=2, ensure_ascii=False, default=str)}
"""
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"未知的工具: {name}")]
    
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"執行工具時發生錯誤: {str(e)}\n\n詳細錯誤:\n{type(e).__name__}: {e}",
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
