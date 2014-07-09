from sqlalchemy import Binary, Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import backref

from pyfsw import db
from pyfsw import Guild, GuildMembership

class Player(db.Model):
	__tablename__ = 'players'

	# Standard columns
	id = Column(Integer, primary_key=True, unique=True)
	name = Column(String(255), unique=True)
	group_id = Column(Integer, default=1)
	account_id = Column(Integer, ForeignKey('accounts.id'))
	level = Column(Integer, default=8)
	vocation = Column(Integer, default=0)
	health = Column(Integer, default=185)
	healthmax = Column(Integer, default=185)
	experience = Column(BigInteger, default=4200)
	lookbody = Column(Integer, default=0)
	lookfeet = Column(Integer, default=0)
	lookhead = Column(Integer, default=0)
	looklegs = Column(Integer, default=0)
	looktype = Column(Integer, default=136)
	lookaddons = Column(Integer, default=0)
	maglevel = Column(Integer, default=0)
	mana = Column(Integer, default=35)
	manamax = Column(Integer, default=35)
	manaspent = Column(Integer, default=0)
	soul = Column(Integer, default=100)
	town_id = Column(Integer, default=1)
	posx = Column(Integer, default=0)
	posy = Column(Integer, default=0)
	posz = Column(Integer, default=0)
	conditions = Column(Binary, default='')
	cap = Column(Integer, default=500)
	sex = Column(Integer, default=0)
	lastlogin = Column(BigInteger, default=0)
	lastip = Column(Integer, default=0)
	save = Column(Integer, default=1)
	skull = Column(Integer, default=0)
	skulltime = Column(Integer, default=0)
	lastlogout = Column(BigInteger, default=0)
	blessings = Column(Integer, default=0)
	onlinetime = Column(Integer, default=0)
	deletion = Column(BigInteger, default=0)
	balance = Column(BigInteger, default=0)
	offlinetraining_time = Column(Integer, default=43200)
	offlinetraining_skill = Column(Integer, default=-1)
	stamina = Column(Integer, default=2520)
	skill_fist = Column(Integer, default=10)
	skill_fist_tries = Column(Integer, default=0)
	skill_club = Column(Integer, default=10)
	skill_club_tries = Column(Integer, default=0)
	skill_sword = Column(Integer, default=10)
	skill_sword_tries = Column(Integer, default=0)
	skill_axe = Column(Integer, default=10)
	skill_axe_tries = Column(Integer, default=0)
	skill_dist = Column(Integer, default=10)
	skill_dist_tries = Column(Integer, default=0)
	skill_shielding = Column(Integer, default=10)
	skill_shielding_tries = Column(Integer, default=0)
	skill_fishing = Column(Integer, default=10)
	skill_fishing_tries = Column(Integer, default=10)

	# Custom columns
	comment = Column(String(255), default='')

	# Relationships
	storages = db.relationship('PlayerStorage', primaryjoin='Player.id == PlayerStorage.player_id', backref='players', passive_deletes=True)

	# Misc
	guild = None

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<Player.{}>'.format(self.id)

	def getStorageValue(self, key):
		for storage in self.storages:
			if storage.key == key:
				return storage.value

		return -1

	def getGuild(self):
		if self.guild:
			return self.guild

		membership = db.session().query(GuildMembership.guild_id).filter(GuildMembership.player_id == self.id).first()
		if not membership:
			return None

		guild = Guild.query.filter(Guild.id == membership.guild_id).first()
		if not guild:
			return None

		self.guild = guild
		self.membership = membership

		return self.guild

class PlayerItem(db.Model):
	__tablename__ = 'player_items'

	# Standard columns
	player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
	pid = Column(Integer, primary_key=True)
	sid = Column(Integer)
	itemtype = Column(Integer)
	count = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<PlayerItem.{}.{}>'.format(self.player_id, self.pid)

class PlayerStorage(db.Model):
	__tablename__ = 'player_storage'

	# Standard columns
	player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
	key = Column(Integer, primary_key=True)
	value = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<PlayerStorage.{}.{}.{}>'.format(self.player_id, self.key, self.value)

class PlayerDeath(db.Model):
	__tablename__ = 'player_deaths'

	# Standard columns
	player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
	time = Column(BigInteger)
	level = Column(Integer)
	killed_by = Column(String(255), primary_key=True)
	is_player = Column(Integer)
	mostdamage_by = Column(String(100), primary_key=True)
	mostdamage_is_player = Column(Integer)
	unjustified = Column(Integer)
	mostdamage_unjustified = Column(Integer)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<PlayerDeath.{}>'.format(self.player_id)

	def toString(self, lower=False):
		if lower:
			ret = 'died at level {} to '.format(self.level)
		else:
			ret = 'Died at level {} to '.format(self.level)

		if self.is_player:
			ret += '<a href="/community/player/{}">{}</a>'.format(self.killed_by, self.killed_by)
		else:
			ret += '{}'.format(self.killed_by)

		if self.mostdamage_by != '' and self.mostdamage_by != self.killed_by:
			if self.mostdamage_is_player:
				ret += ' and <a href="/community/player/{}">{}</a>'.format(self.mostdamage_by, self.mostdamage_by)
			else:
				ret += ' and {}'.format(self.mostdamage_by)

		ret += '.'
		return ret

class PlayerOnline(db.Model):
	__tablename__ = 'players_online'

	# Standard columns
	player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)

	# Methods
	def __init__(self):
		pass

	def __repr__(self):
		return '<PlayerOnline.{}>'.format(self.player_id)
