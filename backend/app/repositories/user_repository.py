from ..extensions import db
from ..models import User


class UserRepository:
    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        statement = db.select(User).filter_by(email=email)
        return db.session.scalar(statement)
