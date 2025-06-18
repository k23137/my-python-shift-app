from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# 外部ファイルのインポート
from db import get_db_connection
from models import User # Userモデルはmodels.pyからインポート
from forms import AddUserForm, AdminPasswordForm
from flask_babel import _
from config import ADMIN_USERNAME # config.py から ADMIN_USERNAME をインポート

admin_bp = Blueprint('admin', __name__) # Blueprintを作成

@admin_bp.route('/settings_auth', methods=['GET', 'POST'])
@login_required
def settings_auth():
    if not current_user.is_admin:
        flash(_('管理者権限が必要です。'), 'danger')
        # ★修正点★: url_for('index') -> url_for('shifts.index')
        return redirect(url_for('shifts.index'))

    form = AdminPasswordForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s AND is_admin = TRUE", (ADMIN_USERNAME,))
        admin_password_hash = cursor.fetchone()
        conn.close()

        if admin_password_hash and check_password_hash(admin_password_hash[0], form.admin_password.data):
            # 管理者パスワードが正しい場合、設定画面へリダイレクト
            # ★修正なし（adminブループリント内のsettingsルートなのでOK）★
            return redirect(url_for('admin.settings')) 
        else:
            flash(_('管理者パスワードが間違っています。'), 'danger')
    return render_template('settings_auth.html', form=form)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin:
        flash(_('管理者権限が必要です。'), 'danger')
        # ★修正点★: url_for('index') -> url_for('shifts.index')
        return redirect(url_for('shifts.index'))
    
    add_user_form = AddUserForm()
    if add_user_form.validate_on_submit() and request.form.get('form_name') == 'add_user':
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(add_user_form.password.data)
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
                (add_user_form.username.data, hashed_password, add_user_form.is_admin.data)
            )
            conn.commit()
            flash(_('ユーザー "%(username)s" が追加されました！', username=add_user_form.username.data), 'success')
            # ★修正なし（adminブループリント内のsettingsルートなのでOK）★
            return redirect(url_for('admin.settings')) 
        except Exception as e:
            flash(_('ユーザー追加エラー: %(error_message)s', error_message=str(e)), 'danger')
            conn.rollback()
        finally:
            conn.close()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, is_admin FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template('settings.html', add_user_form=add_user_form, users=users)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash(_('管理者権限が必要です。'), 'danger')
        # ★修正点★: url_for('index') -> url_for('shifts.index')
        return redirect(url_for('shifts.index'))
    
    if user_id == current_user.id:
        flash(_('自分自身を削除することはできません。'), 'danger')
        # ★修正なし（adminブループリント内のsettingsルートなのでOK）★
        return redirect(url_for('admin.settings')) 

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash(_('ユーザーを削除しました。'), 'success')
    except Exception as e:
        flash(_('ユーザー削除エラー: %(error_message)s', error_message=str(e)), 'danger')
        conn.rollback()
    finally:
        conn.close()
    # ★修正なし（adminブループリント内のsettingsルートなのでOK）★
    return redirect(url_for('admin.settings'))