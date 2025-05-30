from flask_login import UserMixin
from ..database import get_db
from .user import User


class UserData:
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


class UserModel(UserMixin):
    def __init__(self, user_data):
        """
        :param user_data: UserData
        """
        self.id = str(user_data.id)
        self.username = user_data.username
        self.password = user_data.password
        self.email = user_data.email

    @staticmethod
    def query(user_identifier):
        user_doc = None
        try:
            user_doc = get_user_by_id(int(user_identifier))
        except (ValueError, TypeError):
            pass

        if not user_doc:
            user_doc = get_user(user_identifier)

        if user_doc:
            user_data = UserData(
                id=user_doc.id, 
                username=user_doc.username,
                password=user_doc.password,
                email=user_doc.email,
            )
            return UserModel(user_data)
        return None


def get_user(username, db=None):
    if db is None:
        db = next(get_db()) #
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(user_id, db=None): # Nueva función para buscar usuario por ID
    if db is None:
        db = next(get_db())
    return db.query(User).filter(User.id == user_id).first()