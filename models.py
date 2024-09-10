from sqlalchemy import Column, DateTime, String, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    alias = Column(String(60), unique=True, nullable=True)

    def __repr__(self):
        return f'id: {self.id} - name: {self.name}'