from sqlalchemy import Column, Integer, String, ForeignKey

from pyfsw import db
from pyfsw import Player

class House(db.Model):
	__tablename__ = 'houses'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	owner = Column(Integer, ForeignKey('players.id'))
	paid = Column(Integer)
	warnings = Column(Integer)
	name = Column(String(255))
	rent = Column(Integer)
	town_id = Column(Integer)
	bid = Column(Integer)
	bid_end = Column(Integer)
	last_bid = Column(Integer)
	highest_bidder = Column(Integer)
	size = Column(Integer)
	beds = Column(Integer)

	# Relationships
	player = db.relationship('Player', foreign_keys='House.owner')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<House {} => {}>'.format(self.id, self.name)
