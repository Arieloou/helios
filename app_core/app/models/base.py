from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from app.database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id, cls.is_deleted == False).first()

    @classmethod
    def get_all(cls):
        return cls.query.filter(cls.is_deleted == False).all()

    def save(self, db):
        db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db, soft=True):
        if soft:
            self.soft_delete()
            db.commit()
        else:
            db.delete(self)
            db.commit()