from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()
metadata = Base.metadata

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    brand_name = Column(String(60), unique=True, nullable=True)
    name = Column(String(60), unique=True, nullable=False)

    # RELATIONSHIP(s) 
    ingredients = relationship('ProductIngredient', back_populates='product')

    def __repr__(self):
        return f'id: {self.id} - brand_name: {self.brand_name} > name: {self.name}'

class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    alias = Column(String(60), unique=True, nullable=True)

    # RELATIONSHIP(s)
    products = relationship('ProductIngredient', back_populates='ingredient')
    components = relationship('IngredientComponent', foreign_keys='IngredientComponent.ingredient_id', back_populates='ingredient')
    component_of = relationship('IngredientComponent', foreign_keys='IngredientComponent.component_id', back_populates='component')

    def __repr__(self):
        return f'id: {self.id} - name: {self.name}'

class ProductIngredient(Base):
    """
        This table will store the relationship between products and their ingredients. It will help in associating multiple ingredients with a single product.
    """
    __tablename__ = 'product_ingredients'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)

    # Establish relationships
    product = relationship('Product', back_populates='ingredients')
    ingredient = relationship('Ingredient', back_populates='products')

    def __repr__(self):
        return f'id: {self.id} - product_id: {self.product_id} - ingredient_id: {self.ingredient_id}'

class IngredientComponent(Base):
    """
        This table handles cases where ingredients are composed of other ingredients. For example, "Enriched Macaroni" is composed of "Wheat Flour", "Durum Flour", etc.
    """
    __tablename__ = 'ingredient_components'

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    component_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)

    # Establish relationships
    ingredient = relationship('Ingredient', foreign_keys=[ingredient_id], back_populates='components')
    component = relationship('Ingredient', foreign_keys=[component_id], back_populates='component_of')

    def __repr__(self):
        return f'id: {self.id} - ingredient_id: {self.ingredient_id} - component_id: {self.component_id}'

class Summary(Base):
    __tablename__ = 'summaries'

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
