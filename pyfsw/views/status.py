import socket
from bs4 import BeautifulSoup
from datetime import timedelta

from pyfsw import app, cache
from pyfsw import STATUS_HOST, STATUS_PORT, STATUS_TIMEOUT

@app.route('/status')
@cache.cached(STATUS_TIMEOUT)
def route_status():
	# Prepare the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(2.0)

	# Try to connect
	try:
		sock.connect((STATUS_HOST, STATUS_PORT))
	except Exception:
		return 'Status: Offline', 200

	# Send the status request sequence
	sock.sendall(b"\x06\x00\xff\xffinfo")

	# Parse the status (XML)
	data = BeautifulSoup(sock.recv(4096))

	# Calculate the uptime
	uptime = int(data.tsqp.serverinfo.get('uptime', 0))

	hour = uptime / 3600
	rem  = uptime % 3600
	min  = rem / 60

	uptime = '{}h {}m'.format(int(hour), int(min))

	# Close the socket and return formatted data
	sock.close()
	return 'Status: Online &bull; Players: {}/{} &bull; Record: {} &bull; Uptime: {}'.format(
		data.tsqp.players.get('online', 0), data.tsqp.players.get('max', 0),
		data.tsqp.players.get('peak', 0), uptime
	), 200
