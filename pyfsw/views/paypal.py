from flask import render_template

from pyfsw import app, db
from pyfsw import login_required, current_user

import http.client
import socket

@app.route('/paypal/donate')
@login_required
def route_paypal():
	return render_template('paypal/donate.htm')

@app.route('/paypal/donated')
def route_paypal_donated():
	return render_template('paypal/donated.htm')

@app.route('/paypal/reversed')
def route_paypal_reversed():
	return render_template('paypal/reversed.htm')

@app.route('/paypal/ipn')
def route_paypal_ipn():
	host = socket.getfqdn(request.remote_addr)
	if host != 'notify.paypal.com':
		# POST not received from PayPal.
		return ''

	txn = request.args.get('txn_id', '')
	aid = request.args.get('custom', '')
	status = request.args.get('payment_status', '')
	currency = request.args.get('mc_currency', '')

	if currency != 'USD':
		# Payment not received in USD.
		return ''

	account = db.session().query(Account).filter(Account.id == aid).first()

	if not account:
		# Unknown account donated.
		# Perhaps refund the transaction?
		return ''

	raw_ipn = request.url[len(request.base_url) + 1:]
	verify = httplib.HTTPSConnection('www.sandbox.paypal.com')
	verify.request('GET', 'cgi-bin/webscr?cmd=_notify-validate&{}'.format(raw_ipn))

	if verify.getresponse().read() == 'VERIFIED':
		if status == 'Completed':
			# Add Points
			# Log transaction
			# Redirect to /paypal/donated
			print('ok')
		elif status == 'Reversed':
			# Delete account
			# Log transaction (blacklist?)
			# Redirect to /paypal/reversed
			print('boo')

	return ''
