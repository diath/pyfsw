from flask import render_template, request

import socket
from time import time

from pyfsw import app, db
from pyfsw import login_required, current_user
from pyfsw import Account, PayPalHistory
from pyfsw import PAYPAL_BUTTONS

@app.route('/paypal/donate')
@login_required
def route_paypal():
	return render_template(
		'paypal/donate.htm',
		buttons=PAYPAL_BUTTONS, account_id=current_user().id
	)

@app.route('/paypal/success')
def route_paypal_donated():
	return render_template('paypal/donated.htm')

@app.route('/paypal/canceled')
def route_paypal_canceled():
	return render_template('paypal/canceled.htm')

@app.route('/paypal/ipn', methods=['POST'])
def route_paypal_ipn():
	error = False

	host = socket.getfqdn(request.remote_addr)
	if host not in ['notify.paypal.com', 'localhost', 'localhost.localdomain']:
		error = True

	test = request.form.get('test_ipn', 0, type=int)
	if test != 0:
		error = True

	status = request.form.get('payment_status', '', type=str)
	if status != 'Completed':
		error = True

	currency = request.form.get('mc_currency', '', type=str)
	if currency != 'USD':
		error = True

	account_id = request.form.get('custom', 0, type=int)
	account = db.session().query(Account).filter(Account.id == account_id).first()
	if not account:
		error = True

	amount = request.form.get('mc_gross', '', type=str)
	button = None
	for v in PAYPAL_BUTTONS:
		if v.get('amount', '0.00') == amount:
			button = v
			break

	if not button:
		button = {'amount': '0.00', 'points': 0}

	if not error:
		account.points += button.get('points', 0)
		db.session().commit()

	history = PayPalHistory()
	history.account_id = account_id
	history.timestamp = int(time())
	history.status = status
	history.test = test
	history.origin = host
	history.amount = button.get('amount', 0)
	history.points = button.get('points', 0)

	db.session().add(history)
	db.session().commit()

	return '', 200
