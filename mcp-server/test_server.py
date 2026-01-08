#!/usr/bin/env python3
"""
測試 FinLab MCP Server 是否正常運作

執行方式：
    uv run python test_server.py
    # 或傳統方式
    python test_server.py
"""

import os
import sys


def test_imports():
    """測試必要的套件是否已安裝"""
    print("📦 測試套件導入...")
    
    try:
        import mcp
        print("  ✓ mcp")
    except ImportError:
        print("  ✗ mcp - 請執行: pip install mcp")
        return False
    
    try:
        import finlab
        print("  ✓ finlab")
    except ImportError:
        print("  ✗ finlab - 請執行: pip install finlab")
        return False
    
    try:
        import pandas
        print("  ✓ pandas")
    except ImportError:
        print("  ✗ pandas - 請執行: pip install pandas")
        return False
    
    return True


def test_api_token():
    """測試 API token 是否已設置"""
    print("\n🔑 測試 API Token...")
    
    token = os.getenv("FINLAB_API_TOKEN")
    if token:
        print(f"  ✓ FINLAB_API_TOKEN 已設置 (長度: {len(token)} 字元)")
        return True
    else:
        print("  ✗ FINLAB_API_TOKEN 未設置")
        print("    請執行: export FINLAB_API_TOKEN=\"your_token_here\"")
        return False


def test_finlab_connection():
    """測試 FinLab 連線"""
    print("\n🌐 測試 FinLab 連線...")
    
    try:
        from finlab import data
        
        # 嘗試獲取少量數據
        close = data.get("price:收盤價")
        print(f"  ✓ 成功連接 FinLab API")
        print(f"    數據形狀: {close.shape}")
        print(f"    最新日期: {close.index[-1]}")
        return True
    except Exception as e:
        print(f"  ✗ 連線失敗: {e}")
        return False


def test_server_module():
    """測試服務器模組是否可以載入"""
    print("\n⚙️  測試 MCP Server 模組...")
    
    try:
        from finlab_mcp import server
        print("  ✓ 成功載入 finlab_mcp.server")
        
        # 檢查必要的函數
        if hasattr(server, 'main'):
            print("  ✓ main() 函數存在")
        if hasattr(server, 'app'):
            print("  ✓ app 物件存在")
        
        return True
    except Exception as e:
        print(f"  ✗ 載入失敗: {e}")
        return False


def main():
    """執行所有測試"""
    print("=" * 60)
    print("FinLab MCP Server 測試")
    print("=" * 60)
    
    results = []
    
    # 執行測試
    results.append(("套件導入", test_imports()))
    results.append(("API Token", test_api_token()))
    results.append(("FinLab 連線", test_finlab_connection()))
    results.append(("Server 模組", test_server_module()))
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("測試結果")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 所有測試通過！MCP Server 已準備就緒。")
        print("\n下一步：")
        print("1. 配置你的 MCP client (參考 README.md)")
        print("2. 重新啟動 MCP client")
        print("3. 開始使用 FinLab tools 和 resources")
        return 0
    else:
        print("\n⚠️  部分測試失敗，請檢查上述錯誤訊息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
