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

	# Relationships
	owner = db.relationship('Player', foreign_keys='Guild.ownerid')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<Guild.{}>'.format(self.id)

class GuildInvite(db.Model):
	__tablename__ = 'guild_invites'

	# Standard columns
	player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
	guild_id = Column(Integer, ForeignKey('guilds.id'))

	# Relationships
	player = db.relationship('Player', foreign_keys='GuildInvite.player_id')
	guild = db.relationship('Guild', foreign_keys='GuildInvite.guild_id')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<GuildInvite.{}.{}>'.format(self.guild_id, self.player_id)

class GuildMembership(db.Model):
	__tablename__ = 'guild_membership'

	# Standard columns
	player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
	guild_id = Column(Integer, ForeignKey('guilds.id'))
	rank_id = Column(Integer, ForeignKey('guild_ranks.id'))
	nick = Column(String(15), default='')

	# Relationship
	player = db.relationship('Player', foreign_keys='GuildMembership.player_id')
	guild = db.relationship('Guild', foreign_keys='GuildMembership.guild_id')
	rank = db.relationship('GuildRank', foreign_keys='GuildMembership.rank_id')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<GuildMembership.{}.{}.{}>'.format(self.guild_id, self.player_id, self.rank_id)

class GuildRank(db.Model):
	__tablename__ = 'guild_ranks'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	guild_id = Column(Integer, ForeignKey('guilds.id'))
	name = Column(String(255))
	level = Column(Integer)

	# Relationship
	guild = db.relationship('Guild', foreign_keys='GuildRank.guild_id')

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<GuildRank.{}.{}.{}>'.format(self.guild_id, self.name, self.level)

class GuildWar(db.Model):
	__tablename__ = 'guild_wars'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	guild1 = Column(Integer)
	guild2 = Column(Integer)
	name1 = Column(String(255))
	name2 = Column(String(255))
	status = Column(Integer)
	started = Column(Integer)
	ended = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<GuildWar.{}.{}.{}>'.format(self.id, self.guild1, self.guild2)

class GuildWarKill(db.Model):
	__tablename__ = 'guildwar_kills'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	killer = Column(Integer)
	target = Column(Integer)
	killerguild = Column(Integer)
	targetguild = Column(Integer)
	warid = Column(Integer, ForeignKey('guild_wars.id'))
	time = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<GuildWarKill.{}.{}>'.format(self.id, self.warid)
