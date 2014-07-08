from flask import redirect, render_template, url_for

from pyfsw import app, db
from pyfsw import Library

@app.route('/library/<string:uri>')
def route_library(uri):
	library = db.session().query(Library.uri, Library.name, Library.content)
	library = library.filter(Library.uri == uri).filter(Library.enabled == 1).first()

	if not library:
		return redirect(url_for('route_news'))

	return render_template('library/library.htm', library=library)
