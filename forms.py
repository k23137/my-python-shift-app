from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

# Flask-Babelの翻訳機能を利用
from flask_babel import _

# dbモジュールから接続関数をインポート
from db import get_db_connection

class LoginForm(FlaskForm):
    username = StringField(_('ユーザーID'), validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField(_('パスワード'), validators=[DataRequired(), Length(min=4, max=10)])
    submit = SubmitField(_('ログイン'))

class AddUserForm(FlaskForm):
    username = StringField(_('ユーザーID'), validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField(_('パスワード'), validators=[DataRequired(), Length(min=4, max=10)])
    confirm_password = PasswordField(_('パスワード（確認）'), validators=[DataRequired(), EqualTo('password', message=_('パスワードが一致しません。'))])
    is_admin = BooleanField(_('管理者として追加'))
    submit = SubmitField(_('ユーザー追加'))

    def validate_username(self, username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username.data,))
        user = cursor.fetchone()
        conn.close()
        if user:
            raise ValidationError(_('このユーザーIDは既に使われています。'))

class AdminPasswordForm(FlaskForm):
    admin_password = PasswordField(_('管理者パスワード'), validators=[DataRequired()])
    submit = SubmitField(_('進む'))