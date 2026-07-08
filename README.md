# FastAPI Todo Calendar

日付ごとに Todo を管理できる Web アプリケーションです。カレンダーから日付を選び、その日のタスクを追加・完了・削除できます。

## 機能

- 月表示カレンダーから日付を選択
- 選択した日付の Todo 一覧表示
- Todo の追加・完了切り替え・削除
- Todo 詳細ページ
- Todo がある日付をカレンダー上でドット表示

## 技術スタック

| 区分 | 技術 |
| --- | --- |
| バックエンド | FastAPI |
| テンプレート | Jinja2 |
| ORM | SQLAlchemy |
| データベース | PostgreSQL |
| 環境変数 | python-dotenv |
| サーバー | Uvicorn |

## プロジェクト構成

```
FastAPITodo/
├── main.py              # ルーティング・ビジネスロジック
├── models.py            # Todo モデル定義
├── database.py          # DB 接続設定
├── templates/
│   ├── base.html        # 共通レイアウト
│   ├── index.html       # カレンダー画面
│   ├── todo.html        # Todo 一覧画面
│   └── about.html       # Todo 詳細画面
├── static/
│   └── css/
│       └── style.css    # スタイル
├── .env                 # 環境変数（Git 管理外）
└── README.md
```

## セットアップ

### 1. 前提条件

- Python 3.9 以上
- PostgreSQL

### 2. リポジトリのクローンと仮想環境

```bash
git clone <repository-url>
cd FastAPITodo
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. 依存パッケージのインストール

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
```

### 4. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成します。

```env
DATABASE_URL=postgresql://postgres:@localhost:5432/postgres
```

接続 URL の形式:

```
postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名
```

### 5. データベースの準備

PostgreSQL を起動し、接続先データベースを作成してください。アプリ起動時に `Base.metadata.create_all()` で `todos` テーブルが自動作成されます。

既存テーブルへカラムを追加する場合は、`create_all()` では反映されないため、PgAdmin4 などで手動実行が必要です。

```sql
ALTER TABLE todos ADD COLUMN todo_date DATE DEFAULT CURRENT_DATE;
ALTER TABLE todos ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

## 起動方法

```bash
uvicorn main:app --reload
```

ブラウザで [http://127.0.0.1:8000](http://127.0.0.1:8000) を開きます。

## 画面の使い方

1. トップページ（`/`）でカレンダーを表示
2. 日付をクリックして Todo 一覧（`/todos/YYYY-MM-DD`）へ遷移
3. タスクを追加・完了・削除
4. 「カレンダーに戻る」リンクでトップへ戻る

## エンドポイント

| メソッド | パス | 説明 |
| --- | --- | --- |
| GET | `/` | カレンダー画面 |
| GET | `/todos/{selected_date}` | 指定日の Todo 一覧 |
| GET | `/about/{todo_id}` | Todo 詳細 |
| POST | `/add` | Todo 追加 |
| POST | `/done/{todo_id}` | 完了 / 未完了の切り替え |
| POST | `/delete/{todo_id}` | Todo 削除 |

### クエリパラメータ（カレンダー）

| パラメータ | 説明 | 例 |
| --- | --- | --- |
| `cal_year` | 表示する年 | `2026` |
| `cal_month` | 表示する月 | `7` |

例: `/?cal_year=2026&cal_month=7`

## データモデル

### todos テーブル

| カラム | 型 | 説明 |
| --- | --- | --- |
| `id` | INTEGER | 主キー |
| `title` | VARCHAR(100) | タスク名 |
| `done` | BOOLEAN | 完了フラグ |
| `todo_date` | DATE | タスクの日付 |
| `created_at` | TIMESTAMP | 作成日時 |

## 注意事項

- `.env` には DB 接続情報が含まれるため、Git にコミットしないでください（`.gitignore` に含まれています）
- スキーマ変更を本格的に管理する場合は Alembic の導入を検討してください
- API ドキュメントは [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) で確認できます
