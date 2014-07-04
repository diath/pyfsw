from flask import render_template

from pyfsw import app

@app.errorhandler(403)
def error_forbidden(error):
	return render_template('error.htm', error=403,
		message='Access to the resource you are trying to reach is forbidden.'), 403

@app.errorhandler(404)
def error_not_found(error):
	return render_template('error.htm', error=404,
		message='The page you are trying to reach has not been found.'), 404

@app.errorhandler(500)
def error_internal(error):
	return render_template('error.htm', error=500,
		message='Internal server error, please contact the administrator.'), 500
