from datetime import datetime

from pyfsw import app
from pyfsw import DATE_FORMAT, GENDERS, VOCATIONS, TOWNS

@app.template_filter('datetime')
def filter_datetime(value):
	return datetime.fromtimestamp(int(value)).strftime(DATE_FORMAT)

@app.template_filter('timetotal')
def filter_timetotal(value):
	value = int(value)

	hour = value / 3600
	rem = value % 3600
	minute = rem / 60
	second = rem % 60

	return '{:02d} hours, {:02d} minutes and {:02d} seconds'.format(int(hour), int(minute), int(second))

@app.template_filter('gender')
def filter_gender(value):
	return GENDERS.get(value, 'Unknown')

@app.template_filter('vocation')
def filter_vocation(value):
	return VOCATIONS.get(value, 'Unknown')

@app.template_filter('town')
def filter_town(value):
	return TOWNS.get(value, 'Unknown')

@app.template_filter('rank')
def filter_rank(value):
	if value == 3:
		return 'The Leader'
	elif value == 2:
		return 'Vice Leader'

	return 'Member'
