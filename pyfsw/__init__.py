from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.cache import Cache

from pyfsw.config import *

from functools import wraps
from os import path
from datetime import date
import inspect

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

BASE_PATH = path.dirname(inspect.getfile(inspect.currentframe()))
db = SQLAlchemy(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.before_request
def init_globals():
	g.server_name = SERVER_NAME
	g.server_description = SERVER_DESCR
	g.year = date.today().year
	g.admin_account_type = ADMIN_ACCOUNT_TYPE

from pyfsw.models.account import Account
from pyfsw.models.guild import Guild, GuildInvite, GuildMembership, GuildRank, GuildWar, GuildWarKill
from pyfsw.models.player import Player, PlayerItem, PlayerStorage, PlayerDeath, PlayerOnline
from pyfsw.models.house import House
from pyfsw.models.news import News
from pyfsw.models.forum import ForumCategory, ForumBoard, ForumThread, ForumPost
from pyfsw.models.library import Library
from pyfsw.models.shop import ShopCategory, ShopItem, ShopOrder, ShopHistory, PaypalHistory
from pyfsw.models.market import MarketOffer, MarketHistory

from pyfsw.filters import *
from pyfsw.helpers import *

from pyfsw.views import news, forum, account, community, community_guilds, library, shop
from pyfsw.views import error, captcha, outfit, paypal
from pyfsw.views.admin import dashboard, news, forum, community, shop
