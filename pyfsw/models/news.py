from sqlalchemy import Column, Integer, String, Text, ForeignKey

from pyfsw import db
from pyfsw import Player

class News(db.Model):
	__tablename__ = 'news'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	timestamp = Column(Integer)
	header = Column(String(64))
	content = Column(Text)
	author_id = Column(Integer, ForeignKey(Player.id))

	# Relationships
	author = db.relationship('Player', foreign_keys='News.author_id')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<News.{}>'.format(self.id)
