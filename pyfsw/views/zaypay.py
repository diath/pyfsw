from flask import render_template, request

from pyfsw import app, db
from pyfsw import login_required, current_user
from pyfsw import Account, ZayPayHistory
from pyfsw import ZAYPAY_OPTIONS

import requests
from bs4 import BeautifulSoup
from time import time
from urllib.parse import parse_qs
from collections import OrderedDict

def zaypay_show_payment(payment_id, option):
	request = requests.get('https://secure.zaypay.com///pay/{}/payments/{}/?key={}'.format(
		option.get('price_id', 0), payment_id, option.get('price_key', 0)
	), headers={'Accept': 'application/xml'})

	if request.status_code != 200:
		return None

	data = BeautifulSoup(request.text)
	if not data.response:
		return None

	return data.response

@app.route('/zaypay/pay')
@login_required
def route_zaypay():
	return render_template(
		'zaypay/pay.htm',
		options = ZAYPAY_OPTIONS, account_id = current_user().id
	)

@app.route('/zaypay/paid')
def route_zaypay_paid():
	return render_template('zaypay/paid.htm')

@app.route('/zaypay/ipn')
def route_zaypay_ipn():
	error = False

	# Get the payment ID param
	payment_id = request.args.get('payment_id', -1, type=int)
	if payment_id == -1:
		error = True

	# Get the price setting ID param
	price_setting_id = request.args.get('price_setting_id', -1, type=int)
	if price_setting_id == -1:
		error = True

	# Fetch the ZayPay option
	option = None

	for tmp in ZAYPAY_OPTIONS:
		if tmp.price_id == price_setting_id:
			option = tmp
			break

	# Fetch the payment status
	data = zaypay_show_payment(payment_id, option)
	if not data:
		# In case of a shitty payment, just send that it's been processed.
		return '*ok*', 200

	# Check the payment status
	try:
		if data.payment.findAll('status')[0].text != 'paid':
			error = True
	except Exception:
		error = True

	# Check if the code was already used
	exists = db.session().query(ZayPayHistory).filter(ZayPayHistory.payment_id == payment_id).first()
	if exists:
		error = True

	# Fetch the account
	try:
		var = parse_qs(data.payment.findAll('your-variables')[0].text)
		var = var.get('account_id')[0]
	except Exception:
		var = 0		

	account = db.session().query(Account).filter(Account.id == int(var)).first()
	if not account:
		error = True

	# Add premium points and history entry
	# Unlike with PayPal, we don't actually log failed transactions for ZayPay
	if not error:
		account.points += option.get('points', 0)

		history = ZayPayHistory()
		history.account_id = account.id
		history.timestamp = int(time())
		history.payment_id = payment_id
		history.price_setting_id = price_setting_id
		history.amount = data.get('total-amount', 0.0)
		history.points = option.get('points', 0)

		db.session().add(history)
		db.session().commit()

	return '*ok*', 200
