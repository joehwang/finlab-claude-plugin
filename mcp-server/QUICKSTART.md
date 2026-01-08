# FinLab MCP Server 快速開始指南

## 安裝步驟

### 0. 安裝 uv（如果尚未安裝）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc  # 或 source ~/.bashrc
```

### 1. 安裝套件

**使用一鍵安裝腳本**（推薦）：
```bash
cd mcp-server
./install.sh
```

**或手動安裝**：
```bash
cd mcp-server
uv sync
```

**或使用傳統 pip**：
```bash
cd mcp-server
pip3 install -e .
```

### 2. 設置 API Token

前往 https://ai.finlab.tw/api_token/ 取得你的 API token，然後：

```bash
export FINLAB_API_TOKEN="your_token_here"
```

永久保存（推薦）：

```bash
echo 'export FINLAB_API_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. 測試安裝

**使用 uv**：
```bash
uv run python test_server.py
```

**或傳統方式**：
```bash
python3 test_server.py
```

應該會看到：
```
✅ 通過 - 套件導入
✅ 通過 - API Token
✅ 通過 - FinLab 連線
✅ 通過 - Server 模組
```

### 4. 配置 MCP Client

#### Cursor

在專案根目錄創建 `.cursor/mcp.json`：

**使用 uv（推薦）**：
```json
{
  "mcpServers": {
    "finlab": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/yourusername/path/to/finlab-claude-plugin/mcp-server",
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

**或使用傳統 Python**：
```json
{
  "mcpServers": {
    "finlab": {
      "command": "python3",
      "args": ["-m", "finlab_mcp.server"],
      "cwd": "/Users/yourusername/path/to/finlab-claude-plugin/mcp-server",
      "env": {
        "FINLAB_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**重要**：將路徑改成你的實際路徑！

#### Claude Desktop

編輯 `~/Library/Application Support/Claude/claude_desktop_config.json`：

**使用 uv（推薦）**：
```json
{
  "mcpServers": {
    "finlab": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-server",
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

**或使用傳統 Python**：
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

### 5. 重新啟動 MCP Client

- **Cursor**: Cmd+Shift+P → "Reload Window"
- **Claude Desktop**: 完全退出後重新開啟

## 使用範例

### 1. 檢查連線狀態

```
請使用 check_api_token 工具檢查我的 FinLab API token 是否正常
```

### 2. 獲取股票資料

#### 獲取收盤價

```
請使用 get_stock_data 工具獲取台積電（2330）和聯發科（2454）
從 2023-01-01 到現在的收盤價

參數：
- table: "price"
- column: "收盤價"
- stock_ids: ["2330", "2454"]
- start_date: "2023-01-01"
```

#### 獲取月營收

```
請獲取台積電最近 12 個月的月營收資料

參數：
- table: "monthly_revenue"
- column: "當月營收"
- stock_ids: ["2330"]
```

#### 獲取本益比

```
請獲取半導體股票的本益比資料
從 2024-01-01 開始

參數：
- table: "price_earning_ratio"
- column: "本益比"
- start_date: "2024-01-01"
```

### 3. 計算技術指標

#### RSI 指標

```
請使用 get_technical_indicator 計算 RSI(14)

參數：
- indicator_name: "RSI"
- params: {"timeperiod": 14}
```

#### MACD 指標

```
請計算 MACD 指標

參數：
- indicator_name: "MACD"
- params: {"fastperiod": 12, "slowperiod": 26, "signalperiod": 9}
```

#### 布林帶

```
請計算 20 日布林帶

參數：
- indicator_name: "BBANDS"
- params: {"timeperiod": 20, "nbdevup": 2, "nbdevdn": 2}
```

### 4. 回測策略

首先需要準備 position DataFrame，然後：

```
請幫我回測這個策略

參數：
- position_data: "{...}"  # Position DataFrame 的 JSON
- resample: "M"
- stop_loss: 0.08
- take_profit: 0.15
```

### 5. 讀取文檔

#### 查看數據目錄

```
請讀取 finlab://docs/data-reference.md
我想了解有哪些數據可以使用
```

#### 查看策略範例

```
請讀取 finlab://docs/factor-examples.md
我想看一些策略範例
```

#### 查看最佳實踐

```
請讀取 finlab://docs/best-practices.md
```

## 完整範例：價值+動能策略

```
我想建立一個結合價值和動能的選股策略：

1. 先幫我讀取 finlab://docs/factor-examples.md 了解範例
2. 使用 get_stock_data 獲取以下數據：
   - 股價淨值比 (table: "price_earning_ratio", column: "股價淨值比")
   - 收盤價 (table: "price", column: "收盤價")
3. 然後我會給你 position DataFrame 進行回測
```

## 故障排除

### MCP Server 無法啟動

檢查終端機輸出中是否有錯誤訊息：

```bash
# 手動測試服務器
cd mcp-server
python3 -m finlab_mcp.server
```

### API Token 錯誤

```bash
# 確認 token 已設置
echo $FINLAB_API_TOKEN

# 測試 token 是否有效
python3 test_server.py
```

### 套件未安裝

```bash
# 確認安裝
pip3 list | grep -E "(mcp|finlab|pandas)"

# 重新安裝
cd mcp-server
pip3 install -e . --force-reinstall
```

### Python 路徑問題

```bash
# 確認 Python 位置
which python3

# 在 MCP 配置中使用完整路徑
# 例如："/usr/local/bin/python3" 或 "/opt/homebrew/bin/python3"
```

## 進階用法

### 自訂環境變數

在 MCP 配置的 `env` 區塊可以設置額外的環境變數：

```json
{
  "mcpServers": {
    "finlab": {
      "command": "python3",
      "args": ["-m", "finlab_mcp.server"],
      "env": {
        "FINLAB_API_TOKEN": "your_token_here",
        "PYTHONPATH": "/custom/path"
      }
    }
  }
}
```

### 使用虛擬環境

```json
{
  "mcpServers": {
    "finlab": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "finlab_mcp.server"],
      "env": {
        "FINLAB_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

## 更多資源

- **完整文檔**: [README.md](README.md)
- **FinLab 官網**: https://ai.finlab.tw/
- **API Token**: https://ai.finlab.tw/api_token/
- **MCP Protocol**: https://modelcontextprotocol.io/

## 支援

遇到問題？請在 GitHub Issues 回報：
https://github.com/koreal6803/finlab-claude-plugin/issues
