from ..extensions import db

class TestObj(db.Model):
    __tablename__ = 'testobjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }