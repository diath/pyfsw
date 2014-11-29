from flask import render_template, request

from pyfsw import app, db
from pyfsw import login_required, current_user
from pyfsw import Account, ZayPayHistory
from pyfsw import ZAYPAY_OPTIONS

import requests
from bs4 import BeautifulSoup
from time import time

def zaypay_show_payment(payment_id, option):
	request = requests.get('https://secure.zaypay.com///pay/{}/payments/{}/?key={}'.format(
		option.price_id, payment_id, option.price_key
	))

	if request.status_code != 200:
		return None

	data = BeautifulSoup(request.text)
	return data.response

@app.route('/zaypay/pay')
@login_required
def route_zaypay():
	return render_template(
		'zaypay/pay.htm',
		options = ZAYPAY_OPTIONS, account_id = current_user().id
	)

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
	option = ZAYPAY_OPTIONS.get(price_setting_id, None)
	if not option:
		error = True

	# Fetch the payment status
	data = zaypay_show_payment(payment_id, option)

	# Check the payment status
	if data.payment.status != 'paid':
		error = True

	# Check if the code was already used
	que = db.session().query(ZayPayHistory).filter(ZayPayHistory.payment_id == payment_id).first()
	if que:
		error = True

	# Fetch the account
	var = data.get('your-variables', '')
	var = var.split('&')
	var = var[0].split('=')[1]

	account = db.session().query(Account).filter(Account.id == int(var)).first()
	if not account:
		error = True

	# Add premium points and history entry
	# Unlike with PayPal, we don't actually log failed transactions for ZayPay
	if not error:
		account.points += option.points

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
