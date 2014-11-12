from flask import redirect, render_template, request, url_for, flash, session

from pyfsw import app, db
from pyfsw import admin_required

@app.route('/admin/dashboard')
@admin_required
def route_admin_dashboard():
	return render_template('admin/dashboard.htm')
