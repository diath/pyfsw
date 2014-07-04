from sqlalchemy import Column, Integer, String, Text, ForeignKey
from pyfsw import db

class ShopCategory(db.Model):
	__tablename__ = 'shop_category'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	name = Column(String(32))
	enabled = Column(Integer, default=1)

	# Relationship
	items = db.relationship('ShopItem', backref='shop_category')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<ShopCategory.{}.{}>'.format(self.id, self.name)

class ShopItem(db.Model):
	__tablename__ = 'shop_item'

	# Constants
	Type = {
		'Item': 1,
		'Container': 2,
		'Addon': 3,
		'Mount': 4
	}

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	name = Column(String(32))
	description = Column(Text)
	category_id = Column(Integer, ForeignKey('shop_category.id'))
	type = Column(Integer)
	key = Column(Integer)
	value = Column(Integer)
	price = Column(Integer)
	enabled = Column(Integer, default=1)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<ShopItem.{}>'.format(self.id)

class ShopOrder(db.Model):
	__tablename__ = 'shop_order'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	name = Column(String(32))
	type = Column(Integer)
	key = Column(Integer)
	value = Column(Integer)
	price = Column(Integer)
	ordered = Column(Integer)
	character_id = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<ShopOrder.{}>'.format(self.id)

class ShopHistory():
	def __init__(self):
		pass
