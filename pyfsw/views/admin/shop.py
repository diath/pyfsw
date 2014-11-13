from flask import redirect, render_template, request, url_for, flash, session

from pyfsw import app, db
from pyfsw import admin_required, current_user
from pyfsw import ShopCategory, ShopItem, ShopOrder

@app.route('/admin/shop/categories')
@admin_required
def route_admin_shop_categories():
	categories = ShopCategory.query.all()

	return render_template(
		'admin/shop/categories.htm',
		categories = categories
	)

@app.route('/admin/shop/category/add', methods=['POST'])
@admin_required
def route_admin_shop_category_add():
	name = request.form.get('name', '')
	enabled = request.form.get('enabled', None)

	if len(name) == 0:
		flash('Please fill the name field.', 'error')
	else:
		category = ShopCategory()
		category.name = name
		category.enabled = 1 if enabled else 0

		db.session().add(category)
		db.session().commit()

		flash('The category has been added.', 'success')

	return redirect(url_for('route_admin_shop_categories'))

@app.route('/admin/shop/category/edit/<int:id>')
@admin_required
def route_admin_shop_category_edit(id):
	category = ShopCategory.query.filter(ShopCategory.id == id).first()

	return render_template(
		'admin/shop/category_edit.htm',
		category = category
	)

@app.route('/admin/shop/category/edit/<int:id>', methods=['POST'])
@admin_required
def route_admin_shop_category_edit_post(id):
	category = ShopCategory.query.filter(ShopCategory.id == id).first()
	category.name = request.form.get('name', '')
	category.enabled = 1 if request.form.get('enabled', None) else 0

	db.session().commit()
	flash('The category has been edited.', 'success')

	return redirect(url_for('route_admin_shop_categories'))

@app.route('/admin/shop/category/delete/<int:id>')
@admin_required
def route_admin_shop_category_delete(id):
	category = ShopCategory.query.filter(ShopCategory.id == id).first()

	db.session().delete(category)
	db.session().commit()

	flash('The category has been deleted.', 'success')

	return redirect(url_for('route_admin_shop_categories'))

@app.route('/admin/shop/items')
@admin_required
def route_admin_shop_items():
	items = ShopItem.query.all()
	categories = ShopCategory.query.all()

	return render_template(
		'admin/shop/items.htm',
		items = items, categories = categories
	)

@app.route('/admin/shop/item/add', methods=['POST'])
@admin_required
def route_admin_shop_item_add():
	name = request.form.get('name', '')
	description = request.form.get('description', '')
	category = request.form.get('category', 0)
	type = request.form.get('type', 0)
	key = request.form.get('key', 0)
	value = request.form.get('value', 0)
	price = request.form.get('price', 0)
	image = request.form.get('image', '')
	enabled = request.form.get('enabled', None)
	error = False

	# TODO: Add verifications

	if not error:
		item = ShopItem()
		item.name = name
		item.description = description
		item.category_id = category
		item.type = type
		item.key = key
		item.value = value
		item.price = price
		item.custom_image = image
		item.enabled = 1 if enabled else 0

		db.session().add(item)
		db.session().commit()

		flash('The item has been added.', 'success')

	return redirect(url_for('route_admin_shop_items'))

@app.route('/admin/shop/item/edit/<int:id>')
@admin_required
def route_admin_shop_item_edit(id):
	item = ShopItem.query.filter(ShopItem.id == id).first()
	categories = ShopCategory.query.all()

	return render_template(
		'admin/shop/item_edit.htm',
		item = item, categories = categories
	)

@app.route('/admin/shop/item/edit/<int:id>', methods=['POST'])
@admin_required
def route_admin_shop_item_edit_post(id):
	item = ShopItem.query.filter(ShopItem.id == id).first()

	# TODO: Add verification

	item.name = request.form.get('name', '')
	item.description = request.form.get('description', '')
	item.category = request.form.get('category', 0)
	item.type = request.form.get('type', 0)
	item.key = request.form.get('key', 0)
	item.value = request.form.get('value', 0)
	item.price = request.form.get('price', 0)
	item.image = request.form.get('image', '')
	item.enabled = 1 if request.form.get('enabled', None) else 0

	db.session().commit()
	flash('The item has been edited.', 'success')

	return redirect(url_for('route_admin_shop_items'))

@app.route('/admin/shop/item/delete/<int:id>')
@admin_required
def route_admin_shop_item_delete(id):
	item = ShopItem.query.filter(ShopItem.id == id).first()

	db.session().delete(item)
	db.session().commit()

	flash('The item has been deleted.', 'success')

	return redirect(url_for('route_admin_shop_items'))
