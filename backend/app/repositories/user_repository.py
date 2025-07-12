from ..extensions import db
from ..models import User


class UserRepository:
    @staticmethod
    def find_user_by_email(email: str) -> User | None:
        return db.session.scalar(db.select(User).filter_by(email=email))
