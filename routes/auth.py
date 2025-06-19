from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

# 外部ファイルのインポート
from db import get_db_connection
from models import User
from forms import LoginForm
from flask_babel import _

auth_bp = Blueprint('auth', __name__) # Blueprintを作成

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        # ★修正点★: SELECT文に full_name, is_admin を追加
        cursor.execute("SELECT id, username, password_hash, full_name, is_admin FROM users WHERE username = %s", (form.username.data,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and check_password_hash(user_data[2], form.password.data):
            user = User(*user_data) # ここで取得したuser_dataがUserクラスのコンストラクタに渡される
            login_user(user)
            flash(_('ログインしました！'), 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('shifts.index'))
        else:
            flash(_('無効なユーザーIDまたはパスワードです。'), 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('ログアウトしました。'), 'info')
    # ★修正点★: url_for('login') -> url_for('auth.login')
    return redirect(url_for('auth.login'))