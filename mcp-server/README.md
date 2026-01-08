# FinLab MCP Server

MCP (Model Context Protocol) server for FinLab quantitative trading package, specifically designed for Taiwan stock market (台股) analysis.

## Features

### Tools (工具)
- **get_stock_data**: 獲取台股市場數據（價格、財報、月營收、本益比等）
- **backtest_strategy**: 執行回測策略，回傳績效指標
- **get_technical_indicator**: 計算技術指標（RSI, MACD, BBANDS 等）
- **check_api_token**: 檢查 FINLAB_API_TOKEN 是否已設置

### Resources (資源)
提供完整的 FinLab 文檔作為 resources：
- Data Reference: 900+ 數據欄位目錄
- Backtesting Reference: 回測 API 參考
- Factor Examples: 60+ 策略範例
- DataFrame Reference: FinLabDataFrame 方法
- Best Practices: 最佳實踐指南
- Machine Learning Reference: 機器學習參考

## Prerequisites

1. **uv**: Fast Python package installer (推薦)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **FinLab API Token**: 從 https://ai.finlab.tw/api_token/ 取得
3. **Python 3.10+** (uv 會自動管理)

## Installation

### 1. 安裝依賴

**使用 uv (推薦)**:
```bash
cd mcp-server
uv sync
```

**或使用傳統 pip**:
```bash
cd mcp-server
pip install -e .
```

### 2. 設置環境變數

```bash
# 取得你的 API token
# 前往: https://ai.finlab.tw/api_token/

# 設置環境變數（臨時）
export FINLAB_API_TOKEN="your_token_here"

# 永久設置（加入 shell 配置）
echo 'export FINLAB_API_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. 配置 MCP Client

在你的 MCP client 配置文件中添加：

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

**使用 uv (推薦)**:
```json
{
  "mcpServers": {
    "finlab": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/finlab-claude-plugin/mcp-server",
        "python",
        "-m",
        "finlab_mcp.server"
      ],
      "env": {
        "FINLAB_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**或使用傳統 Python**:
```json
{
  "mcpServers": {
    "finlab": {
      "command": "python3",
      "args": ["-m", "finlab_mcp.server"],
      "env": {
        "FINLAB_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Cursor** (`.cursor/mcp.json` 在專案根目錄):

**使用 uv (推薦)**:
```json
{
  "mcpServers": {
    "finlab": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/finlab-claude-plugin/mcp-server",
        "python",
        "-m",
        "finlab_mcp.server"
      ],
      "env": {
        "FINLAB_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**或使用傳統 Python**:
```json
{
  "mcpServers": {
    "finlab": {
      "command": "python3",
      "args": ["-m", "finlab_mcp.server"],
      "cwd": "/absolute/path/to/mcp-server",
      "env": {
        "FINLAB_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**或使用絕對路徑**:

```json
{
  "mcpServers": {
    "finlab": {
      "command": "/usr/local/bin/python3",
      "args": [
        "/absolute/path/to/finlab-claude-plugin/mcp-server/finlab_mcp/server.py"
      ],
      "env": {
        "FINLAB_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 4. 重新啟動你的 MCP Client

- **Claude Desktop**: 完全退出並重新開啟
- **Cursor**: 重新載入視窗 (Cmd+Shift+P → "Reload Window")

## Usage Examples

### 1. 檢查 API Token

```
請使用 check_api_token 工具檢查我的 FinLab API token 是否已設置
```

### 2. 獲取股票數據

```
請使用 get_stock_data 工具獲取台積電 (2330) 過去一年的收盤價
參數: table="price", column="收盤價", stock_ids=["2330"]
```

### 3. 計算技術指標

```
請計算大盤的 RSI(14) 指標
使用 get_technical_indicator 工具，indicator_name="RSI", params={"timeperiod": 14}
```

### 4. 回測策略

```
請幫我回測這個策略（提供 position DataFrame）
使用 backtest_strategy 工具，設置 resample="M", stop_loss=0.08
```

### 5. 閱讀文檔

```
請讀取 FinLab 的數據目錄文檔
資源: finlab://docs/data-reference.md
```

## Tool Schemas

### get_stock_data

```json
{
  "table": "price",
  "column": "收盤價",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "stock_ids": ["2330", "2317"]
}
```

### backtest_strategy

```json
{
  "position_data": "{...}",  // Position DataFrame JSON (orient='split')
  "resample": "M",
  "stop_loss": 0.08,
  "take_profit": 0.15,
  "fee_ratio": 0.001425,
  "tax_ratio": 0.003
}
```

### get_technical_indicator

```json
{
  "indicator_name": "RSI",
  "params": {
    "timeperiod": 14
  }
}
```

## Development

### Run Server Directly

```bash
cd mcp-server
python -m finlab_mcp.server
```

### Run Tests

```bash
cd mcp-server
pytest tests/
```

## Troubleshooting

### MCP Server 無法啟動

1. 確認 Python 路徑正確：`which python3`
2. 確認已安裝 mcp 和 finlab：`pip list | grep -E "(mcp|finlab)"`
3. 確認 FINLAB_API_TOKEN 已設置：`echo $FINLAB_API_TOKEN`

### "FinLab 套件未安裝" 錯誤

```bash
pip install finlab
```

### API Token 錯誤

1. 檢查 token 是否正確設置
2. 前往 https://ai.finlab.tw/api_token/ 確認 token 有效
3. 確認 token 已加入 MCP client 配置的 env 區塊

## Resources

- FinLab 官網: https://ai.finlab.tw/
- API Token: https://ai.finlab.tw/api_token/
- MCP Protocol: https://modelcontextprotocol.io/
- GitHub: https://github.com/koreal6803/finlab-claude-plugin

## License

MIT

## Author

FinLab Community
