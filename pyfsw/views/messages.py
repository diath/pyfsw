from flask import render_template

from pyfsw import app

@app.route('/messages')
def route_messages():
	return render_template('messages.htm')
