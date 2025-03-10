#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, TypeVar, Generic, Callable, cast

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolRequestParams, ErrorData
from mcp import McpError

# 独自のエラーコード定義
class ErrorCode:
    """エラーコード定義"""
    # エラーコードは整数値を使用
    InvalidRequest = 400  # 無効なリクエスト
    InvalidParams = 422   # 無効なパラメータ
    InternalError = 500   # 内部エラー

from html_parser import fetch_document, parse_html_content, DocumentFetchError

# ロギング設定
logging.basicConfig(
    level=logging.ERROR,
    format='[%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("readthis-server")


class ReadThisServer:
    """
    ReadThis MCPサーバー
    
    HTMLドキュメントを取得して解析するためのMCPサーバー
    """
    
    def __init__(self) -> None:
        """サーバーの初期化"""
        logger.error("[Setup] ReadThis MCPサーバーを初期化しています...")
        
        # Server型を調整
        self.server = Server(
            name="readthis-server", 
            version="0.1.0"
        )
        
        # manuals.jsonの読み込み
        self.documents_config = self._load_documents_config()
        
        # ツールハンドラの登録
        self._register_tools()
        
        # MCP Serverの初期化完了ログ
        logger.error("[Setup] Serverオブジェクトが初期化されました")
        
        # エラーハンドラの登録（型チェック無視）
        self.server.onerror = lambda error: logger.error(f"[Error] MCPエラー: {error}")  # type: ignore
    
    def _load_documents_config(self) -> Dict:
        """
        manuals.jsonファイルを読み込む
        
        Returns:
            Dict: ドキュメント設定の辞書
        """
        try:
            config_path = Path('./manuals.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    logger.error(f"[Setup] manuals.jsonを読み込みました: {config_path}")
                    return json.load(f)
            else:
                logger.error("[Setup] manuals.jsonが見つかりません。デフォルト設定を使用します。")
                return {"documents": []}
        except Exception as e:
            logger.error(f"[Error] manuals.jsonの読み込みに失敗しました: {str(e)}")
            return {"documents": []}
    
    def _resolve_url(self, url_or_id: str) -> str:
        """
        URLまたはIDからURLを解決する
        
        Args:
            url_or_id: URLまたはドキュメントID
            
        Returns:
            str: 解決されたURL
            
        Raises:
            ValueError: IDが無効な場合
        """
        # 既にURLの場合はそのまま返す
        if url_or_id.startswith(('http://', 'https://')):
            return url_or_id
        
        # IDからURLを解決
        for doc in self.documents_config.get("documents", []):
            if doc.get("id") == url_or_id:
                return doc.get("url")
        
        # 該当するIDが見つからない場合はエラー
        raise ValueError(f"無効なドキュメントID: {url_or_id}。有効なURLまたはmanuals.jsonで定義されたIDを指定してください。")
    
    def _register_tools(self) -> None:
        """ツールハンドラの登録"""
        logger.error("[Setup] ツールハンドラを登録しています...")
        
        # readthisツールのハンドラ定義
        async def handle_readthis_request(request: Any) -> str:
            """
            指定されたURLからHTMLドキュメントを取得し、その内容を返す
            
            Args:
                request: リクエスト情報（URL情報を含む）
                
            Returns:
                str: 取得したドキュメントの内容
            """
            # URLをリクエストから取得
            url = request.params.url
            try:
                logger.error(f"[API] ドキュメント取得リクエスト: {url}")
                
                # URLの解決
                resolved_url = self._resolve_url(url)
                logger.error(f"[API] 解決されたURL: {resolved_url}")
                
                # ドキュメントの取得
                html_content = fetch_document(resolved_url)
                
                # HTMLの解析
                parsed_content = parse_html_content(html_content)
                
                logger.error(f"[API] ドキュメント取得完了: {len(parsed_content)} 文字")
                return parsed_content
                
            except ValueError as e:
                logger.error(f"[Error] 無効なURL/ID: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InvalidParams, message=str(e)))
            except DocumentFetchError as e:
                logger.error(f"[Error] ドキュメント取得エラー: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InternalError, message=f"ドキュメントの取得に失敗しました: {str(e)}"))
            except Exception as e:
                logger.error(f"[Error] 予期しないエラー: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InternalError, message=f"予期しないエラーが発生しました: {str(e)}"))
        
        # reload_manualsツールのハンドラ定義
        async def handle_reload_manuals_request(request: Any) -> Dict:
            """
            manuals.jsonファイルを再読み込みしてドキュメント設定を更新するハンドラ
            
            Args:
                request: リクエスト情報
                
            Returns:
                Dict: 更新後のドキュメント設定情報と結果ステータス
            """
            try:
                logger.error("[API] manuals.jsonのリロードを開始します")
                
                # 設定ファイルを再読み込み前の状態を記録
                previous_count = len(self.documents_config.get("documents", []))
                
                # 設定ファイルを再読み込み
                self.documents_config = self._load_documents_config()
                
                # 更新後の状態を取得
                current_count = len(self.documents_config.get("documents", []))
                
                # 結果を返す
                result = {
                    "success": True,
                    "message": f"manuals.jsonを正常にリロードしました",
                    "previous_documents_count": previous_count,
                    "current_documents_count": current_count, 
                    "documents": self.documents_config
                }
                
                logger.error(f"[API] manuals.jsonのリロード完了: {current_count} 件のドキュメント設定")
                return result
                
            except Exception as e:
                logger.error(f"[Error] manuals.jsonのリロード中にエラーが発生しました: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InternalError, message=f"設定ファイルのリロードに失敗しました: {str(e)}"))
                
        # ツールハンドラの登録（実際のMCP APIに合わせて修正が必要な場合があります）
        # 現在はコメントアウトしていますが、実際のMCP SDKの仕様に合わせて実装してください
        logger.error("[Setup] ツールハンドラの登録方法はMCP SDKの仕様に合わせて実装してください")
        
        # 例: CallToolRequestParamsを処理するハンドラの登録
        # self.server.tool("readthis", readthis_handler)
        # self.server.tool("reload_manuals", reload_manuals_handler)
    
    async def run(self) -> None:
        """サーバーの実行"""
        transport = stdio_server()
        await self.server.connect(transport)  # type: ignore
        logger.error("[Setup] ReadThis MCPサーバーが起動しました（stdio経由）")


if __name__ == "__main__":
    import asyncio
    
    server = ReadThisServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.error("[Setup] サーバーを終了しています...")
    except Exception as e:
        logger.error(f"[Error] サーバー実行中にエラーが発生しました: {str(e)}")
