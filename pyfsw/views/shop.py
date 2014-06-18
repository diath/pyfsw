from flask import redirect, render_template, url_for

from pyfsw import app, db
from pyfsw import ShopCategory, ShopItem
from pyfsw import login_required, current_user

@app.route('/shop/offer')
def route_shop():
	categories = db.session.query(ShopCategory).all()
	return render_template('shop/browse.htm', categories=categories, logged=current_user())

@app.route('/shop/order/<int:id>', methods=['GET'])
@login_required
def route_shop_order(id):
	item = db.session.query(ShopItem).filter(ShopItem.id == id).first()
	characters = current_user().players
	return render_template('shop/order.htm', item=item, characters=characters)

@app.route('/shop/order/<int:id>', methods=['POST'])
@login_required
def route_shop_order_post(id):
	pass
