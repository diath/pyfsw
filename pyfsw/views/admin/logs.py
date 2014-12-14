from flask import redirect, render_template, request, url_for, flash, session

from time import time

from sqlalchemy import func

from pyfsw import app, db
from pyfsw import admin_required, current_user
from pyfsw import Account, LoginHistory, PayPalHistory, ZayPayHistory

# Handle Login Logs
@app.route('/admin/logs/login')
@admin_required(5)
def route_admin_logs_login():
	history = LoginHistory.query.order_by(LoginHistory.time.desc()).limit(25).all()

	return render_template(
		'admin/logs/login.htm',
		history = history
	)

@app.route('/admin/logs/login/delete/<int:id>')
@admin_required(5)
def route_admin_logs_login_delete(id):
	history = LoginHistory.query.filter(LoginHistory.id == id).first()

	db.session().delete(history)
	db.session().commit()

	flash('The entry has been deleted.', 'success')

	return redirect(url_for('route_admin_logs_login'))

@app.route('/admin/logs/login/search', methods=['POST'])
@admin_required(5)
def route_admin_logs_login_search_post():
	name = request.form.get('name', '', type=str)
	ip = request.form.get('ipAddress', '', type=str)
	history = db.session().query(
		LoginHistory.id, LoginHistory.account, LoginHistory.ip, LoginHistory.platform, 
		LoginHistory.browser, LoginHistory.status, LoginHistory.time
	).order_by(LoginHistory.time.desc())

	if name != '':
		accountName = db.session().query(Account.name).filter(Account.name == name).first()
		if not accountName:
			flash('The account name you are trying to search for does not exist.', 'error')
			return redirect(url_for('route_admin_logs_login'))

		history = history.filter(LoginHistory.account == accountName[0]).all()

		if not history:
			flash('The is no login history for this account name.', 'error')
			return redirect(url_for('route_admin_logs_login'))
	elif ip != '':
		history = history.filter(LoginHistory.ip == ip).all()

		if not history:
			flash('The submitted IP address did not match any records.', 'error')
			return redirect(url_for('route_admin_logs_login'))
	else:
		flash('You must fill out one of the search forms.', 'error')

	return render_template(
		'admin/logs/login.htm',
		history = history
	)

@app.route('/admin/logs/login/search', methods=['GET'])
def route_admin_logs_login_search():
	return render_template('admin/logs/login.htm')

# Handle PayPal Logs
@app.route('/admin/logs/paypal')
@admin_required(5)
def route_admin_logs_paypal():
	history = PayPalHistory.query.order_by(PayPalHistory.timestamp.desc()).limit(10).all()

	return render_template(
		'admin/logs/paypal.htm',
		history = history
	)

@app.route('/admin/logs/paypal/sort/<int:duration>')
@admin_required(5)
def route_admin_logs_paypal_sort(duration):
	durationTime = int(time()) - (60 * 60 * 24 * duration)
	history = PayPalHistory.query.filter(PayPalHistory.timestamp > durationTime).all()
	durationTotal = db.session().query(func.sum(PayPalHistory.amount)).filter(PayPalHistory.timestamp > durationTime).first()

	if not len(history):
		flash('No donation records were found within the specified range.', 'error')
		return redirect(url_for('route_admin_logs_paypal'))

	flash('You have received {} {} in the past {} {}.'.format(
		len(history),
		'donations' if len(history) != 1 else 'donation',
		duration if duration != 1 else '',
		('days' if duration != 1 else 'day')
	), 'success')

	return render_template(
		'admin/logs/paypal.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/paypal/sort/all')
@admin_required(5)
def route_admin_logs_paypal_sort_all():
	history = PayPalHistory.query.order_by(PayPalHistory.timestamp.desc()).all()
	durationTotal = db.session().query(func.sum(PayPalHistory.amount)).first()
	flash('You have received {} donations total.'.format(len(history)), 'success')

	return render_template(
		'admin/logs/paypal.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/paypal/edit/<int:id>')
@admin_required(5)
def route_admin_logs_paypal_edit(id):
	history = PayPalHistory.query.filter(PayPalHistory.id == id).first()

	return render_template(
		'admin/logs/paypal_edit.htm',
		history = history
	)

@app.route('/admin/logs/paypal/edit/<int:id>', methods=['POST'])
@admin_required(5)
def route_admin_logs_paypal_edit_post(id):
	history = PayPalHistory.query.filter(PayPalHistory.id == id).first()

	account_id = request.form.get('accountID', 0)
	timestamp = request.form.get('timestamp', 0)
	amount = request.form.get('amount', 0)

	if int(timestamp) == 0:
		flash('Timestamp was not set. Current timestamp applied.', 'warning')
		timestamp = int(time())

	history.account_id = account_id
	history.timestamp = timestamp
	history.amount = amount

	db.session().commit()
	flash('The entry has been edited.', 'success')

	return redirect(url_for('route_admin_logs_paypal'))

@app.route('/admin/logs/paypal/delete/<int:id>')
@admin_required(5)
def route_admin_logs_paypal_delete(id):
	history = PayPalHistory.query.filter(PayPalHistory.id == id).first()

	db.session().delete(history)
	db.session().commit()

	flash('The entry has been deleted.', 'success')

	return redirect(url_for('route_admin_logs_paypal'))

# Handle ZayPay Logs
@app.route('/admin/logs/zaypay')
@admin_required(5)
def route_admin_logs_zaypay():
	history = ZayPayHistory.query.order_by(ZayPayHistory.timestamp.desc()).limit(10).all()

	return render_template(
		'admin/logs/zaypay.htm',
		history = history
	)

@app.route('/admin/logs/zaypay/sort/<int:duration>')
@admin_required(5)
def route_admin_logs_zaypay_sort(duration):
	durationTime = int(time()) - (60 * 60 * 24 * duration)
	history = ZayPayHistory.query.filter(ZayPayHistory.timestamp > durationTime).all()
	durationTotal = db.session().query(func.sum(ZayPayHistory.amount)).filter(ZayPayHistory.timestamp > durationTime).first()

	if not len(history):
		flash('No donation records were found within the specified range.', 'error')
		return redirect(url_for('route_admin_logs_zaypay'))

	flash('You have received {} {} in the past {} {}.'.format(
		len(history),
		'donations' if len(history) != 1 else 'donation',
		duration if duration != 1 else '',
		('days' if duration != 1 else 'day')
	), 'success')

	return render_template(
		'admin/logs/zaypay.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/zaypay/sort/all')
@admin_required(5)
def route_admin_logs_zaypay_sort_all():
	history = ZayPayHistory.query.order_by(ZayPayHistory.timestamp.desc()).all()
	durationTotal = db.session().query(func.sum(ZayPayHistory.amount)).first()
	flash('You have received {} donations total.'.format(len(history)), 'success')

	return render_template(
		'admin/logs/zaypay.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/zaypay/edit/<int:id>')
@admin_required(5)
def route_admin_logs_zaypay_edit(id):
	history = ZayPayHistory.query.filter(ZayPayHistory.id == id).first()

	return render_template(
		'admin/logs/zaypay_edit.htm',
		history = history
	)

@app.route('/admin/logs/zaypay/edit/<int:id>', methods=['POST'])
@admin_required(5)
def route_admin_logs_zaypay_edit_post(id):
	history = ZayPayHistory.query.filter(ZayPayHistory.id == id).first()

	account_id = request.form.get('accountID', 0)
	timestamp = request.form.get('timestamp', 0)
	amount = request.form.get('amount', 0)

	if int(timestamp) == 0:
		flash('Timestamp was not set. Current timestamp applied.', 'warning')
		timestamp = int(time())

	history.account_id = account_id
	history.timestamp = timestamp
	history.amount = amount

	db.session().commit()
	flash('The entry has been edited.', 'success')

	return redirect(url_for('route_admin_logs_zaypay'))

@app.route('/admin/logs/zaypay/delete/<int:id>')
@admin_required(5)
def route_admin_logs_zaypay_delete(id):
	history = ZayPayHistory.query.filter(ZayPayHistory.id == id).first()

	db.session().delete(history)
	db.session().commit()

	flash('The entry has been deleted.', 'success')

	return redirect(url_for('route_admin_logs_zaypay'))
