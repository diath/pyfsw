import time

from datetime import datetime
from math import floor

from pyfsw import app
from pyfsw import DATE_FORMAT, GENDERS, VOCATIONS, TOWNS, STAFF_POSITIONS

@app.template_filter('datetime')
def filter_datetime(value):
	return datetime.fromtimestamp(int(value)).strftime(DATE_FORMAT)

@app.template_filter('worddate')
def filter_worddate(value):
	if value == 1:
		return 'day'
	elif value == 7:
		return 'week'
	elif value == 30:
		return 'month'

	return value

@app.template_filter('timetotal')
def filter_timetotal(value):
	return time.strftime('%H hours, %M minutes and %S seconds', time.gmtime(int(value)))

@app.template_filter('gender')
def filter_gender(value):
	return GENDERS.get(value, 'Unknown')

@app.template_filter('vocation')
def filter_vocation(value, group = -1):
	if group != -1 and value == 0:
		return STAFF_POSITIONS.get(group, 'Unknown')

	return VOCATIONS.get(value, 'Unknown')

@app.template_filter('staffrank')
def filter_staffpos(value):
	return STAFF_POSITIONS.get(value, 'Unknown')

@app.template_filter('town')
def filter_town(value):
	town = TOWNS.get(value, None)
	if not town:
		return 'Unknown'

	return town.get('name')

@app.template_filter('rank')
def filter_rank(value):
	if value == 3:
		return 'The Leader'
	elif value == 2:
		return 'Vice Leader'

	return 'Member'

@app.template_filter('price')
def filter_price(value):
	if value < 1000:
		return '{}{}'.format(value, 'gp')

	s = ''
	while value > 1000:
		value /= 1000
		s += 'k'

	return '{:.1f}{}'.format(value, s)

@app.template_filter('stamina')
def filter_stamina(value):
	stamina = value
	hours = 0
	minutes = 0

	while stamina >= 60:
		hours += 1
		stamina -= 60

	minutes = floor(stamina)
	if minutes == 0:
		minutes = '00'

	return '{} hours, {} minutes'.format(hours, minutes)

ITEM_TYPES = {
	1: 'Item',
	2: 'Container',
	3: 'Addon',
	4: 'Mount'
}

@app.template_filter('itemtype')
def filter_itemtype(value):
	return ITEM_TYPES.get(value, 'Unknown')
