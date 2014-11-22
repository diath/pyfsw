from flask import redirect, render_template, request, url_for, flash, session

from pyfsw import app, db
from pyfsw import admin_required
from pyfsw import Library

@app.route('/admin/community/library')
@admin_required
def route_admin_library():
	pages = Library.query.all()

	return render_template(
		'admin/community/library.htm',
		pages = pages
	)

@app.route('/admin/community/library/add', methods=['POST'])
@admin_required
def route_admin_library_add():
	uri = request.form.get('uri', '')
	name = request.form.get('name', '')
	enabled = request.form.get('enabled', None)
	content = request.form.get('content', '')

	page = Library()
	page.uri = uri
	page.name = name
	page.enabled = 1 if enabled else 0
	page.content = content

	db.session().add(page)
	db.session().commit()

	flash('The page has been added.', 'success')

	return redirect(url_for('route_admin_library'))

@app.route('/admin/community/library/edit/<int:id>', methods=['GET'])
@admin_required
def route_admin_library_edit(id):
	page = Library.query.filter(Library.id == id).first()

	return render_template(
		'admin/community/library_edit.htm',
		page = page
	)

@app.route('/admin/community/library/edit/<int:id>', methods=['POST'])
@admin_required
def route_admin_library_edit_post(id):
	page = Library.query.filter(Library.id == id).first()
	page.uri = request.form.get('uri', '')
	page.name = request.form.get('name', '')
	page.enabled = 1 if request.form.get('enabled', None) else 0
	page.content = request.form.get('content', '')

	db.session().commit()
	flash('The page has been edited.', 'success')

	return redirect(url_for('route_admin_library'))

@app.route('/admin/community/library/delete/<int:id>', methods=['GET'])
@admin_required
def route_admin_library_delete(id):
	page = Library.query.filter(Library.id == id).first()

	db.session().delete(page)
	db.session().commit()

	flash('The library page has been deleted.', 'success')

	return redirect(url_for('route_admin_library'))
