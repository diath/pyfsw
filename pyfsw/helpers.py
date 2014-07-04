from flask import redirect, url_for, session
from functools import wraps

from pyfsw import app, db
from pyfsw import Account, Library, Guild

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
