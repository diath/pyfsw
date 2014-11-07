from flask import redirect, render_template, request, url_for, flash, session

from pyfsw import app, db

@app.route('/admin/dashboard')
def route_admin_dashboard():
	return render_template('admin/dashboard.htm')
