import psycopg2
from urllib.parse import urlparse
import os

from config import Config
from werkzeug.security import generate_password_hash

def get_db_connection():
    database_url = Config.DATABASE_URL
    
    url = urlparse(database_url)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        sslmode='require' if 'render.com' in url.hostname else 'prefer'
    )
    return conn

# init_db 関数が app オブジェクト、ADMIN_USERNAME, ADMIN_PASSWORD を引数として受け取るように変更
def init_db(app, admin_username, admin_password):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ★users テーブルに full_name カラムを追加★
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY, 
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT, -- ★追加: 名前を保存するカラム (NULL許容)★
                is_admin BOOLEAN NOT NULL DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shift_entries (
                date_str TEXT NOT NULL,
                staff_name TEXT NOT NULL,
                status TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (date_str, staff_name, user_id),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

        # 管理者ユーザーが存在しない場合に自動で作成
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
        if cursor.fetchone()[0] == 0:
            admin_password_hash = generate_password_hash(admin_password)
            # ★管理者ユーザーの初期名を設定★
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, is_admin) VALUES (%s, %s, %s, %s)", 
                (admin_username, admin_password_hash, "管理者", True) # ★名前も挿入★
            )
            conn.commit()
            print(f"管理者ユーザー '{admin_username}' (名前: '管理者') を作成しました。パスワードは '{admin_password}' です。")
            print("本番環境ではパスワードを変更してください。")

    except Exception as e:
        print(f"データベース初期化エラー: {e}")
        app.logger.error(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()