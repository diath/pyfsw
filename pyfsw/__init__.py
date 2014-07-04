from flask import Flask, render_template, redirect, url_for, jsonify, request, current_app, g, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

from pyfsw.config import *

from datetime import date, datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

if DEBUG:
	app.debug = DEBUG
	app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

	if DEBUG_PROFILER:
		app.config['DEBUG_TB_PROFILER_ENABLED'] = True

	DebugToolbarExtension(app)

db = SQLAlchemy(app)

@app.before_request
def init_globals():
	g.year = date.today().year

@app.template_filter('datetime')
def filter_datetime(value):
	return datetime.fromtimestamp(int(value)).strftime(DATE_FORMAT)

@app.template_filter('timetotal')
def filter_timetotal(value):
	value = int(value)

	hour = value / 3600
	rem = value % 3600
	minute = rem / 60
	second = rem % 60

	return '{:02d} hours, {:02d} minutes and {:02d} seconds'.format(int(hour), int(minute), int(second))

@app.template_filter('gender')
def filter_gender(value):
	return GENDERS[value]

@app.template_filter('vocation')
def filter_vocation(value):
	return VOCATIONS[value]

@app.template_filter('town')
def filter_town(value):
	return TOWNS[value]

@app.template_filter('rank')
def filter_rank(value):
	if value == 3:
		return 'The Leader'
	elif value == 2:
		return 'Vice Leader'

	return 'Member'

@app.errorhandler(403)
def error_forbidden(error):
	return render_template('error.htm', error=403,
		message='Access to the resource you are trying to reach is forbidden.'), 403

@app.errorhandler(404)
def error_not_found(error):
	return render_template('error.htm', error=404,
		message='The page you are trying to reach has not been found.'), 404

@app.errorhandler(500)
def error_internal(error):
	return render_template('error.htm', error=500,
		message='Internal server error, please contact the administrator.'), 500

def login_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if 'account' not in session:
			return redirect(url_for('route_account_login', next=request.path))

		return f(*args, **kwargs)

	return decorated

def current_user():
	if 'account' in session:
		return db.session().query(Account).filter(Account.id == session['account']).first()

	return None

def get_library():
	liblist = []
	library = db.session().query(Library).all()

	for lib in library:
		liblist.append({'uri': lib.uri, 'name': lib.name})

	return liblist

def is_guild_leader(id):
	user = current_user()
	if not user:
		return False

	guild = db.session().query(Guild.ownerid).filter(Guild.id == id).first()
	if not guild:
		return False

	owner = guild[0]
	found = False

	for player in user.players:
		if player.id == owner:
			found = True
			break

	return found

app.jinja_env.globals.update(get_library=get_library)

from pyfsw.models.account import Account
from pyfsw.models.guild import Guild, GuildInvite, GuildMembership, GuildRank, GuildWar, GuildWarKill
from pyfsw.models.player import Player, PlayerStorage, PlayerDeath, PlayerOnline
from pyfsw.models.house import House
from pyfsw.models.news import News
from pyfsw.models.library import Library
from pyfsw.models.shop import ShopCategory, ShopItem, ShopOrder, ShopHistory
from pyfsw.models.market import MarketOffer, MarketHistory

from pyfsw.views import news, account, community, community_guilds, library, shop
from pyfsw.views import paypal
