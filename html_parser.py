#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import trafilatura

# ロギング設定
logger = logging.getLogger("readthis-server")

class DocumentFetchError(Exception):
    """ドキュメント取得時のエラーを表す例外クラス"""
    pass


def fetch_document(url: str) -> str:
    """
    指定されたURLからHTMLドキュメントを取得する
    
    Args:
        url: 取得するドキュメントのURL
        
    Returns:
        str: 取得したHTMLドキュメント
        
    Raises:
        DocumentFetchError: ドキュメントの取得に失敗した場合
    """
    try:
        logger.error(f"[Fetch] ドキュメントを取得しています: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # HTTP エラーがある場合は例外を発生
        
        logger.error(f"[Fetch] ドキュメント取得成功: {len(response.text)} バイト")
        return response.text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[Error] ドキュメント取得リクエストエラー: {str(e)}")
        raise DocumentFetchError(f"ドキュメントの取得に失敗しました: {str(e)}")
    except Exception as e:
        logger.error(f"[Error] 予期しない取得エラー: {str(e)}")
        raise DocumentFetchError(f"予期しないエラーが発生しました: {str(e)}")


def parse_html_content(html_content: str) -> str:
    """
    HTMLコンテンツからメインコンテンツを抽出する
    
    Args:
        html_content: 解析するHTMLコンテンツ
        
    Returns:
        str: 抽出されたメインコンテンツ
        
    Raises:
        ValueError: HTMLの解析に失敗した場合
    """
    try:
        logger.error("[Parse] HTMLコンテンツを解析しています...")
        
        # trafilaturaを使用してメインコンテンツを抽出
        extracted_text = trafilatura.extract(html_content, include_links=True, include_images=True, include_tables=True)
        
        # trafilaturaで抽出できなかった場合はBeautifulSoupでシンプルに抽出を試みる
        if not extracted_text:
            logger.error("[Parse] trafilaturaでの抽出に失敗したため、BeautifulSoupを使用します")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # スクリプトと不要なタグを削除
            for script in soup(["script", "style"]):
                script.extract()
                
            # ページの本文を抽出
            body = soup.body
            if body:
                # ヘッダーとフッターらしきものを除去する試み
                for unwanted in body.select('header, footer, nav, .sidebar, #sidebar, .menu, #menu, .navigation, .ads, .advertisement'):
                    unwanted.extract()
                
                # メインコンテンツらしきものを探す
                main_content = body.select_one('main, #main, .main, article, .article, .content, #content')
                if main_content:
                    extracted_text = main_content.get_text(separator='\n')
                else:
                    # 見つからない場合はbodyの全テキストを使用
                    extracted_text = body.get_text(separator='\n')
            else:
                # bodyが見つからない場合
                extracted_text = soup.get_text(separator='\n')
            
            # 余分な空白と改行を整理
            lines = (line.strip() for line in extracted_text.splitlines())
            extracted_text = '\n'.join(line for line in lines if line)
        
        logger.error(f"[Parse] コンテンツ抽出完了: {len(extracted_text)} 文字")
        return extracted_text
        
    except Exception as e:
        logger.error(f"[Error] HTML解析エラー: {str(e)}")
        raise ValueError(f"HTMLの解析に失敗しました: {str(e)}")


def get_document_metadata(url: str) -> Dict[str, Any]:
    """
    ドキュメントのメタデータ（タイトル、説明など）を取得する
    
    Args:
        url: 取得するドキュメントのURL
        
    Returns:
        Dict[str, Any]: メタデータの辞書
    """
    try:
        html_content = fetch_document(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title = soup.title.string if soup.title else "不明なタイトル"
        
        # メタ説明の取得を試みる
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            description = meta_desc['content']
        
        return {
            "title": title.strip() if title else "",
            "description": description.strip() if description else "",
            "url": url
        }
    except Exception as e:
        logger.error(f"[Error] メタデータ取得エラー: {str(e)}")
        return {
            "title": "取得エラー",
            "description": "",
            "url": url
        }
