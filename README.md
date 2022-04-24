# verible

## Python仮想環境の構築手順

仮想環境内で必要なパッケージをインストールすることにより、開発するパッケージが依存するパッケージを管理できるようする。

仮想環境を構築せずにパッケージを開発した場合、依存パッケージが分からなくなる（OS内にインストールされているパッケージ全てとなる）。

### Workspaceディレクトリ内に".venv"を作成後、`venv`コマンドにより、仮想環境を作成する。
```
mkdir .venv
python -m venv .venv
```

### 仮想環境の有効化方法

For Windows
```
.venv\Scripts\activate.bat
```

For Linux
```
source .venv/bin/activate
```

### パッケージのインストールコマンド（例 anytree）
```
python -m pip install anytree
```

### 仮想環境内でインストールしたパッケージ一覧を管理ファイル"requirements.txt"として保存する方法
```
pip freeze > requirements.txt
```

### パッケージ管理ファイル"requirements.txt"からパッケージ一覧をインストールする方法
```
python -m pip install -r requirements.txt
```
