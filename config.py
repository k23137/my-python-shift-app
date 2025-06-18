import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here' # 本番では環境変数を使用
    BABEL_DEFAULT_LOCALE = 'ja'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Tokyo'
    # ローカル開発用DB_URL（RenderのPostgreSQL接続文字列をここに貼り付けるか、別途ローカルDBを用意）
    # 例: postgresql://admin:password@localhost:5432/shift_db
    # Renderにデプロイする際は、Render側で設定するDATABASE_URL環境変数が優先されます。
    DATABASE_URL = os.environ.get('DATABASE_URL') or "postgresql://my_shift_app_db_user:KovtPYhQYdqrFDHoCFLnPZOMgxZjGnfN@dpg-d18m5bmmcj7s73a5ih2g-a.singapore-postgres.render.com/my_shift_app_db"
    # 上の行の <your_render_user> ... の部分をあなたの実際の接続文字列で置き換えてください

STAFF_NAMES = ["昼", "夜"] # シフト担当者の名前
ADMIN_USERNAME = "Yokoyama" # 管理者ユーザーのデフォルト名
ADMIN_PASSWORD = "3236" # 管理者ユーザーのデフォルトパスワード (初回作成用)