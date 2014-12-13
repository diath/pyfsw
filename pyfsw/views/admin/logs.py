from flask import redirect, render_template, request, url_for, flash, session

from time import time

from sqlalchemy import func

from pyfsw import app, db
from pyfsw import admin_required, current_user
from pyfsw import Account, LoginHistory, PayPalHistory, ZayPayHistory
from pyfsw import is_number

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
	)

	if name != '':
		accountName = db.session().query(Account.name).filter(Account.name == name).first()
		if not accountName:
			flash('The account name you are trying to search for does not exist.', 'error')
			return redirect(url_for('route_admin_logs_login'))

		history = history.order_by(LoginHistory.time.desc()).filter(LoginHistory.account == accountName[0]).all()

		if not history:
			flash('The is no login history for this account name.', 'error')
			return redirect(url_for('route_admin_logs_login'))
	elif ip != '':
		history = history.order_by(LoginHistory.time.desc()).filter(LoginHistory.ip == ip).all()

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

@app.route('/admin/logs/paypal/sort/today')
@admin_required(5)
def route_admin_logs_paypal_sort_today():
	day = int(time()) - (60 * 60 * 24)
	history = PayPalHistory.query.filter(PayPalHistory.timestamp > day).all()
	durationTotal = db.session().query(func.sum(PayPalHistory.amount)).filter(PayPalHistory.timestamp > day).first()

	return render_template(
		'admin/logs/paypal.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/paypal/sort/week')
@admin_required(5)
def route_admin_logs_paypal_sort_week():
	week = int(time()) - (60 * 60 * 24 * 7)
	history = PayPalHistory.query.filter(PayPalHistory.timestamp > week).all()
	durationTotal = db.session().query(func.sum(PayPalHistory.amount)).filter(PayPalHistory.timestamp > week).first()

	return render_template(
		'admin/logs/paypal.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/paypal/sort/month')
@admin_required(5)
def route_admin_logs_paypal_sort_month():
	month = int(time()) - (60 * 60 * 24 * 7 * 30)
	history = PayPalHistory.query.filter(PayPalHistory.timestamp > month).all()
	durationTotal = db.session().query(func.sum(PayPalHistory.amount)).filter(PayPalHistory.timestamp > month).first()

	return render_template(
		'admin/logs/paypal.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/paypal/sort/all')
@admin_required(5)
def route_admin_logs_paypal_sort_all():
	history = PayPalHistory.query.order_by(PayPalHistory.timestamp.desc()).all()
	durationTotal = db.session().query(func.sum(PayPalHistory.amount)).first()

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

@app.route('/admin/logs/zaypay/sort/today')
@admin_required(5)
def route_admin_logs_zaypay_sort_today():
	day = int(time()) - (60 * 60 * 24)
	history = ZayPayHistory.query.filter(ZayPayHistory.timestamp > day).all()
	durationTotal = db.session().query(func.sum(ZayPayHistory.amount)).filter(ZayPayHistory.timestamp > day).first()

	return render_template(
		'admin/logs/zaypay.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/zaypay/sort/week')
@admin_required(5)
def route_admin_logs_zaypay_sort_week():
	week = int(time()) - (60 * 60 * 24 * 7)
	history = ZayPayHistory.query.filter(ZayPayHistory.timestamp > week).all()
	durationTotal = db.session().query(func.sum(ZayPayHistory.amount)).filter(ZayPayHistory.timestamp > week).first()

	return render_template(
		'admin/logs/zaypay.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/zaypay/sort/month')
@admin_required(5)
def route_admin_logs_zaypay_sort_month():
	month = int(time()) - (60 * 60 * 24 * 7 * 30)
	history = ZayPayHistory.query.filter(ZayPayHistory.timestamp > month).all()
	durationTotal = db.session().query(func.sum(ZayPayHistory.amount)).filter(ZayPayHistory.timestamp > month).first()

	return render_template(
		'admin/logs/zaypay.htm',
		history = history, durationTotal = durationTotal
	)

@app.route('/admin/logs/zaypay/sort/all')
@admin_required(5)
def route_admin_logs_zaypay_sort_all():
	history = ZayPayHistory.query.order_by(ZayPayHistory.timestamp.desc()).all()
	durationTotal = db.session().query(func.sum(ZayPayHistory.amount)).first()

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
