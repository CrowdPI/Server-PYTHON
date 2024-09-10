from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    brand_name = Column(String(60), unique=True, nullable=True)
    name = Column(String(60), unique=True, nullable=False)

    # RELATIONSHIP(s) 
    ingredients = relationship('Product_Ingredients', back_populates='product')

    def __repr__(self):
        return f'id: {self.id} - brand_name: {self.brand_name} > name: {self.name}'

class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    alias = Column(String(60), unique=True, nullable=True)

    # RELATIONSHIP(s)
    products = relationship('Product_Ingredients', back_populates='ingredient')

    def __repr__(self):
        return f'id: {self.id} - name: {self.name}'

class Product_Ingredients(Base):
    __tablename__ = 'product_ingredients'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)

    # Establish relationships
    product = relationship('Product', back_populates='ingredients')
    ingredient = relationship('Ingredient', back_populates='products')

    def __repr__(self):
        return f'id: {self.id} - product_id: {self.product_id} - ingredient_id: {self.ingredient_id}'
