from flask_login import UserMixin


# Flask-Loginのuser_loaderはapp.pyに残す
# Flask-SQLAlchemyを使う場合は、ここでdb.Modelを継承する

class User(UserMixin):
    def __init__(self, id, username, password_hash, full_name, is_admin):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.is_admin = is_admin

    def get_id(self):
        return str(self.id)