#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ReadThis MCPサーバーのモックテスト

このスクリプトは、MCPサーバーとの連携をモックでシミュレートし、
readthisツールの動作を確認します。
"""

import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# テスト対象のモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# html_parserのimport
from html_parser import fetch_document, parse_html_content, DocumentFetchError

# サーバークラスのモック作成用
class MockServer:
    def __init__(self):
        self.tool_handlers = {}
    
    def tool(self, name):
        def decorator(func):
            self.tool_handlers[name] = func
            return func
        return decorator

# テスト用のmcpモジュールをモック
class MockMcp:
    @staticmethod
    async def use_tool(server_name, tool_name, args):
        if server_name != "readthis-server" or tool_name != "readthis":
            raise ValueError(f"Unknown tool: {server_name}.{tool_name}")
        
        url = args.get("url")
        if not url:
            raise ValueError("URL is required")
        
        # 実際のfetch_documentとparse_html_contentを呼び出す代わりにモックレスポンスを返す
        if url.startswith(("http://", "https://")):
            return f"Mock content for {url}"
        else:
            # IDからURLを解決する場合
            mock_docs = {
                "python-asyncio": "https://docs.python.org/3/library/asyncio.html",
                "react-hooks": "https://react.dev/reference/react"
            }
            resolved_url = mock_docs.get(url)
            if not resolved_url:
                raise ValueError(f"Unknown document ID: {url}")
            return f"Mock content for resolved URL: {resolved_url}"


class TestReadThisMockMcp(unittest.TestCase):
    """ReadThis MCPサーバーのモックテスト"""
    
    def setUp(self):
        """テスト環境のセットアップ"""
        # サーバーのモックを作成
        self.mock_server = MockServer()
        
        # 実際のサーバーコードを部分的に再現
        def resolve_url(url_or_id):
            # 既にURLの場合はそのまま返す
            if url_or_id.startswith(('http://', 'https://')):
                return url_or_id
            
            # IDからURLを解決
            mock_docs = {
                "python-asyncio": "https://docs.python.org/3/library/asyncio.html",
                "react-hooks": "https://react.dev/reference/react"
            }
            
            resolved_url = mock_docs.get(url_or_id)
            if not resolved_url:
                raise ValueError(f"無効なドキュメントID: {url_or_id}")
            
            return resolved_url
        
        # readthisツール関数の定義
        @self.mock_server.tool("readthis")
        async def readthis(url):
            try:
                print(f"[Mock] ドキュメント取得リクエスト: {url}")
                
                # URLの解決
                resolved_url = resolve_url(url)
                print(f"[Mock] 解決されたURL: {resolved_url}")
                
                # 実際のHTTP取得と解析はスキップし、モックレスポンスを返す
                return f"Mock content for {resolved_url}"
                
            except ValueError as e:
                print(f"[Mock Error] 無効なURL/ID: {str(e)}")
                raise ValueError(str(e))
            except Exception as e:
                print(f"[Mock Error] 予期しないエラー: {str(e)}")
                raise Exception(str(e))
    
    @patch('sys.stdout')  # 標準出力をキャプチャするためのパッチ
    def test_readthis_with_url(self, mock_stdout):
        """URLを使用したreadthisツールのテスト"""
        import asyncio
        
        # テスト用URL
        test_url = "https://example.com/test"
        
        # readthisツール関数を非同期で実行
        result = asyncio.run(self.mock_server.tool_handlers["readthis"](test_url))
        
        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn("Mock content for", result)
        self.assertIn(test_url, result)
        print(f"[テスト] readthis_with_url: 成功")
    
    @patch('sys.stdout')
    def test_readthis_with_id(self, mock_stdout):
        """ドキュメントIDを使用したreadthisツールのテスト"""
        import asyncio
        
        # テスト用ID
        test_id = "python-asyncio"
        expected_url = "https://docs.python.org/3/library/asyncio.html"
        
        # readthisツール関数を非同期で実行
        result = asyncio.run(self.mock_server.tool_handlers["readthis"](test_id))
        
        # 結果の検証
        self.assertIsNotNone(result)
        self.assertIn("Mock content for", result)
        self.assertIn(expected_url, result)
        print(f"[テスト] readthis_with_id: 成功")
    
    @patch('sys.stdout')
    def test_readthis_with_invalid_id(self, mock_stdout):
        """無効なIDを使用したreadthisツールのテスト"""
        import asyncio
        
        # 無効なID
        invalid_id = "non-existent-id"
        
        # 例外が発生することを確認
        with self.assertRaises(ValueError):
            asyncio.run(self.mock_server.tool_handlers["readthis"](invalid_id))
        
        print(f"[テスト] readthis_with_invalid_id: 成功")
    
    def test_mock_mcp_use_tool(self):
        """MockMcpクラスを使用したuse_toolのテスト"""
        import asyncio
        
        # モックMCPインスタンス
        mock_mcp = MockMcp()
        
        # URLでテスト
        result1 = asyncio.run(mock_mcp.use_tool("readthis-server", "readthis", {"url": "https://example.com/test"}))
        self.assertIn("Mock content for", result1)
        
        # IDでテスト
        result2 = asyncio.run(mock_mcp.use_tool("readthis-server", "readthis", {"url": "python-asyncio"}))
        self.assertIn("Mock content for resolved URL", result2)
        self.assertIn("asyncio", result2)
        
        # 無効なIDでテスト
        with self.assertRaises(ValueError):
            asyncio.run(mock_mcp.use_tool("readthis-server", "readthis", {"url": "non-existent-id"}))
        
        print(f"[テスト] mock_mcp_use_tool: 成功")


if __name__ == "__main__":
    print("ReadThis MCPサーバーのモックテストを開始します...")
    unittest.main()
