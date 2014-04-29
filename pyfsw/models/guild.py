from sqlalchemy import Column, Integer, String, ForeignKey
from pyfsw import db

class Guild(db.Model):
	__tablename__ = 'guilds'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	name = Column(String(255))
	ownerid = Column(Integer, ForeignKey('players.id'))
	creationdata = Column(Integer)
	motd = Column(String(255))

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<Guild.{}>'.format(self.id)
