from flask_login import UserMixin  # type: ignore
from ..database import get_db
from .user import User


class UserData:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


class UserModel(UserMixin):
    def __init__(self, user_data):
        """
        :param user_data: UserData
        """
        self.id = user_data.username
        self.password = user_data.password
        self.email = user_data.email

    @staticmethod
    def query(user_id):
        user_doc = get_user(user_id)
        user_data = UserData(
            username=user_doc.username,
            password=user_doc.password,
            email=user_doc.email,
        )

        return UserModel(user_data)


def get_user(username, db=None):
    if db is None:
        db = next(get_db())
    return db.query(User).filter(User.username == username).first()
