from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, g, session
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

# セッションタイムアウトの設定 (5分)
app.permanent_session_lifetime = timedelta(minutes=5) 

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
    # PostgreSQLではプレースホルダーは%s
    cursor.execute("SELECT id, username, password_hash, full_name, is_admin FROM users WHERE id = %s", (user_id,)) 
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

# Flask-Babelはg.localeとg.timezoneを自動的に使用します。
# @babel.localeselector や @babel.timezoneselector デコレーターは削除しました。

# --- Blueprintの登録 ---
app.register_blueprint(auth_bp)
app.register_blueprint(shifts_bp)
app.register_blueprint(admin_bp)

# --- データベース初期化 (アプリコンテキスト内で実行) ---
with app.app_context():
    init_db(app, ADMIN_USERNAME, ADMIN_PASSWORD) # appインスタンスとADMIN_USERNAME, ADMIN_PASSWORDを渡す

# --- 新しいAPIエンドポイント: ログインユーザー情報を返す ---
@app.route('/api/user_info', methods=['GET'])
@login_required
def get_user_info():
    """現在ログイン中のユーザー情報を返すAPI"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'fullName': current_user.full_name,
        'isAdmin': current_user.is_admin
    })


if __name__ == '__main__':
    # 開発用サーバーを実行
    app.run(debug=True, port=5001)