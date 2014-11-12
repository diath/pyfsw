from flask import redirect, render_template, request, url_for, flash, session

from time import time

from pyfsw import app, db
from pyfsw import admin_required, current_user
from pyfsw import ForumCategory, ForumBoard

@app.route('/admin/forum/categories')
@admin_required
def route_admin_forum_categories():
	categories = ForumCategory.query.all()

	return render_template(
		'admin/forum/categories.htm',
		categories = categories
	)

@app.route('/admin/forum/category/add', methods=['POST'])
@admin_required
def route_admin_forum_category_add():
	name = request.form.get('name', '')

	if len(name) == 0:
		flash('You need to fill the name field', 'error')
	else:
		category = ForumCategory()
		category.name = name

		db.session().add(category)
		db.session().commit()

		flash('The category has been added.', 'success')

	return redirect(url_for('route_admin_forum_categories'))

@app.route('/admin/forum/category/edit/<int:id>')
@admin_required
def route_admin_forum_category_edit(id):
	category = ForumCategory.query.filter(ForumCategory.id == id).first()

	return render_template(
		'admin/forum/category_edit.htm',
		category = category
	)

@app.route('/admin/forum/category/edit/<int:id>', methods=['POST'])
@admin_required
def route_admin_forum_category_edit_post(id):
	category = ForumCategory.query.filter(ForumCategory.id == id).first()

	category.name = request.form.get('name', '')

	db.session().commit()
	flash('The category name has been changed.', 'success')

	return redirect(url_for('route_admin_forum_categories'))

@app.route('/admin/forum/category/delete/<int:id>')
@admin_required
def route_admin_forum_category_delete(id):
	category = ForumCategory.query.filter(ForumCategory.id == id).first()

	db.session().delete(category)
	db.session().commit()

	flash('The category has been deleted.', 'success')

	return redirect(url_for('route_admin_forum_categories'))

@app.route('/admin/forum/boards')
@admin_required
def route_admin_forum_boards():
	boards = ForumBoard.query.all()
	categories = ForumCategory.query.all()

	for board in boards:
		category = db.session().query(ForumCategory.name).filter(ForumCategory.id == board.category_id).first()
		if category:
			board.category = category.name
		else:
			board.category = 'Unknown'

	return render_template(
		'admin/forum/boards.htm',
		boards = boards, categories = categories
	)

@app.route('/admin/forum/board/add', methods=['POST'])
@admin_required
def route_admin_forum_board_add():
	name = request.form.get('name', '')
	description = request.form.get('description', '')
	category = request.form.get('category', 0)
	locked = request.form.get('locked', None)
	error = False

	if len(name) == 0:
		flash('Please fill the name field.', 'error')
		error = True

	if len(description) == 0:
		flash('Please fill the description field.', 'error')
		error = True

	if not error:
		board = ForumBoard()
		board.name = name
		board.description = description
		board.category_id = category
		board.locked = 0 if not locked else 1

		db.session().add(board)
		db.session().commit()

		flash('The board has beed added.', 'success')

	return redirect(url_for('route_admin_forum_boards'))

@app.route('/admin/forum/board/edit/<int:id>')
@admin_required
def route_admin_forum_board_edit(id):
	board = ForumBoard.query.filter(ForumBoard.id == id).first()
	categories = ForumCategory.query.all()

	return render_template(
		'admin/forum/board_edit.htm',
		board = board, categories = categories
	)

@app.route('/admin/forum/board/edit/<int:id>', methods=['POST'])
@admin_required
def route_admin_forum_board_edit_post(id):
	board = ForumBoard.query.filter(ForumBoard.id == id).first()

	board.name = request.form.get('name', '')
	board.description = request.form.get('description', '')
	board.category_id = request.form.get('category', 0)
	board.locked = 0 if not request.form.get('locked', None) else 1

	db.session().commit()
	flash('The board has been edited.', 'success')

	return redirect(url_for('route_admin_forum_boards'))

@app.route('/admin/forum/board/delete/<int:id>')
@admin_required
def route_admin_forum_board_delete(id):
	board = ForumBoard.query.filter(ForumBoard.id == id).first()

	db.session().delete(board)
	db.session().commit()

	flash('The board has been deleted.', 'success')

	return redirect(url_for('route_admin_forum_boards'))
