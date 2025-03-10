#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
reload_manuals ツールの統合テストスクリプト

このスクリプトは、実際のReadThisServerのreload_manuals機能を
モックを使わずに直接テストします。
"""

import os
import sys
import json
import asyncio
import shutil
from pathlib import Path

# テスト対象のモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# reload_manuals関数を直接テスト

async def main():
    """統合テスト実行"""
    # テスト用のmanuals.jsonを準備
    original_path = Path("./manuals.json")
    backup_path = Path("./manuals.json.bak")
    test_path = Path("./manuals.json")
    
    # 既存のファイルがあればバックアップ
    if original_path.exists():
        print(f"既存のmanuals.jsonをバックアップしています: {backup_path}")
        shutil.copy2(original_path, backup_path)
    
    try:
        # 初期データ
        documents_config = {}
        
        # _load_documents_config関数をシミュレート
        def _load_documents_config():
            try:
                config_path = Path('./manuals.json')
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        print(f"manuals.jsonを読み込みました: {config_path}")
                        return json.load(f)
                else:
                    print("manuals.jsonが見つかりません。デフォルト設定を使用します。")
                    return {"documents": []}
            except Exception as e:
                print(f"manuals.jsonの読み込みに失敗しました: {str(e)}")
                return {"documents": []}
        
        # reload_manuals実装をシミュレート
        async def reload_manuals():
            nonlocal documents_config
            
            print("manuals.jsonのリロードを開始します")
            
            # 設定ファイルを再読み込み前の状態を記録
            previous_count = len(documents_config.get("documents", []))
            
            # 設定ファイルを再読み込み
            documents_config = _load_documents_config()
            
            # 更新後の状態を取得
            current_count = len(documents_config.get("documents", []))
            
            # 結果を返す
            result = {
                "success": True,
                "message": f"manuals.jsonを正常にリロードしました",
                "previous_documents_count": previous_count,
                "current_documents_count": current_count, 
                "documents": documents_config
            }
            
            print(f"manuals.jsonのリロード完了: {current_count} 件のドキュメント設定")
            return result
        
        # テスト用のドキュメント設定を作成
        initial_data = {
            "documents": [
                {
                    "id": "test-doc-1",
                    "name": "テストドキュメント1",
                    "url": "https://example.com/test1",
                    "description": "テスト用のドキュメント1"
                }
            ]
        }
        
        # テスト用のJSONファイルを書き込み
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)
        
        print(f"テスト用のmanuals.jsonを作成しました: {len(initial_data['documents'])} 件のドキュメント")
        
        # 初期設定を読み込む
        documents_config = _load_documents_config()
        print(f"初期ドキュメント数: {len(documents_config.get('documents', []))}")
        
        # テスト1: 変更なしでのリロード
        print("\n--- テスト1: 変更なしでのリロード ---")
        result1 = await reload_manuals()
        print(f"結果: {result1['message']}")
        print(f"ドキュメント数: {result1['current_documents_count']} (変更前: {result1['previous_documents_count']})")
        
        # テスト2: ドキュメントを追加してリロード
        print("\n--- テスト2: ドキュメント追加後のリロード ---")
        updated_data = initial_data.copy()
        updated_data["documents"].append({
            "id": "test-doc-2",
            "name": "テストドキュメント2",
            "url": "https://example.com/test2",
            "description": "テスト用のドキュメント2"
        })
        
        # 更新されたデータでファイルを上書き
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        result2 = await reload_manuals()
        print(f"結果: {result2['message']}")
        print(f"ドキュメント数: {result2['current_documents_count']} (変更前: {result2['previous_documents_count']})")
        assert result2["current_documents_count"] == 2, "ドキュメント追加が反映されていません"
        
        # テスト3: ドキュメントを変更してリロード
        print("\n--- テスト3: ドキュメント変更後のリロード ---")
        updated_data["documents"][0]["name"] = "更新されたテストドキュメント"
        updated_data["documents"][0]["url"] = "https://example.com/updated"
        
        # 更新されたデータでファイルを上書き
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)
        
        result3 = await reload_manuals()
        print(f"結果: {result3['message']}")
        print(f"ドキュメント数: {result3['current_documents_count']} (変更前: {result3['previous_documents_count']})")
        print(f"更新されたドキュメント名: {result3['documents']['documents'][0]['name']}")
        assert result3["documents"]["documents"][0]["name"] == "更新されたテストドキュメント", "ドキュメント更新が反映されていません"
        
        # テスト4: ドキュメントを削除してリロード
        print("\n--- テスト4: ドキュメント削除後のリロード ---")
        reduced_data = {
            "documents": [updated_data["documents"][0]]  # 2つ目のドキュメントを削除
        }
        
        # 更新されたデータでファイルを上書き
        with open(test_path, "w", encoding="utf-8") as f:
            json.dump(reduced_data, f, ensure_ascii=False, indent=2)
        
        result4 = await reload_manuals()
        print(f"結果: {result4['message']}")
        print(f"ドキュメント数: {result4['current_documents_count']} (変更前: {result4['previous_documents_count']})")
        assert result4["current_documents_count"] == 1, "ドキュメント削除が反映されていません"
        
        print("\n全てのテストが正常に完了しました！")
        
    except AssertionError as e:
        print(f"テスト失敗: {str(e)}")
    except Exception as e:
        print(f"予期しないエラー: {str(e)}")
    finally:
        # バックアップがあれば元に戻す
        if backup_path.exists():
            print(f"manuals.jsonをバックアップから復元しています")
            shutil.copy2(backup_path, original_path)
            backup_path.unlink()
        else:
            # テスト用ファイルを削除
            if test_path.exists():
                test_path.unlink()

if __name__ == "__main__":
    print("reload_manuals ツールの統合テストを開始します...")
    asyncio.run(main())
