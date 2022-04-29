# verible


This repository is executing [Verible SystemVerilog Syntax Tool][link-syntax_tool] by TypeScript language.

Since Verible's sample code is [`export_json_examples`][link-export_json_examples] by Python language,
the repository code is coded by TypeScript language.

[link-verible]:https://github.com/chipsalliance/verible

[link-syntax_tool]:https://github.com/chipsalliance/verible/tree/master/verilog/tools/syntax

# Codes using the repository
* verible [`export_json_examples`][link-export_json_examples]

[link-export_json_examples]:https://github.com/chipsalliance/verible/tree/master/verilog/tools/syntax/export_json_examples

# License

Licensed under Apache License, Version 2.0, ([http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0))

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
### Nuitkaのインストール方法
`※余計なプラグインをパッケージングしないように仮想環境へインストールする。`
```
python -m pip install nuitka zstandard
```

### Nuitka実行時に含まれるパッケージ一覧を表示
`※リストに表示されないプラグインは、仮想環境または外部環境内にパッケージがインストールされていない可能性があるため、pipを実行`
```
python -m nuitka --plugin-list
```

### 

### Nuitkaの実行コマンド
```
nuitka --mingw64 --follow-imports --onefile (エントリーポイントにしたい Python ファイル).py
```
