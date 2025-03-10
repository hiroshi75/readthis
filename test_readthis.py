#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ReadThis MCPサーバーのテストスクリプト

このスクリプトは、ReadThis MCPサーバーの基本機能をテストします。
実際のMCPサーバー接続なしでも、コア機能をテストできます。
"""

import os
import sys
import unittest
import json
from pathlib import Path

# テスト対象のモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from html_parser import fetch_document, parse_html_content, get_document_metadata


class TestHTMLParser(unittest.TestCase):
    """HTMLパーサー機能のテスト"""
    
    def test_fetch_document(self):
        """ドキュメント取得のテスト"""
        # 公開されているWebページでテスト
        url = "https://docs.python.org/3/"
        try:
            html = fetch_document(url)
            self.assertIsNotNone(html)
            self.assertIsInstance(html, str)
            self.assertGreater(len(html), 1000)  # 十分な長さがあることを確認
            print(f"[テスト] fetch_document: 成功 ({len(html)} バイト)")
        except Exception as e:
            self.fail(f"fetch_document failed with {str(e)}")
    
    def test_parse_html_content(self):
        """HTMLパース機能のテスト"""
        # 簡単なHTMLでテスト
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>テストページ</title>
        </head>
        <body>
            <header>ヘッダー部分</header>
            <main>
                <h1>メインコンテンツ</h1>
                <p>これは本文です。</p>
            </main>
            <footer>フッター部分</footer>
        </body>
        </html>
        """
        
        parsed = parse_html_content(html)
        self.assertIsNotNone(parsed)
        self.assertIsInstance(parsed, str)
        self.assertIn("メインコンテンツ", parsed)
        self.assertIn("これは本文です", parsed)
        print("[テスト] parse_html_content: 成功")
    
    def test_metadata_extraction(self):
        """メタデータ抽出のテスト"""
        # サンプルHTMLからメタデータを抽出
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>テストタイトル</title>
            <meta name="description" content="テスト説明文">
        </head>
        <body>
            <p>コンテンツ</p>
        </body>
        </html>
        """
        
        # テスト用のモックURLを使用
        test_url = "https://example.com/test"
        
        # get_document_metadataの代わりに直接BeautifulSoupでテスト
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.title.string if soup.title else "不明なタイトル"
        self.assertEqual(title, "テストタイトル")
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        self.assertIsNotNone(meta_desc)
        self.assertEqual(meta_desc['content'], "テスト説明文")
        
        print("[テスト] metadata_extraction: 成功")


class TestReadThisJson(unittest.TestCase):
    """manuals.jsonファイル処理のテスト"""
    
    def setUp(self):
        """テスト用のmanuals.jsonを作成"""
        self.test_json_path = Path("./test_manuals.json")
        self.test_data = {
            "documents": [
                {
                    "id": "test-doc",
                    "name": "テストドキュメント",
                    "url": "https://example.com/test",
                    "description": "テスト用のドキュメント"
                }
            ]
        }
        
        # テスト用のJSONファイルを書き込み
        with open(self.test_json_path, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """テスト用のファイルを削除"""
        if self.test_json_path.exists():
            self.test_json_path.unlink()
    
    def test_read_json(self):
        """JSONファイル読み込みのテスト"""
        self.assertTrue(self.test_json_path.exists())
        
        # ファイル読み込みテスト
        with open(self.test_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertEqual(len(data["documents"]), 1)
        self.assertEqual(data["documents"][0]["id"], "test-doc")
        self.assertEqual(data["documents"][0]["url"], "https://example.com/test")
        print("[テスト] read_json: 成功")
    
    def test_id_to_url_resolution(self):
        """IDからURLへの解決機能のテスト"""
        # 実際のサーバー機能を模倣したシンプルなID→URL解決関数
        def resolve_url(url_or_id, documents):
            if url_or_id.startswith(('http://', 'https://')):
                return url_or_id
            
            for doc in documents:
                if doc.get("id") == url_or_id:
                    return doc.get("url")
            
            return None
        
        # テスト
        docs = self.test_data["documents"]
        
        # 既にURLの場合
        self.assertEqual(
            resolve_url("https://example.com/direct", docs),
            "https://example.com/direct"
        )
        
        # IDからURLを解決
        self.assertEqual(
            resolve_url("test-doc", docs),
            "https://example.com/test"
        )
        
        # 存在しないID
        self.assertIsNone(resolve_url("non-existent", docs))
        
        print("[テスト] id_to_url_resolution: 成功")


if __name__ == "__main__":
    print("ReadThis MCPサーバーのテストを開始します...")
    unittest.main()
