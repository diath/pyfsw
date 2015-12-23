from flask import redirect, render_template, request, url_for, flash, session
from hashlib import sha1
from time import time
import random, string, re

from pyfsw import app, db
from pyfsw import Account, Player, LoginHistory
from pyfsw import login_required, current_user, check_captcha
from pyfsw import CAPTCHA_SITE_KEY, NEW_CHARACTER, DELETION_DELAY

CHAR_NAME_EXPR = re.compile('^([a-zA-Z ]+)$')

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

	history = LoginHistory()
	history.account = name
	history.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	history.platform = request.user_agent.platform
	history.browser = request.user_agent.browser
	history.time = int(time())

	account = db.session().query(Account.id, Account.type, Account.web_access, Account.creation).filter(Account.name == name).filter(Account.password == pswd).first()
	if not account:
		history.status = 0
		db.session().add(history)
		db.session().commit()

		return render_template('account/login.htm', error=True)

	session['account'] = account.id
	session['access'] = account.type
	session['web_access'] = account.web_access

	history.status = 1
	db.session().add(history)
	db.session().commit()

	if 'next' in request.form:
		return redirect(request.form['next'])

	return redirect(url_for('route_account_manage'))

@app.route('/account/logout')
@login_required
def route_account_logout():
	session.pop('account')
	session.pop('access')
	session.pop('web_access')

	return redirect(url_for('route_account_login'))

@app.route('/account/create', methods=['GET'])
def route_account_create():
	return render_template(
		'account/create.htm', name=request.args.get('name', ''),
		mail=request.args.get('mail', ''), site_key=CAPTCHA_SITE_KEY
	)

@app.route('/account/create', methods=['POST'])
def route_account_create_post():
	name = request.form.get('name', '', type=str)
	pswd = request.form.get('pswd', '', type=str)
	mail = request.form.get('mail', '', type=str)
	pswdRepeat = request.form.get('pswdRepeat', '', type=str)
	captcha = request.form.get('g-recaptcha-response')
	error = False

	if len(name) < 4 or len(name) > 32:
		flash('The account name length must be between 4 and 32 characters.', 'error')
		error = True

	if len(pswd) < 5:
		flash('The password must be at least 5 characters long.', 'error')
		error = True

	if pswd != pswdRepeat:
		flash('The passwords do not match.', 'error')
		error = True

	if len(mail) < 6:
		flash('The specified e-mail address is not valid.', 'error')
		error = True

	account = db.session().query(Account.id).filter(Account.name == name).first()
	if account:
		flash('The account name is already in use.', 'error')
		error = True

	if check_captcha(captcha) is False:
		flash('You have failed the human verification', 'error')
		error = True

	if error:
		return redirect(url_for('route_account_create', name=name, mail=mail))

	hash = sha1()
	hash.update(pswd.encode('utf-8'))
	pswd = hash.hexdigest()

	account = Account()
	account.name = name
	account.password = pswd
	account.email = mail
	account.creation = int(time())
	account.key = ''

	db.session().add(account)
	db.session().commit()

	session['account'] = account.id
	session['access'] = account.type
	session['web_access'] = account.web_access

	flash('The account has been created. You can create a character now.', 'success')
	return redirect(url_for('route_account_manage'))

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
	user = current_user()
	error = False

	hash = sha1()
	hash.update(pswd.encode('utf-8'))
	pswd = hash.hexdigest()

	if user.password != pswd:
		flash('The current password is not correct.', 'error')
		error = True

	if len(pswdNew) < 5:
		flash('The new password must be at least 5 characters long.', 'error')
		error = True

	if pswdNew == user.password:
		flash('The new password must be different than the current one.', 'error')
		error = True

	if pswdNew != pswdRepeat:
		flash('The new passwords do not match.', 'error')
		error = True

	if error:
		return redirect(url_for('route_account_password'))

	hash = sha1()
	hash.update(pswdNew.encode('utf-8'))
	newPswd = hash.hexdigest()

	user.password = newPswd
	db.session().commit()

	flash('The password has been changed.', 'success')

	return redirect(url_for('route_account_manage'))

@app.route('/account/key')
@login_required
def route_account_key():
	user = current_user()
	if user.key != '':
		return redirect(url_for('route_account_manage'))

	parts = []
	for i in range(4):
		parts.append(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)))

	key = '-'.join(parts)

	user.key = key
	db.session().commit()

	return render_template('account/key.htm', key=key)

@app.route('/account/edit/<int:id>', methods=['GET'])
@login_required
def route_account_edit(id):
	account = current_user()
	player = db.session().query(Player.account_id, Player.comment).filter(Player.id == id).first()
	if not account or not player or account.id != player.account_id:
		return redirect(url_for('route_account_manage'))

	return render_template('account/character_edit.htm', id=id, comment=player.comment)

@app.route('/account/edit/<int:id>', methods=['POST'])
@login_required
def route_account_edit_post(id):
	account = current_user()
	player = db.session().query(Player).filter(Player.id == id).first()
	if player and account.id == player.account_id:
		player.comment = request.form.get('comment', '', type=str)
		db.session().commit()

		flash('The character comment has been updated.', 'success')
	else:
		flash('You cannot edit the comment of a character that does not belong to you.', 'error')

	return redirect(url_for('route_account_manage'))

@app.route('/account/signature/<int:id>', methods=['GET'])
@login_required
def route_account_signature(id):
	account = current_user()
	player = db.session().query(Player.account_id, Player.signature).filter(Player.id == id).first()
	if not account or not player or account.id != player.account_id:
		return redirect(url_for('route_account_manage'))

	return render_template(
		'account/character_signature.htm',
		id = id, signature = player.signature
	)

@app.route('/account/signature/<int:id>', methods=['POST'])
@login_required
def route_account_signature_post(id):
	account = current_user()
	player = Player.query.filter(Player.id == id).first()
	if player and account.id == player.account_id:
		signature = request.form.get('signature', '', type=str)

		# Strip the signature
		signature = signature.strip()

		# Strip consecutive spaces
		signature = ' '.join(signature.split())

		# Make sure that len(signature) <= 255
		signature = signature[:254]

		player.signature = signature
		db.session().commit()

		flash('The character signature has been updated.', 'success')
	else:
		flash('You cannot edit the signature of a character that does not belong to you.', 'error')

	return redirect(url_for('route_account_manage'))

@app.route('/account/delete/<int:id>', methods=['GET'])
@login_required
def route_account_delete(id):
	account = current_user()
	player = db.session().query(Player.account_id, Player.name).filter(Player.id == id).first()
	if not player or account.id != player.account_id:
		return redirect(url_for('route_account_manage'))

	return render_template('account/character_delete.htm', id=id, name=player.name)

@app.route('/account/delete/<int:id>', methods=['POST'])
@login_required
def route_account_delete_post(id):
	account = current_user()
	player = db.session().query(Player).filter(Player.id == id).first()
	if player and account.id == player.account_id:
		player.deletion = int(time()) + (DELETION_DELAY * 86400)
		db.session().commit()

		flash('The character has been scheduled for deletion.', 'success')
	else:
		flash('You cannot delete a character that does not belong to you.', 'error')

	return redirect(url_for('route_account_manage'))

@app.route('/account/restore/<int:id>', methods=['GET'])
@login_required
def route_account_restore(id):
	account = current_user()
	player = db.session().query(Player.account_id, Player.name).filter(Player.id == id).first()
	if not player or account.id != player.account_id:
		return redirect(url_for('route_account_manage'))

	return render_template('account/character_restore.htm', id=id, name=player.name)

@app.route('/account/restore/<int:id>', methods=['POST'])
@login_required
def route_account_restore_post(id):
	account = current_user()
	player = db.session().query(Player).filter(Player.id == id).first()
	if player and account.id == player.account_id:
		player.deletion = 0
		db.session().commit()

		flash('The character has been restored.', 'success')
	else:
		flash('You cannot restore a character that does not belong to you.', 'error')

	return redirect(url_for('route_account_manage'))

@app.route('/account/hide/<int:id>', methods=['GET'])
@login_required
def route_account_hide(id):
	account = current_user()
	player = db.session().query(Player).filter(Player.id == id).first()
	if player and account.id == player.account_id:
		player.hidden = 1
		db.session().commit()

		flash('The characted is now hidden.', 'success')
	else:
		flash('You cannot hide a character that does not belong to you.', 'error')

	return redirect(url_for('route_account_manage'))

@app.route('/account/show/<int:id>', methods=['GET'])
@login_required
def route_account_show(id):
	account = current_user()
	player = db.session().query(Player).filter(Player.id == id).first()
	if player and account.id == player.account_id:
		player.hidden = 0
		db.session().commit()

		flash('The characted is no longer hidden.', 'success')
	else:
		flash('You cannot show a character that does not belong to you.', 'error')

	return redirect(url_for('route_account_manage'))

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
	error = False

	if len(name) < 4:
		flash('The name must be at least 4 characters long.', 'error')
		error = True

	if not CHAR_NAME_EXPR.match(name):
		flash('The name may only contain latin characters (A-Z, a-z and spaces).', 'error')
		error = True

	if len(name.split(' ')) > 3:
		flash('The name may only consist of 3 words.', 'error')
		error = True

	if gender not in NEW_CHARACTER.get('genders'):
		flash('The selected gender is not valid.', 'error')
		error = True

	if vocation not in NEW_CHARACTER.get('vocations'):
		flash('The selected vocation is not valid.', 'error')
		error = True

	if town not in NEW_CHARACTER.get('towns'):
		flash('The selected town is not valid.', 'error')
		error = True

	name = string.capwords(name)
	player = db.session().query(Player.id).filter(Player.name == name).first()
	if player:
		flash('The character name is already in use.', 'error')
		error = True

	if error:
		return redirect(url_for('route_account_character'))

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

	flash('The character has been created.', 'success')

	return redirect(url_for('route_account_manage'))

@app.route('/account/recover', methods=['GET'])
def route_account_recover():
	return render_template('account/recover.htm')

@app.route('/account/recover', methods=['POST'])
def route_account_recover_post():
	name = request.form.get('name', '', type=str)
	key = request.form.get('key', '', type=str)
	pswd = request.form.get('pswd', '', type=str)
	pswdRepeat = request.form.get('pswdRepeat', '', type=str)
	error = False

	if len(name) < 4 or len(name) > 32:
		flash('Invalid account name specified.', 'error')
		error = True

	if len(pswd) < 5:
		flash('The new password must be at least 5 characters long.', 'error')
		error = True

	if pswd != pswdRepeat:
		flash('The passwords do not match.', 'error')
		error = True

	account = db.session().query(Account).filter(Account.name == name).filter(Account.key == key).first()
	if not account:
		flash('Invalid recovery key specified.', 'error')
		error = True
	elif account and not error:
		hash = sha1()
		hash.update(pswd.encode('utf-8'))
		pswd = hash.hexdigest()

		account.password = pswd
		account.key = ''

		db.session().commit()

		flash('The password for the account has been changed.', 'success')

	return redirect(url_for('route_account_recover'))
