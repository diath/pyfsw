from sqlalchemy import Column, Integer, String, Text, ForeignKey
from pyfsw import db

class ForumCategory(db.Model):
	__tablename__ = 'forum_categories'

	# Standard columns
	id = Column(Integer, unique=True, primary_key=True)
	name = Column(String(64))

	# Relationships
	boards = db.relationship('ForumBoard', foreign_keys='ForumBoard.category_id')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<ForumCategory.{}>'.format(self.id)

class ForumBoard(db.Model):
	__tablename__ = 'forum_boards'

	# Standard columns
	id = Column(Integer, unique=True, primary_key=True)
	name = Column(String(32))
	description = Column(Text)
	category_id = Column(Integer, ForeignKey('forum_categories.id'))
	locked = Column(Integer, default=0)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<ForumBoard.{}>'.format(self.id)

class ForumThread(db.Model):
	__tablename__ = 'forum_threads'

	# Standard column
	id = Column(Integer, primary_key=True, unique=True)
	subject = Column(String(64))
	timestamp = Column(Integer)
	board_id = Column(Integer, ForeignKey('forum_boards.id'))
	locked = Column(Integer, default=0)
	pinned = Column(Integer, default=0)
	lastpost = Column(Integer, default=0)
	author_id = Column(Integer)
	content = Column(Text)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<ForumThread.{}>'.format(self.id)

class ForumPost(db.Model):
	__tablename__ = 'forum_posts'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	author_id = Column(Integer)
	content = Column(Text)
	timestamp = Column(Integer)
	thread_id = Column(Integer, ForeignKey('forum_threads.id'))

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<ForumPost.{}>'.format(self.id)
