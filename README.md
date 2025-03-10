# ReadThis MCP サーバー

このMCPサーバーは、AIエージェントがプログラム開発時に最新のライブラリドキュメントを参照できるようにするためのツールです。ユーザーのプロジェクトに置かれた `manuals.json` ファイルで指定されたドキュメントをウェブから取得し、AIのコンテキストに追加します。

## manuals.json の形式

プロジェクトのルートディレクトリに `manuals.json` ファイルを配置します。このファイルには以下の形式でドキュメント情報を記述します：

```json
{
  "documents": [
    {
      "id": "react-hooks",
      "name": "React Hooks API",
      "url": "https://reactjs.org/docs/hooks-reference.html",
      "description": "Reactフックの公式ドキュメント。useState, useEffectなどのフック使用時に参照。"
    },
    {
      "id": "python-asyncio",
      "url": "https://docs.python.org/3/library/asyncio.html",
      "name": "Python AsyncIO",
      "description": "Pythonの非同期プログラミングライブラリ。非同期アプリケーション開発時に参照。"
    }
  ]
}
```

## API: readthis

```python
def readthis(url: str) -> str:
    """
    指定されたURLからHTMLドキュメントを取得し、その内容を返します。
    
    このAPIは、AIエージェントがプログラミングタスクを行う際に参照すべき
    ライブラリやフレームワークのドキュメントを取得するために使用されます。
    取得したドキュメントの内容はAIエージェントのコンテキストに追加され、
    より正確なプログラム開発を支援します。
    
    Args:
        url (str): 取得するドキュメントのURL
                  ※ manuals.jsonで定義されたIDを使用することも可能です
    
    Returns:
        str: 取得したドキュメントの内容（HTML）
             HTMLから主要なコンテンツ部分を抽出して返します
    
    Raises:
        ValueError: URLが無効、またはmanuals.jsonに定義されていないIDが指定された場合
        ConnectionError: ドキュメントの取得に失敗した場合
        ParseError: HTMLの解析に失敗した場合
    
    Examples:
        # URLを直接指定
        content = readthis("https://docs.python.org/3/library/asyncio.html")
        
        # manuals.jsonで定義されたIDを使用
        content = readthis("python-asyncio")
    """
```

## API: reload_manuals

```python
def reload_manuals() -> dict:
    """
    manuals.jsonファイルを再読み込みして、ドキュメント設定を更新します。
    
    サーバー稼働中にmanuals.jsonファイルが更新された場合、
    このAPIを呼び出すことで設定の変更をリアルタイムに反映できます。
    サーバーの再起動は不要です。
    
    Returns:
        dict: 更新結果を含む辞書
            {
                "success": bool,  # 成功したかどうか
                "message": str,   # 結果メッセージ
                "previous_documents_count": int,  # 更新前のドキュメント数
                "current_documents_count": int,   # 更新後のドキュメント数
                "documents": dict  # 更新後のドキュメント設定全体
            }
    
    Raises:
        Exception: 設定ファイルの読み込みや解析に失敗した場合
    
    Examples:
        # 設定ファイルをリロード
        result = reload_manuals()
        print(f"リロード結果: {result['message']}")
        print(f"ドキュメント数: {result['current_documents_count']}")
    """
```

## 使用例

```python
# MCPサーバーのツールを使用
from mcp import use_tool

# URLを直接指定してドキュメントを取得
react_docs = use_tool("readthis-server", "readthis", {"url": "https://reactjs.org/docs/hooks-reference.html"})
print(f"React Hooksドキュメント: {len(react_docs)} 文字取得しました")

# manuals.jsonで定義されたIDを使用
asyncio_docs = use_tool("readthis-server", "readthis", {"url": "python-asyncio"})
print(f"AsyncIOドキュメント: {len(asyncio_docs)} 文字取得しました")

# manuals.jsonをリロード
reload_result = use_tool("readthis-server", "reload_manuals", {})
print(f"リロード結果: {reload_result['message']}")
print(f"ドキュメント数: {reload_result['current_documents_count']} (更新前: {reload_result['previous_documents_count']})")
```

## 実装詳細

このMCPサーバーは以下の処理を行います：

1. URLまたはIDが指定された場合、対応するドキュメントをウェブから取得
2. HTMLから主要なコンテンツ部分を抽出（余計なヘッダー、フッター、サイドバーなどを除去）
3. 抽出したコンテンツを文字列として返す
4. manuals.jsonのリロード機能により、サーバー再起動なしで設定を更新

## 制限事項

- 現在はHTML形式のドキュメントのみに対応しています
- 認証が必要なサイトのドキュメントは取得できません
- 一部のサイトではHTMLの構造によってコンテンツの抽出精度が変わる場合があります
