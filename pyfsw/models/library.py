from sqlalchemy import Column, Integer, String, Text
from pyfsw import db

class Library(db.Model):
	__tablename__ = 'library'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	uri = Column(String(32), unique=True)
	name = Column(String(32))
	enabled = Column(Integer, default=1)
	content = Column(Text)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<Library.{}.{}>'.format(self.id, self.uri)
