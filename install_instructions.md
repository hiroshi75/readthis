# ReadThis MCPプラグインのインストール手順

このドキュメントでは、ReadThis MCPプラグインのインストール方法と設定について説明します。

## 前提条件

- Python 3.12 以上
- uvまたはpip（パッケージインストール用）
- Cline拡張機能がインストールされたClaudeデスクトップアプリ

## インストール手順

1. リポジトリをクローンまたはダウンロードします。

```bash
git clone <repository-url>
cd readthis
```

2. 依存パッケージをインストールします。

uvを使用する場合:
```bash
uv pip install -r requirements.txt
```

pipを使用する場合:
```bash
pip install -r requirements.txt
```

## MCPサーバーの設定

1. Claudeデスクトップアプリの設定ファイルを開きます。

Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

macOS:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

2. 設定ファイルに以下のMCPサーバー定義を追加します。

```json
{
  "mcpServers": {
    "readthis-server": {
      "command": "python",
      "args": ["path/to/readthis/server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

`path/to/readthis/server.py` を実際のserver.pyファイルのパスに置き換えてください。

## 使用方法

1. プロジェクトのルートディレクトリに `manuals.json` ファイルを作成し、参照したいドキュメントを定義します。

```json
{
  "documents": [
    {
      "id": "react-hooks",
      "name": "React Hooks API",
      "url": "https://react.dev/reference/react",
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

2. Claudeに対して、ドキュメントを読み込むよう指示します。

例:
```
Reactフックについて開発しています。ドキュメントを参照して、useStateとuseEffectの使い方を説明してください。
```

Claudeは必要に応じてReadThis MCPサーバーを使用し、指定されたドキュメントを参照して回答します。

## トラブルシューティング

- MCPサーバーが接続されていない場合は、Claude設定ファイルのパスが正しいか確認してください。
- ドキュメントが取得できない場合は、URLが正しいか、またインターネット接続が利用可能か確認してください。
- ログを確認するには、server.pyを直接実行して出力を確認してください。
