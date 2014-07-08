from flask import redirect, render_template, request, url_for, flash, get_flashed_messages, session
from hashlib import sha1
from time import time
import random, string, re

from pyfsw import app, db
from pyfsw import Account, Player
from pyfsw import login_required, current_user
from pyfsw import NEW_CHARACTER

@app.route('/account/login', methods=['GET'])
def route_account_login():
	next = request.args.get('next')
	if next:
		return render_template('account/login.htm', next=next)

	return render_template('account/login.htm')

@app.route('/account/login', methods=['POST'])
def route_account_login_post():
	name = request.form.get('name', '', type=str)
	pswd = request.form.get('pswd', '', type=str)

	if len(pswd):
		hash = sha1()
		hash.update(pswd.encode('utf-8'))
		pswd = hash.hexdigest()

	account = db.session().query(Account.id).filter(Account.name == name).filter(Account.password == pswd).first()
	if account is None:
		return render_template('account/login.htm', error=True)

	session['account'] = account.id

	if 'next' in request.form:
		return redirect(request.form['next'])

	return redirect(url_for('route_account_manage'))

@app.route('/account/logout')
def route_account_logout():
	session.pop('account')
	return redirect(url_for('route_account_login'))

@app.route('/account/create', methods=['GET'])
def route_account_create():
	return render_template('account/create.htm')

@app.route('/account/create', methods=['POST'])
def route_account_create_post():
	name = request.form.get('name', '', type=str)
	pswd = request.form.get('pswd', '', type=str)
	mail = request.form.get('mail', '', type=str)
	pswdRepeat = request.form.get('pswdRepeat', '', type=str)
	captcha = request.form.get('captcha', '', type=str)

	if len(name) < 4 or len(name) > 32:
		flash('The account name length must be between 4 and 32 characters.')

	if len(pswd) < 5:
		flash('The password must be at least 5 characters long.')

	if pswd != pswdRepeat:
		flash('The passwords do not match.')

	if len(mail) < 6:
		flash('The specified e-mail address is not valid.')

	account = db.session().query(Account.id).filter(Account.name == name).first()
	if account:
		flash('The account name is already in use.')

	if captcha != session.get('captcha', ''):
		flash('The captcha code does not match.')

	if len(get_flashed_messages()) > 0:
		return render_template('account/create.htm')

	hash = sha1()
	hash.update(pswd.encode('utf-8'))
	pswd = hash.hexdigest()

	account = Account()
	account.name = name
	account.password = pswd
	account.email = mail
	account.creation = int(time())

	db.session().add(account)
	db.session().commit()

	return render_template('account/login.htm', created=True)

@app.route('/account/manage')
@login_required
def route_account_manage():
	return render_template('account/manage.htm', account=current_user())

@app.route('/account/password', methods=['GET'])
@login_required
def route_account_password():
	return render_template('account/password.htm')

@app.route('/account/password', methods=['POST'])
@login_required
def route_account_password_post():
	pswd = request.form.get('pswd', '', type=str)
	pswdNew = request.form.get('pswdNew', '', type=str)
	pswdRepeat = request.form.get('pswdRepeat', '', type=str)

	hash = sha1()
	hash.update(pswd.encode('utf-8'))
	pswd = hash.hexdigest()

	if current_user().password != pswd:
		flash('The current password is not correct.')

	if len(pswdNew) < 5:
		flash('The new password must be at least 5 characters long.')

	if pswdNew != pswdRepeat:
		flash('The new passwords do not match.')

	if len(get_flashed_messages()) > 0:
		return render_template('account/password.htm')

	hash = sha1()
	hash.update(pswdNew.encode('utf-8'))
	newPswd = hash.hexdigest()

	current_user().password = newPswd
	db.session().commit()

	return redirect(url_for('route_account_manage'))

@app.route('/account/key')
@login_required
def route_account_key():
	account = current_user()
	if not account or account.key != '':
		return redirect(url_for('route_account_manage'))

	parts = []
	for i in range(4):
		parts.append(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)))

	key = '-'.join(parts)

	account.key = key
	db.session().commit()

	return render_template('account/key.htm', key=key)

@app.route('/account/edit/<int:id>', methods=['GET'])
@login_required
def route_account_edit(id):
	account = current_user()
	player = db.session().query(Player.id, Player.comment, Player.account_id).filter(Player.id == id).first()
	if not account or not player or account.id != player.account_id:
		return redirect(url_for('route_account_manage'))

	return render_template('account/character_edit.htm', player=player)

@app.route('/account/edit/<int:id>', methods=['POST'])
@login_required
def route_account_edit_post(id):
	account = current_user()
	player = db.session().query(Player).filter(Player.id == id).first()
	if not account or not player or account.id != player.account_id:
		return redirect(url_for('route_account_manage'))

	player.comment = request.form.get('comment', '', type=str)
	db.session().commit()

	return render_template('account/manage.htm', account=current_user(), success='The character comment has been updated.')

@app.route('/account/delete/<int:id>', methods=['GET'])
@login_required
def route_account_delete(id):
	account = current_user()
	player = db.session().query(Player.id, Player.account_id).filter(Player.id == id).first()
	if not account or not player or account.id != player.account_id:
		return redirect(url_for('route_account_manage'))

	return render_template('account/character_delete.htm', player=player)

@app.route('/account/delete/<int:id>', methods=['POST'])
@login_required
def route_account_delete_post(id):
	account = current_user()
	player = db.session().query(Player).filter(Player.id == id).first()
	if account and player and account.id == player.account_id:
		db.session().delete(player)
		db.session().commit()

	return render_template('account/manage.htm', account=current_user(), success='The character has been deleted.')

@app.route('/account/character')
@login_required
def route_account_character():
	return render_template(
		'account/character.htm', genders=NEW_CHARACTER.get('genders'),
		vocations=NEW_CHARACTER.get('vocations'), towns=NEW_CHARACTER.get('towns')
	)

@app.route('/account/character', methods=['POST'])
@login_required
def route_account_character_post():
	name = request.form.get('name', '', type=str)
	gender = request.form.get('gender', 0, type=int)
	vocation = request.form.get('vocation', 0, type=int)
	town = request.form.get('town', 1, type=int)

	if len(name) < 4:
		flash('The name must be at least 4 characters long.')

	if re.compile('^[a-zA-Z]$').search(name):
		flash('The name may only contain latin characters (A-Z, a-z).')

	if len(name.split(' ')) > 3:
		flash('The name may only consist of 3 words.')

	if gender not in NEW_CHARACTER.get('genders'):
		flash('The selected gender is not valid.')

	if vocation not in NEW_CHARACTER.get('vocations'):
		flash('The selected vocation is not valid.')

	if town not in NEW_CHARACTER.get('towns'):
		flash('The selected town is not valid.')

	name = string.capwords(name)
	player = db.session().query(Player.id).filter(Player.name == name).first()
	if player:
		flash('The character name is already in use.')

	if len(get_flashed_messages()) > 0:
		return render_template(
			'account/character.htm', genders=NEW_CHARACTER.get('genders'),
			vocations=NEW_CHARACTER.get('vocations'), towns=NEW_CHARACTER.get('towns')
		)

	player = Player()
	player.name = name
	player.sex = gender
	player.vocation = vocation
	player.town_id = town
	player.account_id = current_user().id

	player.looktype = 136 if gender == 0 else 128
	player.lookhead = NEW_CHARACTER.get('outfit')[0]
	player.lookbody = NEW_CHARACTER.get('outfit')[1]
	player.looklegs = NEW_CHARACTER.get('outfit')[2]
	player.lookfeet = NEW_CHARACTER.get('outfit')[3]

	db.session().add(player)
	db.session().commit()

	return render_template('account/manage.htm', account=current_user(), success='The character has been created.')

@app.route('/account/recover', methods=['GET'])
def route_account_recover():
	return render_template('account/recover.htm')

@app.route('/account/recover', methods=['POST'])
def route_account_recover_post():
	name = request.form.get('name', '', type=str)
	key = request.form.get('key', '', type=str)
	pswd = request.form.get('pswd', '', type=str)
	pswdRepeat = request.form.get('pswdRepeat', '', type=str)

	if len(name) < 4 or len(name) > 32:
		flash('Invalid account name specified.')

	if len(pswd) < 5:
		flash('The new password must be at least 5 characters long.')

	if pswd != pswdRepeat:
		flash('The passwords do not match.')

	account = db.session().query(Account).filter(Account.name == name).filter(Account.key == key).first()
	if not account:
		flash('Invalid recovery key specified.')
	else:
		hash = sha1()
		hash.update(pswd.encode('utf-8'))
		pswd = hash.hexdigest()

		account.password = pswd
		account.key = ''

		db.session().commit()

		flash('The password for the account has been changed.')

	return redirect(url_for('route_account_recover'))
