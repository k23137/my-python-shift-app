from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, g
from datetime import date, timedelta
import os
import psycopg2
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash

# Flask-Loginのインポート
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Flask-WTF（フォーム作成用）のインポート
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

# Flask-Babelのインポート
from flask_babel import Babel, _, get_locale, format_date

# 外部ファイルのインポート
from config import Config, STAFF_NAMES, ADMIN_USERNAME, ADMIN_PASSWORD
from db import init_db, get_db_connection
from models import User
from routes.auth import auth_bp
from routes.shifts import shifts_bp
from routes.admin import admin_bp

app = Flask(__name__)

# --- アプリケーション設定 ---
app.config.from_object(Config) # config.py から設定を読み込む

# --- Flask拡張機能の初期化 ---
babel = Babel(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # ログインビューのブループリント名を含むパスに変更

# --- Flask-Loginのuser_loader ---
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, is_admin FROM users WHERE id = %s", (user_id,)) # PostgreSQLは?ではなく%s
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(*user_data)
    return None

# --- リクエスト前処理 (ロケール・タイムゾーン設定) ---
@app.before_request
def before_request():
    g.locale = request.accept_languages.best_match(['ja', 'en']) or 'ja'
    g.timezone = 'Asia/Tokyo' 

# ★重要★
# @babel.localeselector および @babel.timezoneselector デコレーターは削除しました。
# これらは、g.locale / g.timezone を設定する方式では不要であり、
# Flask-BabelのバージョンによってはAttributeErrorを引き起こすためです。
# 代わりに、Babelはg.locale / g.timezoneを自動的に使用します。

# --- Blueprintの登録 ---
app.register_blueprint(auth_bp)
app.register_blueprint(shifts_bp)
app.register_blueprint(admin_bp)

# --- データベース初期化 (アプリコンテキスト内で実行) ---
with app.app_context():
    init_db(app, ADMIN_USERNAME, ADMIN_PASSWORD) # appインスタンスとADMIN_USERNAME, ADMIN_PASSWORDを渡す

if __name__ == '__main__':
    # 開発用サーバーを実行
    app.run(debug=True)