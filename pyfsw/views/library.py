from flask import redirect, render_template, url_for

from pyfsw import app, db
from pyfsw import Library

@app.route('/library/<string:uri>')
def route_library(uri):
	library = db.session().query(Library).filter(Library.uri == uri).first()
	if not library:
		return redirect(url_for('route_news'))

	return render_template('library/library.htm', library=library)
