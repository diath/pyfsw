from sqlalchemy import Column, Integer, String, ForeignKey
from pyfsw import db

class MarketOffer(db.Model):
	__tablename__ = 'market_offers'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	player_id = Column(Integer, ForeignKey('players.id'))
	sale = Column(Integer)
	itemtype = Column(Integer)
	amount = Column(Integer)
	created = Column(Integer)
	anonymous = Column(Integer)
	price = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<MarketOffer.{}>'.format(self.id)

class MarketHistory(db.Model):
	__tablename__ = 'market_history'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	player_id = Column(Integer, ForeignKey('players.id'))
	sale = Column(Integer)
	itemtype = Column(Integer)
	amount = Column(Integer)
	price = Column(Integer)
	expires_at = Column(Integer)
	inserted = Column(Integer)
	state = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<MarketHistory.{}>'.format(self.id)
