from sqlalchemy import Column, Integer, String
from pyfsw import db

class Account(db.Model):
	__tablename__ = 'accounts'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	name = Column(String(32))
	password = Column(String(40))
	type = Column(Integer, default=1)
	premdays = Column(Integer, default=0)
	lastday = Column(Integer, default=0)
	email = Column(String(255))
	creation = Column(Integer)
	lastpost = Column(Integer, default=0)

	# Custom columns
	key = Column(String(19))
	points = Column(Integer, default=0)
	web_access = Column(Integer, default=0)

	# Relationships
	players = db.relationship('Player', backref='accounts')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<Account.{}>'.format(self.id)
