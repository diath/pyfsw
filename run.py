from pyfsw import app, db
from pyfsw import NET_HOST, NET_PORT, DEBUG

if __name__ == '__main__':
	#db.create_all()
	app.run(host=NET_HOST, port=NET_PORT, debug=DEBUG)
